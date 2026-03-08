

import os
import uuid

import cv2
import numpy as np
from flask import Flask, jsonify, render_template, request, session
from werkzeug.utils import secure_filename

from expert_system import AgriculturalExpertSystem

app = Flask(__name__)
app.secret_key = 'votre_cle_secrete_tres_longue_et_aleatoire_123456789'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Assurer que les dossiers existent
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('static/sessions', exist_ok=True)

# Stockage des sessions utilisateur (en production, utiliser une BD)
user_sessions = {}


def allowed_file(filename):
    """Verifie si le fichier est une image autorisee"""
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


def analyze_image(image_path):
    """
    Analyse une image pour en extraire des caracteristiques
    Version simplifiee - a ameliorer avec un vrai modele de deep learning
    """
    try:
        # Lire l'image avec OpenCV
        img = cv2.imread(image_path)
        if img is None:
            return None

        # Convertir en RGB
        _img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # Redimensionner pour l'analyse
        _img_resized = cv2.resize(_img_rgb, (224, 224))

        # Analyse simplifiee des couleurs
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        # Definir les plages de couleurs pour differentes maladies
        color_ranges = {
            'brun_noir': [(0, 0, 0), (180, 255, 50)],
            'blanc': [(0, 0, 200), (180, 50, 255)],
            'jaune': [(20, 100, 100), (30, 255, 255)],
            'orange_rouille': [(0, 100, 100), (10, 255, 255)],
            'vert_pale': [(40, 50, 50), (80, 255, 255)],
        }

        # Detecter la couleur dominante
        dominant_color = None
        max_pixels = 0
        total_pixels = img.shape[0] * img.shape[1]

        for color_name, (lower, upper) in color_ranges.items():
            lower_arr = np.array(lower, dtype=np.uint8)
            upper_arr = np.array(upper, dtype=np.uint8)

            mask = cv2.inRange(hsv, lower_arr, upper_arr)
            color_pixels = cv2.countNonZero(mask)

            if color_pixels > max_pixels and color_pixels > total_pixels * 0.1:
                max_pixels = color_pixels
                dominant_color = color_name

        # Analyser la texture (simplifie)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        variance = np.var(gray)

        if variance < 500:
            texture = 'lisse'
        elif variance < 1500:
            texture = 'granuleuse'
        else:
            texture = 'rugueuse'

        # Analyser la forme des taches (tres simplifie)
        edges = cv2.Canny(gray, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        shape = 'irreguliere'
        if len(contours) > 0:
            largest_contour = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(largest_contour)
            perimeter = cv2.arcLength(largest_contour, True)

            if perimeter > 0:
                circularity = 4 * np.pi * area / (perimeter * perimeter)
                if circularity > 0.8:
                    shape = 'circulaire'
                elif circularity > 0.6:
                    shape = 'ovale'
                else:
                    shape = 'irreguliere'

        # Estimer la severite basee sur la couverture des taches
        green_mask = cv2.inRange(hsv, (35, 50, 50), (85, 255, 255))
        non_green_pixels = total_pixels - cv2.countNonZero(green_mask)
        severity_ratio = non_green_pixels / total_pixels

        if severity_ratio < 0.1:
            severity = 'leger'
        elif severity_ratio < 0.3:
            severity = 'modere'
        else:
            severity = 'severe'

        return {
            'couleur': dominant_color,
            'forme': shape,
            'texture': texture,
            'severite': severity,
            'partie': 'feuilles',
        }

    except Exception as e:
        print(f"Erreur lors de l'analyse de l'image: {e}")
        return None


@app.route('/')
def index():
    """Page d'accueil"""
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
        user_sessions[session['session_id']] = {'expert_system': AgriculturalExpertSystem(), 'step': 0}

    return render_template('index.html')


@app.route('/start_diagnosis', methods=['POST'])
def start_diagnosis():
    """Demarrer un nouveau diagnostic"""
    session_id = session.get('session_id')
    if session_id in user_sessions:
        user_sessions[session_id]['expert_system'].start_new_session()
        user_sessions[session_id]['step'] = 1
        return jsonify({'status': 'success', 'message': 'Diagnostic demarre'})

    return jsonify({'status': 'error', 'message': 'Session invalide'})


@app.route('/upload_image', methods=['POST'])
def upload_image():
    """Telecharger et analyser une image"""
    if 'file' not in request.files:
        return jsonify({'status': 'error', 'message': 'Aucun fichier'})

    file = request.files['file']
    if file.filename == '':
        return jsonify({'status': 'error', 'message': 'Nom de fichier vide'})

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(filepath)

        # Analyser l'image
        features = analyze_image(filepath)

        if features:
            session_id = session.get('session_id')
            if session_id in user_sessions:
                expert = user_sessions[session_id]['expert_system']
                expert.process_image_analysis(features)

                return jsonify(
                    {
                        'status': 'success',
                        'features': features,
                        'image_url': f'/static/uploads/{unique_filename}',
                    }
                )

        return jsonify({'status': 'error', 'message': "Impossible d'analyser l'image"})

    return jsonify({'status': 'error', 'message': 'Format de fichier non supporte'})


@app.route('/get_next_question', methods=['GET'])
def get_next_question():
    """Obtenir la prochaine question a poser"""
    session_id = session.get('session_id')
    if session_id in user_sessions:
        expert = user_sessions[session_id]['expert_system']
        question = expert.get_next_question()

        if question:
            return jsonify({'status': 'success', 'question': question})
        return jsonify({'status': 'complete', 'message': 'Toutes les questions ont ete posees'})

    return jsonify({'status': 'error', 'message': 'Session invalide'})


@app.route('/submit_answer', methods=['POST'])
def submit_answer():
    """Soumettre une reponse a une question"""
    data = request.json
    question_id = data.get('question_id')
    response = data.get('response')

    session_id = session.get('session_id')
    if session_id in user_sessions:
        expert = user_sessions[session_id]['expert_system']
        expert.add_user_response(question_id, response)

        return jsonify({'status': 'success'})

    return jsonify({'status': 'error', 'message': 'Session invalide'})


@app.route('/run_diagnosis', methods=['POST'])
def run_diagnosis_route():
    """Executer le diagnostic complet"""
    session_id = session.get('session_id')
    if session_id in user_sessions:
        expert = user_sessions[session_id]['expert_system']
        conclusions = expert.run_diagnosis()
        report = expert.generate_report(conclusions)

        return jsonify({'status': 'success', 'report': report})

    return jsonify({'status': 'error', 'message': 'Session invalide'})


@app.route('/reset_session', methods=['POST'])
def reset_session():
    """Reinitialiser la session"""
    session_id = session.get('session_id')
    if session_id in user_sessions:
        user_sessions[session_id]['expert_system'].start_new_session()
        user_sessions[session_id]['step'] = 0

        return jsonify({'status': 'success'})

    return jsonify({'status': 'error', 'message': 'Session invalide'})


@app.route('/save_session', methods=['POST'])
def save_session():
    """Sauvegarder la session"""
    data = request.json
    filename = data.get('filename', 'session_save')

    session_id = session.get('session_id')
    if session_id in user_sessions:
        expert = user_sessions[session_id]['expert_system']
        result = expert.save_session(f"static/sessions/{filename}")

        return jsonify({'status': 'success', 'message': result})

    return jsonify({'status': 'error', 'message': 'Session invalide'})


if __name__ == '__main__':
    app.run(debug=True, port=5000)
