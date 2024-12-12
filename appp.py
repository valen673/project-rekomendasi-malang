from flask import Flask, request, jsonify
import tensorflow as tf
from tensorflow.keras.metrics import MeanSquaredError
from tensorflow.keras.losses import MeanSquaredError
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
import pandas as pd

tf.config.set_visible_devices([], 'GPU')

app = Flask(__name__)

# Load dataset dan model (ganti dengan path yang sesuai)
data = pd.read_csv("dataset_tempat_wisata_malang.csv", sep=";")
stopword_factory = StopWordRemoverFactory()
stopword_remover = stopword_factory.create_stop_word_remover()

# Preprocessing dan TF-IDF
def preprocess_text(text):
    if pd.isnull(text):
        return ""
    return stopword_remover.remove(text.lower())

data['combined_features'] = data['name'] + " " + data['category'] + " " + data['description']
data['combined_features'] = data['combined_features'].apply(preprocess_text)

tfidf = TfidfVectorizer()
tfidf_matrix = tfidf.fit_transform(data['combined_features'])
cosine_sim = cosine_similarity(tfidf_matrix)

# Load TensorFlow model
model = tf.keras.models.load_model(
    'malang_tourism_model.h5',
    custom_objects={'mse': MeanSquaredError()}
)

# Fungsi untuk memberikan rekomendasi
def predict_relevance(input_features):
    input_vector = tfidf.transform([preprocess_text(input_features)]).toarray().flatten()
    recommendations = []

    for idx in range(len(data)):
        place_vector = tfidf_matrix[idx].toarray().flatten()
        combined_vector = np.concatenate((input_vector, place_vector))
        combined_vector = tf.convert_to_tensor([combined_vector], dtype=tf.float32)

        predicted_score = model.predict(combined_vector)[0][0]
        recommendations.append({
            'name': data.iloc[idx]['name'],
            'description': data.iloc[idx]['description'],
            'predicted_score': float(predicted_score)  # Konversi ke float
        })
    recommendations = sorted(recommendations, key=lambda x: x['predicted_score'], reverse=True)
    return recommendations

@app.route('/recommend', methods=['POST'])
def recommend():
    input_features = request.json.get('input', '')
    if input_features:
        try:
            recommendations = predict_relevance(input_features)
            return jsonify({'recommendations': recommendations})
        except Exception as e:
            # Tangani kesalahan yang mungkin terjadi selama prediksi
            return jsonify({'error': str(e)}), 500  # Kembalikan status error 500
    return jsonify({'error': 'Invalid input'}), 400

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
