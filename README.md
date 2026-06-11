# Quotify

Quotify is an emotion-aware quote recommendation web application. Users describe how they feel in natural language, and the system detects the dominant emotion in the text, searches a curated quote corpus, and returns a relevant quote with its author.

The project was developed as a machine learning application that connects NLP-based emotion classification with a recommendation layer. The official project report is available at [`LEGACY/Machine Learning-AOL.pdf`](LEGACY/Machine%20Learning-AOL.pdf).

## Project Essence

Quotify addresses a simple but meaningful interaction: people often want words that match their current emotional state, but ordinary quote collections rely on manual browsing or keyword search. This application turns that process into a short conversational input.

The system focuses on three emotion classes:

- `anger`
- `fear`
- `joy`

From that input, Quotify combines:

- a fine-tuned BERT classifier for emotion detection
- a preprocessed quote dataset labeled with predicted emotions
- TF-IDF vectorization and cosine similarity for content relevance
- emotion-weighted ranking so the selected quote is semantically similar and emotionally aligned

## How It Works

1. The user enters a short sentence in the React interface.
2. The frontend sends the text to the Flask backend through `POST /get_quote`.
3. The backend tokenizes the text with `bert-base-uncased`.
4. A fine-tuned `BertForSequenceClassification` model predicts the user's emotion.
5. The backend compares the input against the preprocessed quote corpus using TF-IDF and cosine similarity.
6. Quotes with the detected emotion receive a small ranking boost.
7. One quote is selected from the top candidates and returned with:
   - quote text
   - author
   - detected user emotion
   - selected quote emotion

## Machine Learning Pipeline

The research workflow is preserved in the `LEGACY/` notebooks and official report.

### Data

- Emotion dataset: 5,934 cleaned text samples after duplicate removal
- Emotion labels: anger, fear, joy
- Quote dataset: 48,391 raw quote records
- Processed quote corpus: 36,937 unique quotes with author and predicted emotion labels

### Model Experiments

The project compares several approaches before selecting BERT for the application:

| Model | Accuracy | Weighted F1 |
| --- | ---: | ---: |
| Naive Bayes | 0.8812 | 0.8813 |
| Logistic Regression | 0.9191 | 0.9192 |
| Fine-tuned BERT | 0.9562 | 0.9563 |

BERT was selected because it produced the strongest evaluation result and better captures contextual meaning than the baseline bag-of-words models.

## Innovation

Quotify is not only an emotion classifier and not only a quote search tool. Its main contribution is the integration of both:

- Emotion-first recommendation: user mood becomes a ranking signal, not just a displayed prediction.
- Hybrid relevance: quote selection balances text similarity with emotion alignment.
- End-to-end deployment: the trained NLP model is exposed through a Flask API and consumed by a React user interface.
- Research-to-product flow: the repository keeps the exploratory notebooks, preprocessing flow, model comparison, trained-model loading path, backend API, and frontend implementation together.

## Tech Stack

### Machine Learning and Backend

- Python
- Flask
- Flask-CORS
- PyTorch
- Hugging Face Transformers
- scikit-learn
- pandas
- NumPy

### Frontend

- React 18
- Create React App
- React Router
- React Icons
- Tailwind CSS tooling
- CSS modules/files for component styling

### Research Assets

- Jupyter notebooks
- CSV datasets
- Official PDF report

## Repository Structure

```text
.
|-- backend/
|   |-- app.py
|   |-- (Preprocessed)Emotion_classify_Data(Labeled).csv
|   `-- (Preprocessed)quotes.csv
|-- frontend/
|   |-- package.json
|   |-- public/
|   `-- src/
|-- LEGACY/
|   |-- Machine Learning-AOL.pdf
|   |-- EDAandPreprocess.ipynb
|   |-- NaiveBayes_ML_AOL_3_0.ipynb
|   |-- LogisticRegression_ML_AOL_2_0.ipynb
|   |-- BERT_ML_AOL_5_0.ipynb
|   `-- QuotesSelector.ipynb
`-- README.md
```

## Prerequisites

- Python 3.9 or newer is recommended
- Node.js and npm
- A trained model checkpoint named `last_trained_model_checkpoint.pth`

The checkpoint is not included in this repository. Download it from:

```text
https://drive.google.com/file/d/1UCsaBpSQEWzD8kkK2Etcdw5r63pmj2yO/view?usp=drive_web
```

Place the file here:

```text
backend/last_trained_model_checkpoint.pth
```

## How to Run

### 1. Start the backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install flask flask-cors torch transformers pandas scikit-learn numpy
python app.py
```

The API runs on:

```text
http://127.0.0.1:5000
```

### 2. Start the frontend

Open a second terminal:

```bash
cd frontend
npm install
npm start
```

The React app runs on:

```text
http://localhost:3000
```

## API

### `POST /get_quote`

Request body:

```json
{
  "inputText": "I feel nervous about tomorrow"
}
```

Response body:

```json
{
  "quote": "Returned quote text",
  "author": "Quote author",
  "emotion": "fear",
  "quote_emotion": "fear"
}
```

## Notes

- The backend expects to be run from the `backend/` directory because dataset and checkpoint paths are relative.
- The first backend startup may download the base `bert-base-uncased` tokenizer/model files through Hugging Face if they are not already cached locally.
- There is currently no committed Python `requirements.txt`; install the backend dependencies listed above manually.
- The frontend `package.json` proxies development requests to `http://127.0.0.1:5000`, while the current UI also calls that backend URL directly.

## License

This repository includes a [`LICENSE`](LICENSE) file.
