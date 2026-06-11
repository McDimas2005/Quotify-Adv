---
title: Quotify
emoji: 💬
colorFrom: green
colorTo: blue
sdk: docker
app_port: 7860
pinned: false
---

# Quotify

Quotify is an emotion-aware quote recommendation prototype. A user writes how they feel, the backend detects the likely emotion, and the app recommends quotes using one of three selectable NLP retrieval strategies.

The original coursework method is preserved as the baseline, and the upgraded version adds modern dense retrieval plus an optional retrieve-and-rerank pipeline suitable for an AI/NLP portfolio demo.

## What Changed

- Refactored the Flask backend into modular strategy classes.
- Added `/health`, `/strategies`, `/get_quote`, and `/compare`.
- Preserved the legacy BERT + TF-IDF method as a selectable baseline.
- Added SentenceTransformer dense semantic search.
- Added optional Bi-Encoder retrieval + Cross-Encoder reranking.
- Added model/artifact fallback behavior so missing checkpoints do not crash the app.
- Updated the React UI with strategy switching, compare mode, score cards, loading states, and error states.
- Added Docker deployment for Hugging Face Spaces on port `7860`.

## Recommendation Strategies

| Strategy ID | UI Label | Method | Best Use |
| --- | --- | --- | --- |
| `legacy_tfidf_bert` | Legacy BERT + TF-IDF | Fine-tuned BERT emotion classifier, TF-IDF cosine similarity, emotion boost | Preserves the original project method |
| `sbert_dense` | Dense Semantic Search | `sentence-transformers/all-MiniLM-L6-v2` quote embeddings, cosine similarity, emotion boost | Better meaning-based retrieval on CPU |
| `cross_encoder_rerank` | AI Reranker | Dense retrieval top K, `cross-encoder/ms-marco-MiniLM-L6-v2` reranking, emotion-aware final score | Higher quality reranking when CPU/memory allows |

## Architecture

```text
React UI
  |-- strategy selector
  |-- quote result cards
  `-- compare-all mode
        |
        v
Flask API
  |-- GET /health
  |-- GET /strategies
  |-- POST /get_quote
  `-- POST /compare
        |
        v
Recommendation registry
  |-- legacy_tfidf_bert
  |-- sbert_dense
  `-- cross_encoder_rerank
        |
        v
Data and models
  |-- fine-tuned BERT checkpoint, optional
  |-- preprocessed emotion dataset
  |-- preprocessed quote dataset
  `-- generated SBERT artifacts under backend/artifacts/
```

## Tech Stack

- Backend: Flask, gunicorn, PyTorch, Transformers, SentenceTransformers, scikit-learn, pandas, NumPy
- Frontend: React 18, Create React App, CSS, React Icons
- Deployment: Docker, Hugging Face Spaces
- Research assets: Jupyter notebooks and official PDF report in `LEGACY/`

## Local Setup

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

The backend runs on:

```text
http://127.0.0.1:7860
```

For a lighter local run that avoids loading dense models:

```bash
QUOTIFY_ENABLE_SBERT=false QUOTIFY_ENABLE_CROSS_ENCODER=false python app.py
```

### Frontend

```bash
cd frontend
npm install
npm start
```

The frontend runs on:

```text
http://localhost:3000
```

Create React App proxies API calls to the backend through `frontend/package.json`.

## Model Checkpoint

The original fine-tuned BERT checkpoint is intentionally not committed. Download it from:

```text
https://drive.google.com/file/d/1UCsaBpSQEWzD8kkK2Etcdw5r63pmj2yO/view?usp=drive_web
```

Place it at:

```text
backend/last_trained_model_checkpoint.pth
```

If the checkpoint is missing, Quotify still starts and uses a clearly marked lightweight keyword fallback for emotion detection. `/health` reports whether the real checkpoint is loaded.

## Artifact Generation

The dense semantic strategy builds quote embeddings on first startup when `sentence-transformers` is available. To build them manually:

```bash
make build-index
```

Generated files are written to `backend/artifacts/`:

```text
quote_embeddings.npy
quote_metadata.csv
artifact_manifest.json
```

These artifacts can be large, so they are ignored by Git by default.

## Docker

Build and run locally:

