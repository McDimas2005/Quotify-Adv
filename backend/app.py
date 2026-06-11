from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from src.config import AppConfig, config
from src.data_loader import load_data
from src.emotion_classifier import EmotionClassifier
from src.health import artifact_status
from src.recommenders import CrossEncoderRerankRecommender, LegacyTfidfRecommender, SbertDenseRecommender


def create_app(app_config: AppConfig = config, quotes_override=None) -> Flask:
    static_folder = str(app_config.frontend_build_dir) if app_config.frontend_build_dir.exists() else None
    app = Flask(__name__, static_folder=static_folder, static_url_path="")

    if app_config.cors_origins:
        CORS(app, origins=[origin.strip() for origin in app_config.cors_origins.split(",") if origin.strip()])
    else:
        CORS(app, origins=["http://localhost:3000", "http://127.0.0.1:3000"])

    loaded_data = load_data(app_config, quotes_override=quotes_override)
    emotion_classifier = EmotionClassifier(app_config, loaded_data.emotion_data["Emotion"].unique())
    legacy = LegacyTfidfRecommender(app_config, loaded_data.quotes, emotion_classifier)
    dense = SbertDenseRecommender(app_config, loaded_data.quotes, emotion_classifier)
    reranker = CrossEncoderRerankRecommender(app_config, loaded_data.quotes, emotion_classifier, dense)
    recommenders = {
        legacy.strategy_id: legacy,
        dense.strategy_id: dense,
        reranker.strategy_id: reranker,
    }

    app.extensions["quotify"] = {
        "config": app_config,
        "data": loaded_data,
        "emotion_classifier": emotion_classifier,
        "recommenders": recommenders,
    }

    def _available_recommenders():
        return {key: value for key, value in recommenders.items() if value.available}

    def _resolve_strategy(strategy_id):
        requested = strategy_id or app_config.default_strategy
        if requested in recommenders and recommenders[requested].available:
            return recommenders[requested]
        available = _available_recommenders()
        if available:
            return next(iter(available.values()))
        raise RuntimeError("No recommendation strategies are available.")

    @app.get("/health")
    def health():
        available = _available_recommenders()
        return jsonify(
            {
                "status": "ok" if available else "degraded",
                "app": app_config.app_name,
                "version": app_config.version,
                "available_strategies": list(available.keys()),
                "strategies": [strategy.info().to_dict() for strategy in recommenders.values()],
                "artifacts": artifact_status(app_config, dense),
                "models": {
                    "emotion_classifier": emotion_classifier.status.to_dict(),
                    "sentence_transformer": {
                        "available": dense.available,
                        "model": app_config.sbert_model_name,
                        "reason": dense.unavailable_reason or None,
                    },
                    "cross_encoder": {
                        "available": reranker.available,
                        "enabled": app_config.enable_cross_encoder,
                        "model": app_config.cross_encoder_model_name,
                        "reason": reranker.unavailable_reason or None,
                    },
                },
            }
        )

    @app.get("/strategies")
    def strategies():
        return jsonify([strategy.info().to_dict() for strategy in recommenders.values()])

    @app.post("/get_quote")
    def get_quote():
        payload = request.get_json(silent=True) or {}
        input_text = str(payload.get("inputText", "")).strip()
        if not input_text:
            return jsonify({"error": "inputText is required."}), 400

        top_k = int(payload.get("topK") or 5)
        strategy = _resolve_strategy(payload.get("strategy"))
        try:
            return jsonify(strategy.recommend(input_text, top_k=top_k).to_dict())
        except Exception as exc:
            return jsonify({"error": str(exc), "strategy": strategy.strategy_id}), 503

    @app.post("/compare")
    def compare():
        payload = request.get_json(silent=True) or {}
        input_text = str(payload.get("inputText", "")).strip()
        if not input_text:
            return jsonify({"error": "inputText is required."}), 400

        top_k = int(payload.get("topK") or 5)
        results = []
        errors = []
        for strategy in recommenders.values():
            if not strategy.available:
                errors.append({"strategy": strategy.strategy_id, "error": strategy.unavailable_reason})
                continue
            try:
                results.append(strategy.recommend(input_text, top_k=top_k).to_dict())
            except Exception as exc:
                errors.append({"strategy": strategy.strategy_id, "error": str(exc)})
        return jsonify({"inputText": input_text, "results": results, "errors": errors})

    @app.get("/")
    def index():
        if app.static_folder:
            return send_from_directory(app.static_folder, "index.html")
        return jsonify({"app": app_config.app_name, "message": "Frontend build is not available."})

    @app.get("/<path:path>")
    def static_proxy(path):
        if app.static_folder:
            candidate = Path(app.static_folder) / path
            if candidate.exists():
                return send_from_directory(app.static_folder, path)
            return send_from_directory(app.static_folder, "index.html")
        return jsonify({"error": "Not found"}), 404

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=config.port, debug=False)
