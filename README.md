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

Quotify is an emotion-aware quote recommendation prototype that combines emotion classification, semantic retrieval, and ranking logic to recommend quotes from a user's natural-language reflection. The current version preserves the original coursework baseline while adding modern dense retrieval strategies and Docker-based deployment on Hugging Face Spaces.

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Hugging%20Face-blue)](https://huggingface.co/spaces/TsukishimaAlan20/Quotify-advance)
![Docker](https://img.shields.io/badge/SDK-Docker-2496ED)
![Python](https://img.shields.io/badge/Python-3.11-3776AB)
![React](https://img.shields.io/badge/React-18-61DAFB)
[![License](https://img.shields.io/badge/License-See%20LICENSE-lightgrey)](LICENSE)

**Live Demo:** https://huggingface.co/spaces/TsukishimaAlan20/Quotify-advance

## Project Overview

A user writes a sentence about how they feel. Quotify detects the emotional context, retrieves quote candidates, ranks them with semantic similarity and emotion-aware scoring, then returns a quote with its author, detected emotion, quote emotion, selected strategy, and ranking metadata.

The app is designed as an applied NLP prototype: the recommendation result is explainable enough to inspect through scores, while the frontend keeps the interaction simple through strategy switching and compare-all mode.

## What Makes This Project Interesting

- Emotion-aware recommendation: the system is not just searching for matching words; it uses detected emotion as part of ranking.
- Multiple retrieval strategies: users can compare a classical TF-IDF baseline, dense semantic retrieval, and an optional reranker.
- Preserved baseline: the original fine-tuned BERT + TF-IDF coursework method remains available as `legacy_tfidf_bert`.
- Modern NLP upgrade: SentenceTransformer embeddings provide meaning-based quote retrieval with a CPU-friendly model.
- Deployed full-stack ML app: React, Flask, Docker, and Hugging Face Spaces are integrated into one deployed prototype.
- Research-to-product transition: legacy notebooks and the official report are preserved while the application layer has been modularized.

## Live Deployment

| Item | Value |
| --- | --- |
| Platform | Hugging Face Spaces |
| Live URL | https://huggingface.co/spaces/TsukishimaAlan20/Quotify-advance |
| Direct app/API URL | https://tsukishimaalan20-quotify-advance.hf.space |
| SDK | Docker |
| App port | `7860` |
| Free deployment mode | CPU Basic, Docker Space |
| Lightweight setting | `QUOTIFY_ENABLE_CROSS_ENCODER=false` |

The deployed demo uses the Docker Space configuration and keeps Cross-Encoder reranking disabled by default for CPU and memory safety. The AI Reranker remains documented and available as an advanced optional mode when runtime resources allow it.

## Recommendation Strategies

| Strategy | ID | Core Method | Strength | Runtime Notes |
| --- | --- | --- | --- | --- |
| Legacy BERT + TF-IDF | `legacy_tfidf_bert` | Fine-tuned BERT emotion classification when the checkpoint is available, TF-IDF cosine similarity, emotion-alignment boost | Preserves the original project behavior and provides a transparent baseline | Uses lightweight retrieval; BERT checkpoint is optional with fallback behavior |
| Dense Semantic Search | `sbert_dense` | SentenceTransformer embeddings using `sentence-transformers/all-MiniLM-L6-v2`, cosine similarity, emotion-aware final score | Better meaning-based retrieval than lexical matching | Recommended default for the deployed demo; CPU-friendly after model load/artifact generation |
| AI Reranker | `cross_encoder_rerank` | Dense retrieval for top candidates, optional Cross-Encoder reranking, emotion-aware final score | More expressive candidate reranking | Advanced optional mode; can be slower and is disabled by default on free CPU deployment |

## System Architecture

```text
React Frontend
  ├── User input
  ├── Strategy selector
  ├── Quote result card
  └── Compare-all mode

Flask API
  ├── GET /health
  ├── GET /strategies
  ├── POST /get_quote
  └── POST /compare

Recommendation Layer
  ├── Legacy BERT + TF-IDF
  ├── Dense Semantic Search
  └── Optional Cross-Encoder Reranker

Data and Model Assets
  ├── Preprocessed emotion dataset
  ├── Preprocessed quote corpus
  ├── Optional fine-tuned BERT checkpoint
  └── Generated dense embedding artifacts
```

## Machine Learning Workflow

The original research workflow starts with an emotion dataset labeled across three classes: `anger`, `fear`, and `joy`. The quote corpus is cleaned, deduplicated, and labeled with predicted emotions so recommendation can combine text similarity with emotion alignment.

The legacy notebooks compare Naive Bayes, Logistic Regression, and fine-tuned BERT for emotion classification. BERT was selected as the strongest original emotion model and became the basis for the initial application method.

| Model | Accuracy | Weighted F1 |
| --- | ---: | ---: |
| Naive Bayes | 0.8812 | 0.8813 |
| Logistic Regression | 0.9191 | 0.9192 |
| Fine-tuned BERT | 0.9562 | 0.9563 |

The upgraded recommendation layer keeps that baseline intact and adds dense semantic retrieval. In all strategies, quote ranking is influenced by both semantic relevance and whether the quote's predicted emotion matches the user's detected emotion.

## Tech Stack

**Backend**
- Python
- Flask
- Flask-CORS
- gunicorn
- PyTorch
- Hugging Face Transformers
- SentenceTransformers
- scikit-learn
- pandas
- NumPy

**Frontend**
- React 18
- Create React App
- CSS
- React Icons

**Deployment**
- Docker
- Hugging Face Spaces
- GitHub Actions sync

## Repository Structure

```text
.
├── .github/
│   └── workflows/
│       └── sync-to-huggingface.yml
├── backend/
│   ├── app.py
│   ├── requirements.txt
│   ├── runtime.txt
│   ├── artifacts/
│   ├── scripts/
│   ├── src/
│   └── tests/
├── frontend/
│   ├── package.json
│   ├── public/
│   └── src/
├── LEGACY/
│   ├── Machine Learning-AOL.pdf
│   ├── EDAandPreprocess.ipynb
│   ├── NaiveBayes_ML_AOL_3_0.ipynb
│   ├── LogisticRegression_ML_AOL_2_0.ipynb
│   ├── BERT_ML_AOL_5_0.ipynb
│   └── QuotesSelector.ipynb
├── Dockerfile
├── docker-compose.yml
├── Makefile
├── LICENSE
└── README.md
```

## Local Development

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Backend URL:

```text
http://127.0.0.1:7860
```

For a lighter local run:

```bash
QUOTIFY_ENABLE_SBERT=false QUOTIFY_ENABLE_CROSS_ENCODER=false python app.py
```

### Frontend

```bash
cd frontend
npm install
npm start
```

Frontend URL:

```text
http://localhost:3000
```

The React development server proxies API calls to the Flask backend through `frontend/package.json`.

### Docker

```bash
make docker-build
make docker-run
```

Alternative:

```bash
docker compose up --build
```

Docker serves the React build and Flask API from one container on port `7860`.

## Environment Variables

| Variable | Default | Purpose |
| --- | --- | --- |
| `PORT` | `7860` | Flask/gunicorn port |
| `QUOTIFY_DEFAULT_STRATEGY` | `sbert_dense` | Default recommendation method |
| `QUOTIFY_ENABLE_SBERT` | `true` | Enables SentenceTransformer dense retrieval |
| `QUOTIFY_ENABLE_CROSS_ENCODER` | `true` locally, `false` in Docker | Enables optional Cross-Encoder reranking |
| `QUOTIFY_EMOTION_BOOST` | `0.08` | Score boost for emotion-aligned quotes |
| `QUOTIFY_TOP_K_RETRIEVE` | `50` | Candidate count for reranker retrieval |
| `QUOTIFY_MODEL_CHECKPOINT_PATH` | `last_trained_model_checkpoint.pth` | Optional fine-tuned BERT checkpoint path |

Recommended values for the free Hugging Face Spaces deployment:

```text
QUOTIFY_DEFAULT_STRATEGY=sbert_dense
QUOTIFY_ENABLE_CROSS_ENCODER=false
```

## API Reference

### `GET /health`

Returns service status, app metadata, available strategies, artifact status, and model availability.

```bash
curl https://tsukishimaalan20-quotify-advance.hf.space/health
```

### `GET /strategies`

Returns the selectable recommendation strategies and availability flags.

```bash
curl http://127.0.0.1:7860/strategies
```

### `POST /get_quote`

Request:

```bash
curl -X POST http://127.0.0.1:7860/get_quote \
  -H "Content-Type: application/json" \
  -d '{"inputText":"I feel nervous about tomorrow","strategy":"sbert_dense","topK":5}'
```

Response shape:

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

### `POST /compare`

Runs all available strategies for one input and returns side-by-side results.

```bash
curl -X POST http://127.0.0.1:7860/compare \
  -H "Content-Type: application/json" \
  -d '{"inputText":"I feel nervous about tomorrow","topK":5}'
```

Response shape:

```json
{
  "inputText": "I feel nervous about tomorrow",
  "results": [
    {
      "strategy": "legacy_tfidf_bert",
      "strategy_label": "Legacy BERT + TF-IDF",
      "quote": "Returned quote text",
      "author": "Quote author",
      "scores": {
        "semantic_score": 0.42,
        "cross_encoder_score": null,
        "emotion_boost": 0.08,
        "final_score": 0.5
      }
    }
  ],
  "errors": []
}
```

## Deployment

This repository deploys to Hugging Face Spaces using Docker.

- The README metadata block configures the Space.
- The root `Dockerfile` builds the React frontend and serves it through Flask/gunicorn.
- The app listens on port `7860`.
- `.github/workflows/sync-to-huggingface.yml` syncs GitHub updates to the Hugging Face Space.
- Live Space: https://huggingface.co/spaces/TsukishimaAlan20/Quotify-advance
- Direct app/API base: https://tsukishimaalan20-quotify-advance.hf.space

No-cost deployment guidance:

- Use CPU Basic.
- Keep `QUOTIFY_ENABLE_CROSS_ENCODER=false` by default.
- Do not commit large model checkpoints or generated embedding artifacts.
- The app does not require paid APIs, OpenAI keys, or external paid services.

## Model Checkpoint and Artifacts

The fine-tuned BERT checkpoint is optional and is not committed to the repository. If available, place it at:

```text
backend/last_trained_model_checkpoint.pth
```

If the checkpoint is missing, the backend does not crash. It reports the missing checkpoint through `/health` and uses fallback emotion detection for demo resilience.

SBERT embedding artifacts are generated under:

```text
backend/artifacts/
```

To rebuild them manually:

```bash
make build-index
```

Generated embeddings and large model files are ignored by Git when configured through `.gitignore`.

## Legacy Project Reference

The original coursework notebooks and report are preserved under `LEGACY/`. The official report is:

```text
LEGACY/Machine Learning-AOL.pdf
```

These files document the original EDA, preprocessing, baseline experiments, BERT training workflow, and quote selection prototype.

## Limitations

- Emotion classes are limited to `anger`, `fear`, and `joy`.
- Quote emotion labels are generated by the project model and may contain prediction errors.
- Recommendations are intended for reflection and inspiration, not clinical guidance.
- Cross-Encoder reranking can be slower on CPU and is disabled by default in the free deployment setup.
- Fallback emotion detection is for resilience/demo mode only and is not equivalent to the fine-tuned BERT model.

## Ethical Note

Quotify is for quote recommendation, reflection, and inspiration. It is not a mental health diagnosis tool, therapy system, crisis intervention service, or substitute for professional support.

## License

See [`LICENSE`](LICENSE).
