from flask import Flask, request, jsonify, render_template
import tensorflow as tf
from tensorflow.keras.metrics import MeanSquaredError
from tensorflow.keras.losses import MeanSquaredError
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
import pandas as pd
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

tf.config.set_visible_devices([], 'GPU')

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html') 

# Load dataset dan model (ganti dengan path yang sesuai)
data = pd.read_csv("dataset_tempat_wisata_malang.csv", sep=";")
# Ganti NaN dengan string kosong
data = data.fillna('')
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
        # Ambil semua atribut CSV untuk tempat wisata
        place_info = data.iloc[idx].to_dict()
        
        for key, value in place_info.items():
            if pd.isna(value):
                place_info[key] = ''
                
        # Buat dictionary dengan atribut yang diinginkan
        ordered_place_info = {
            "placeId": place_info["placeId"],
            "name": place_info["name"],
            "rating": place_info["rating"],
            "review": place_info["review"],
            "category": place_info["category"],
            "description": place_info["description"],
            "city": place_info["city"],
            "address": place_info["address"],
            "postalCode": place_info["postalCode"],
            "imageUrl": place_info["imageUrl"],
            "url": place_info["url"],
            "latitude": place_info["latitude"],
            "longitude": place_info["longitude"],
            "phone": place_info["phone"],
            "openingHours/0/day": place_info["openingHours/0/day"],
            "openingHours/0/hours": place_info["openingHours/0/hours"],
            "openingHours/1/day": place_info["openingHours/1/day"],
            "openingHours/1/hours": place_info["openingHours/1/hours"],
            "openingHours/2/day": place_info["openingHours/2/day"],
            "openingHours/2/hours": place_info["openingHours/2/hours"],
            "openingHours/3/day": place_info["openingHours/3/day"],
            "openingHours/3/hours": place_info["openingHours/3/hours"],
            "openingHours/4/day": place_info["openingHours/4/day"],
            "openingHours/4/hours": place_info["openingHours/4/hours"],
            "openingHours/5/day": place_info["openingHours/5/day"],
            "openingHours/5/hours": place_info["openingHours/5/hours"],
            "openingHours/6/day": place_info["openingHours/6/day"],
            "openingHours/6/hours": place_info["openingHours/6/hours"],
        }

        # Tambahkan predicted_score untuk pengurutan sementara
        ordered_place_info["predicted_score"] = predicted_score
        recommendations.append(ordered_place_info)

    # Urutkan berdasarkan predicted_score secara descending
    recommendations = sorted(recommendations, key=lambda x: x["predicted_score"], reverse=True)

    # Hapus atribut predicted_score dari output akhir
    for rec in recommendations:
        del rec["predicted_score"]

    return recommendations

@app.route('/recommend', methods=['POST'])
def recommend():
    input_features = request.json.get('input', '')
    logging.debug(f"Received input for recommendation: {input_features}")
    if input_features:
        try:
            recommendations = predict_relevance(input_features)
            logging.debug(f"Generated recommendations: {recommendations}")
            return jsonify({'recommendations': recommendations})
        except Exception as e:
            logging.error(f"Error in recommendation: {str(e)}")
            return jsonify({'error': str(e)}), 500
    logging.warning("Invalid input received")
    return jsonify({'error': 'Invalid input'}), 400


@app.route("/search", methods=["GET"])
def search():
    query = request.args.get("query", "").strip()
    logging.debug(f"Received search query: {query}")
    if query:
        try:
            recommendations = predict_relevance(query)
            logging.debug(f"Search results: {recommendations}")
            return jsonify({"recommendations": recommendations})
        except Exception as e:
            logging.error(f"Error in search: {str(e)}")
            return jsonify({"error": str(e)}), 500
    logging.warning("Empty search query received")
    return jsonify({"error": "Invalid input, query cannot be empty"}), 400


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
