import os
from dataclasses import replace

import pandas as pd
import pytest

os.environ["QUOTIFY_ENABLE_SBERT"] = "false"
os.environ["QUOTIFY_ENABLE_CROSS_ENCODER"] = "false"

from app import create_app
from src.config import config


@pytest.fixture()
def client():
    quotes = pd.DataFrame(
        [
            {
                "Quote": "Courage is resistance to fear, mastery of fear, not absence of fear.",
                "Author": "Mark Twain",
                "emotion": "fear",
            },
            {
                "Quote": "For every minute you are angry you lose sixty seconds of happiness.",
                "Author": "Ralph Waldo Emerson",
                "emotion": "anger",
            },
            {
                "Quote": "Joy is the simplest form of gratitude.",
                "Author": "Karl Barth",
                "emotion": "joy",
            },
        ]
    )
    test_config = replace(
        config,
        enable_sbert=False,
        enable_cross_encoder=False,
        default_strategy="legacy_tfidf_bert",
    )
    app = create_app(test_config, quotes_override=quotes)
    app.config.update(TESTING=True)
    return app.test_client()


def test_health_returns_200(client):
    response = client.get("/health")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["app"] == "Quotify"
    assert "legacy_tfidf_bert" in payload["available_strategies"]
    assert payload["models"]["emotion_classifier"]["available"] is True


def test_strategies_returns_all_strategy_ids(client):
    response = client.get("/strategies")
    assert response.status_code == 200
    ids = {item["id"] for item in response.get_json()}
    assert ids == {"legacy_tfidf_bert", "sbert_dense", "cross_encoder_rerank"}


def test_get_quote_validates_missing_input(client):
    response = client.post("/get_quote", json={})
    assert response.status_code == 400
    assert response.get_json()["error"] == "inputText is required."


def test_each_available_strategy_returns_valid_quote(client):
    strategies = client.get("/strategies").get_json()
    for strategy in strategies:
        if not strategy["available"]:
            continue
        response = client.post(
            "/get_quote",
            json={"inputText": "I am nervous about tomorrow", "strategy": strategy["id"], "topK": 2},
        )
        assert response.status_code == 200
        payload = response.get_json()
        assert payload["quote"]
        assert payload["author"]
        assert payload["strategy"] == strategy["id"]
        assert "final_score" in payload["scores"]


def test_compare_returns_available_strategy_results(client):
    response = client.post("/compare", json={"inputText": "I am happy today", "topK": 2})
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["results"]
    assert payload["results"][0]["strategy"] == "legacy_tfidf_bert"
    assert isinstance(payload["errors"], list)


def test_missing_checkpoint_does_not_crash_backend(client):
    response = client.get("/health")
    assert response.status_code == 200
    classifier = response.get_json()["models"]["emotion_classifier"]
    assert classifier["available"] is True
    assert classifier["checkpoint_loaded"] is False
    assert classifier["fallback"] is True

