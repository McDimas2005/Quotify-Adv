from flask import Flask, request, jsonify
import torch
from transformers import BertTokenizer, BertForSequenceClassification, AdamW
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from sklearn.preprocessing import LabelEncoder
from flask_cors import CORS
import random

app = Flask(__name__)
CORS(app)

# Load the dataset
dataset = pd.read_csv('./(Preprocessed)Emotion_classify_Data(Labeled).csv')

# Shuffle the dataset
dataset = dataset.sample(frac=1, random_state=42).reset_index(drop=True)

# Initialize BERT tokenizer and model
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertForSequenceClassification.from_pretrained('bert-base-uncased', num_labels=dataset['Emotion'].nunique())

# Fine-tune BERT on your dataset
learning_rate = 2e-5
optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate)
loss_fn = torch.nn.CrossEntropyLoss()

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model.to(device)

# Load the checkpoint
checkpoint = torch.load('last_trained_model_checkpoint.pth', map_location=torch.device('cpu'))
model.load_state_dict(checkpoint['model_state_dict'], strict=False)
optimizer = AdamW(model.parameters(), lr=5e-5)
optimizer.load_state_dict(checkpoint['optimizer_state_dict'])

epoch = checkpoint['epoch']
best_val_loss = checkpoint['best_val_loss']
early_stop_count = checkpoint['early_stop_count']

print(f"Model and optimizer states loaded successfully.")
print(f"Epoch: {epoch}, Best Validation Loss: {best_val_loss}, Early Stop Count: {early_stop_count}")

# Prepare label encoder
emotion_labels = dataset['Emotion']
label_encoder = LabelEncoder()
label_encoder.fit(emotion_labels)

# Load quotes and label them with emotions
quotesDF = pd.read_csv('./(Preprocessed)quotes.csv')

def predict_emotion(text, label_encoder):
    inputs = tokenizer.encode_plus(text, add_special_tokens=True, max_length=128, padding='max_length', truncation=True, return_tensors='pt')
    input_ids = inputs['input_ids'].to(device)
    attention_mask = inputs['attention_mask'].to(device)

    with torch.no_grad():
        model.eval()
        outputs = model(input_ids, attention_mask=attention_mask)
    logits = outputs.logits
    predicted_label = torch.argmax(logits, dim=1).item()
    predicted_emotion = label_encoder.inverse_transform([predicted_label])[0]

    return predicted_emotion, logits

def find_most_similar_quote(input_sentence, quotes_df, input_emotion, emotion_weight=1.1):
    quotes = quotes_df['Quote'].tolist()
    authors = quotes_df['Author'].tolist()
    emotions = quotes_df['emotion'].tolist()

    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(quotes)
    input_vec = vectorizer.transform([input_sentence])
    cosine_similarities = cosine_similarity(input_vec, tfidf_matrix).flatten()

    emotion_weights = np.array([emotion_weight if emotion == input_emotion else 1.0 for emotion in emotions])
    weighted_similarities = cosine_similarities * emotion_weights

    top_10_indices = np.argsort(weighted_similarities)[-5:]
    selected_index = random.choice(top_10_indices)

    return quotes[selected_index], authors[selected_index], emotions[selected_index]

@app.route('/get_quote', methods=['POST'])
def get_quote():
    data = request.get_json()
    input_text = data['inputText']
    detected_emotion, _ = predict_emotion(input_text, label_encoder)
    quote, author, quote_emotion = find_most_similar_quote(input_text, quotesDF, detected_emotion)
    return jsonify({"quote": quote, "author": author, "emotion": detected_emotion, "quote_emotion": quote_emotion})

if __name__ == '__main__':
    app.run(port=5000, debug=True)