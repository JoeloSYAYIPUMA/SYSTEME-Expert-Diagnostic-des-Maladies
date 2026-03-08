

import json
from knowledge_base import KnowledgeBase
from inference_engine import InferenceEngine


class AgriculturalExpertSystem:
    def __init__(self):
        self.kb = KnowledgeBase()
        self.engine = InferenceEngine(self.kb)
        self.session_data = {}

    def start_new_session(self):
        """Demarre une nouvelle session de diagnostic"""
        self.kb.reset_facts()
        self.session_data = {'step': 0, 'questions_posees': [], 'images_analysees': []}

    def process_image_analysis(self, image_features):
        """
        Analyse les caracteristiques extraites d'une image
        Simule l'analyse d'image (a connecter a un vrai modele CV)
        """
        features = {
            'partie_affectee': image_features.get('partie', 'feuilles'),
            'couleur_dominante': image_features.get('couleur', None),
            'forme_taches': image_features.get('forme', None),
            'texture': image_features.get('texture', None),
            'severite': image_features.get('severite', 'modere'),
        }

        # Mise a jour des faits bases sur l'image
        if features['partie_affectee']:
            self.kb.update_fact('partie_affectee', features['partie_affectee'])

        if features['couleur_dominante']:
            self.kb.update_fact('couleur_taches', features['couleur_dominante'])

        if features['forme_taches']:
            self.kb.update_fact('forme_taches', features['forme_taches'])

        if features['texture']:
            self.kb.update_fact('texture_feuille', features['texture'])

        # Estimer le stade de la maladie base sur la severite
        if features['severite'] == 'leger':
            self.kb.update_fact('stade_maladie', 'precoce')
        elif features['severite'] == 'modere':
            self.kb.update_fact('stade_maladie', 'intermediaire')
        elif features['severite'] == 'severe':
            self.kb.update_fact('stade_maladie', 'avance')

        return features

    def get_next_question(self):
        """
        Determine la prochaine question a poser a l'utilisateur
        basee sur les faits manquants
        """
        facts = self.kb.get_facts()

        # Questions predefinies pour guider l'utilisateur
        questions = [
            {
                'id': 'plante',
                'question': 'Quel type de plante cultivez-vous ?',
                'options': ['tomate', 'pomme_de_terre', 'vigne', 'fraise', 'cereales', 'autre'],
            },
            {
                'id': 'partie_affectee',
                'question': 'Quelle partie de la plante est affectee ?',
                'options': ['feuilles', 'tiges', 'fruits', 'fleurs', 'racines'],
            },
            {
                'id': 'couleur_taches',
                'question': 'Quelle est la couleur des taches ?',
                'options': ['vert_pale', 'brun_noir', 'blanc', 'orange_rouille', 'gris_brun', 'jaune'],
            },
            {
                'id': 'forme_taches',
                'question': 'Quelle est la forme des taches ?',
                'options': ['irreguliere', 'concentrique', 'poudreuse', 'pustules', 'cercles_concentriques'],
            },
            {
                'id': 'texture_feuille',
                'question': 'Quelle est la texture des feuilles ?',
                'options': ['normale', 'decomposee', 'farineuse', 'pourrie', 'seche'],
            },
            {
                'id': 'conditions_meteo',
                'question': 'Quelles ont ete les conditions meteo recentes ?',
                'options': ['pluie', 'sec', 'humide', 'orage'],
            },
            {
                'id': 'temperature',
                'question': 'Quelle est la temperature actuelle ?',
                'options': ['froid', 'doux', 'modere', 'chaud'],
            },
            {
                'id': 'humidite',
                'question': "Quel est le niveau d'humidite ?",
                'options': ['faible', 'moderee', 'elevee', 'tres_elevee'],
            },
            {
                'id': 'saison',
                'question': 'En quelle saison sommes-nous ?',
                'options': ['printemps', 'ete', 'automne', 'hiver'],
            },
            {
                'id': 'presence_insectes',
                'question': "Observez-vous la presence d'insectes ?",
                'options': [True, False],
            },
        ]

        # Trouver la premiere question dont la reponse est manquante
        for q in questions:
            if facts.get(q['id']) is None:
                return q

        return None  # Toutes les questions ont ete posees

    def add_user_response(self, question_id, response):
        """Ajoute la reponse de l'utilisateur aux faits"""
        self.kb.update_fact(question_id, response)
        self.session_data['questions_posees'].append({'question_id': question_id, 'response': response})

    def run_diagnosis(self):
        """
        Execute le diagnostic complet avec les faits actuels
        """
        facts = self.kb.get_facts()
        conclusions = self.engine.forward_chaining(facts)

        # Enrichir avec des informations sur les conditions meteo si disponibles
        if facts['conditions_meteo'] and facts['temperature'] and facts['humidite']:
            self._add_weather_recommendations(conclusions)

        return conclusions

    def _add_weather_recommendations(self, conclusions):
        """Ajoute des recommandations basees sur la meteo"""
        facts = self.kb.get_facts()

        # Recommandations specifiques meteo
        if facts['conditions_meteo'] == 'pluie' and facts['humidite'] == 'elevee':
            conclusions['conseils'].append(
                {
                    'type': 'meteo',
                    'message': "Evitez de traiter pendant la pluie. Attendez 24h apres la pluie pour appliquer des traitements.",
                }
            )

        if facts['temperature'] == 'chaud' and facts['humidite'] == 'faible':
            conclusions['alertes'].append(
                {
                    'type': 'stress',
                    'message': "Conditions de stress hydrique - Augmentez l'arrosage et paillez le sol",
                }
            )

    def generate_report(self, conclusions):
        """
        Genere un rapport complet du diagnostic
        """
        report = {
            'resume': {},
            'diagnostics': conclusions['diagnostics'],
            'alertes': conclusions['alertes'],
            'traitements': conclusions['traitements'],
            'conseils': conclusions['conseils'],
            'informations': conclusions['informations'],
            'explication': self.engine.get_explanation(),
        }

        # Creer un resume
        if conclusions['diagnostics']:
            main_diagnosis = max(conclusions['diagnostics'], key=lambda x: x['probabilite'])
            report['resume']['diagnostic_principal'] = main_diagnosis['maladie']
            report['resume']['confiance'] = f"{main_diagnosis['probabilite']*100:.0f}%"

            # Ajouter le traitement principal
            for traitement in conclusions['traitements']:
                if traitement.get('maladie') == main_diagnosis['maladie']:
                    report['resume']['traitement_recommande'] = traitement['recommandation']
                    break

        return report

    def save_session(self, filename):
        """Sauvegarde la session actuelle"""
        session = {
            'facts': self.kb.get_facts(),
            'session_data': self.session_data,
            'conclusions': self.engine.conclusions,
        }

        with open(f"{filename}.json", 'w', encoding='utf-8') as f:
            json.dump(session, f, indent=2, ensure_ascii=False)

        return f"Session sauvegardee dans {filename}.json"

    def load_session(self, filename):
        """Charge une session precedente"""
        with open(f"{filename}.json", 'r', encoding='utf-8') as f:
            session = json.load(f)

        # Restaurer les faits
        for key, value in session['facts'].items():
            self.kb.update_fact(key, value)

        self.session_data = session['session_data']
        self.engine.conclusions = session['conclusions']

        return 'Session chargee avec succes'