```bash
make docker-build
make docker-run
```

Or:

```bash
docker compose up --build
```

The container serves the React build and Flask API from one process on:

```text
http://localhost:7860
```

## Hugging Face Spaces Deployment

1. Create a new Hugging Face Space.
2. Choose Docker as the SDK.
3. Push this repository to the Space.
4. Keep the default app port as `7860`.
5. Optional: add repository secrets or Space variables:
   - `QUOTIFY_DEFAULT_STRATEGY=sbert_dense`
   - `QUOTIFY_ENABLE_CROSS_ENCODER=false`
   - `QUOTIFY_EMOTION_BOOST=0.08`
   - `QUOTIFY_TOP_K_RETRIEVE=50`
   - `QUOTIFY_MODEL_CHECKPOINT_PATH=last_trained_model_checkpoint.pth`
6. If you do not include the BERT checkpoint, the app still runs with fallback emotion detection.

For free CPU Spaces, keep `QUOTIFY_ENABLE_CROSS_ENCODER=false` unless startup time and memory are acceptable.

## API Examples

### Health

```bash
curl http://127.0.0.1:7860/health
```

### Strategies

```bash
curl http://127.0.0.1:7860/strategies
```

### Get One Quote

```bash
curl -X POST http://127.0.0.1:7860/get_quote \
  -H "Content-Type: application/json" \
  -d '{"inputText":"I feel nervous about tomorrow","strategy":"sbert_dense","topK":5}'
```

Example response:

```json
{
  "quote": "Returned quote text",
  "author": "Quote author",
  "emotion": "fear",
  "quote_emotion": "fear",
  "strategy": "sbert_dense",
  "strategy_label": "Dense Semantic Search",
  "scores": {
    "semantic_score": 0.721,
    "cross_encoder_score": null,
    "emotion_boost": 0.08,
    "final_score": 0.801
  },
  "alternatives": []
}
```

### Compare Methods

```bash
curl -X POST http://127.0.0.1:7860/compare \
  -H "Content-Type: application/json" \
  -d '{"inputText":"I feel nervous about tomorrow","topK":5}'
```

## Developer Commands

```bash
make dev-backend
make dev-frontend
make test
make build-index
make validate-models
make docker-build
make docker-run
```

## Environment Variables

| Variable | Default | Purpose |
| --- | --- | --- |
| `PORT` | `7860` | Flask/gunicorn port |
| `QUOTIFY_DEFAULT_STRATEGY` | `sbert_dense` | Preferred recommendation strategy |
| `QUOTIFY_ENABLE_SBERT` | `true` | Enable dense retrieval loading |
| `QUOTIFY_ENABLE_CROSS_ENCODER` | `true` locally, `false` in Docker | Enable optional reranker |
| `QUOTIFY_EMOTION_BOOST` | `0.08` | Score boost for emotion-aligned quotes |
| `QUOTIFY_TOP_K_RETRIEVE` | `50` | Dense candidates passed to reranker |
| `QUOTIFY_MODEL_CHECKPOINT_PATH` | `last_trained_model_checkpoint.pth` | Fine-tuned BERT checkpoint path |

## Limitations

- Emotion detection is limited to `anger`, `fear`, and `joy`.
- The quote emotion labels are generated by the project model, so they may contain prediction errors.
- Dense retrieval may need to download open-source model files from Hugging Face on first run.
- Cross-Encoder reranking is slower and may be disabled on constrained CPU deployments.
- The fallback emotion classifier is only for local/demo resilience, not a replacement for the fine-tuned model.

## Ethical Note

Quotify recommends quotes for reflection and inspiration. It is not a mental health diagnosis tool, therapy tool, crisis intervention system, or substitute for professional support.

## Legacy Project Reference

The official report and original research notebooks remain under `LEGACY/`:

```text
LEGACY/Machine Learning-AOL.pdf
LEGACY/EDAandPreprocess.ipynb
LEGACY/NaiveBayes_ML_AOL_3_0.ipynb
LEGACY/LogisticRegression_ML_AOL_2_0.ipynb
LEGACY/BERT_ML_AOL_5_0.ipynb
LEGACY/QuotesSelector.ipynb
```

## License

See [`LICENSE`](LICENSE).
