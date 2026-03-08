"""
Base de connaissances du systeme expert agricole
Contient les faits, les regles et les connaissances expertes
"""


class KnowledgeBase:
    def __init__(self):
        # Faits initiaux (seront completes par l'utilisateur)
        self.facts = {
            'plante': None,
            'symptomes_observes': [],
            'partie_affectee': None,
            'couleur_taches': None,
            'forme_taches': None,
            'texture_feuille': None,
            'presence_insectes': False,
            'conditions_meteo': None,
            'stade_maladie': 'precoce',  # precoce, intermediaire, avance
            'temperature': None,
            'humidite': None,
            'saison': None,
            'culture_previous': None,
        }

        # Base de regles du systeme expert
        self.rules = [
            # REGLES POUR LE MILDIOU (Pomme de terre, tomate)
            {
                'id': 'R001',
                'name': 'Diagnostic Mildiou - Stade precoce',
                'conditions': {
                    'plante': ['tomate', 'pomme_de_terre'],
                    'partie_affectee': 'feuilles',
                    'couleur_taches': 'vert_pale',
                    'forme_taches': 'irreguliere',
                    'humidite': 'elevee',
                    'temperature': ['doux', 'modere'],
                },
                'actions': [
                    {'type': 'diagnostic', 'maladie': 'Mildiou', 'probabilite': 0.8},
                    {'type': 'alerte', 'message': 'Conditions favorables au mildiou detectees'},
                    {
                        'type': 'traitement',
                        'stade': 'precoce',
                        'recommandation': 'appliquer bouillie bordelaise 1%',
                    },
                ],
            },
            {
                'id': 'R002',
                'name': 'Diagnostic Mildiou - Stade avance',
                'conditions': {
                    'plante': ['tomate', 'pomme_de_terre'],
                    'partie_affectee': 'feuilles',
                    'couleur_taches': 'brun_noir',
                    'forme_taches': 'concentrique',
                    'texture_feuille': 'decomposee',
                    'presence_insectes': False,
                },
                'actions': [
                    {'type': 'diagnostic', 'maladie': 'Mildiou', 'probabilite': 0.95},
                    {
                        'type': 'alerte',
                        'message': 'Infection severe de mildiou - Action immediate requise',
                    },
                    {
                        'type': 'traitement',
                        'stade': 'avance',
                        'recommandation': 'appliquer fongicide cuivrique + retirer plants infectes',
                    },
                ],
            },
            # REGLES POUR L'OIDIUM (Blanc)
            {
                'id': 'R003',
                'name': 'Diagnostic Oidium',
                'conditions': {
                    'partie_affectee': ['feuilles', 'tiges'],
                    'couleur_taches': 'blanc',
                    'forme_taches': 'poudreuse',
                    'texture_feuille': 'farineuse',
                    'humidite': 'moderee',
                    'temperature': 'chaud',
                },
                'actions': [
                    {'type': 'diagnostic', 'maladie': 'Oidium', 'probabilite': 0.9},
                    {
                        'type': 'alerte',
                        'message': "Infection d'oidium detectee - Traitement preventif recommande",
                    },
                    {
                        'type': 'traitement',
                        'stade': 'tous',
                        'recommandation': 'soufre micronise ou bicarbonate de soude',
                    },
                ],
            },
            # REGLES POUR LA ROUILLE
            {
                'id': 'R004',
                'name': 'Diagnostic Rouille',
                'conditions': {
                    'partie_affectee': 'feuilles',
                    'couleur_taches': 'orange_rouille',
                    'forme_taches': 'pustules',
                    'texture_feuille': 'poudreuse',
                    'humidite': 'elevee',
                    'saison': 'printemps',
                },
                'actions': [
                    {'type': 'diagnostic', 'maladie': 'Rouille', 'probabilite': 0.85},
                    {
                        'type': 'traitement',
                        'stade': 'tous',
                        'recommandation': 'eliminer feuilles infectees, traitement soufre',
                    },
                ],
            },
            # REGLES POUR LE BOTRYTIS (Pourriture grise)
            {
                'id': 'R005',
                'name': 'Diagnostic Botrytis',
                'conditions': {
                    'partie_affectee': ['fruits', 'fleurs'],
                    'couleur_taches': 'gris_brun',
                    'forme_taches': 'moisissure',
                    'texture_feuille': 'pourrie',
                    'humidite': 'tres_elevee',
                    'temperature': 'frais',
                },
                'actions': [
                    {'type': 'diagnostic', 'maladie': 'Botrytis', 'probabilite': 0.88},
                    {'type': 'alerte', 'message': 'Risque de pourriture grise - Ameliorer aeration'},
                    {
                        'type': 'traitement',
                        'stade': 'tous',
                        'recommandation': 'supprimer parties atteintes, traitement a base de cuivre',
                    },
                ],
            },
            # REGLES POUR L'ALTERNARIOSE
            {
                'id': 'R006',
                'name': 'Diagnostic Alternariose',
                'conditions': {
                    'plante': ['tomate', 'pomme_de_terre'],
                    'partie_affectee': 'feuilles',
                    'couleur_taches': 'brun_fonce',
                    'forme_taches': 'cercles_concentriques',
                    'texture_feuille': 'seche',
                    'stade_maladie': 'avance',
                },
                'actions': [
                    {'type': 'diagnostic', 'maladie': 'Alternariose', 'probabilite': 0.82},
                    {
                        'type': 'traitement',
                        'stade': 'tous',
                        'recommandation': 'fongicides specifiques, rotation des cultures',
                    },
                ],
            },
            # REGLES DE PREVENTION ET ALERTES METEO
            {
                'id': 'R007',
                'name': 'Alerte Mildiou - Conditions meteo favorables',
                'conditions': {
                    'conditions_meteo': 'pluie',
                    'temperature': 'doux',
                    'humidite': 'elevee',
                    'saison': ['printemps', 'ete'],
                },
                'actions': [
                    {
                        'type': 'alerte_epidemio',
                        'message': 'ALERTE: Conditions ideales pour developpement mildiou',
                        'risque': 'eleve',
                        'action_preventive': 'traiter preventivement dans 48h',
                    }
                ],
            },
            {
                'id': 'R008',
                'name': 'Alerte Oidium - Conditions favorables',
                'conditions': {
                    'conditions_meteo': 'sec',
                    'temperature': 'chaud',
                    'humidite': 'moderee',
                    'saison': 'ete',
                },
                'actions': [
                    {
                        'type': 'alerte_epidemio',
                        'message': 'ALERTE: Risque oidium eleve (chaleur + sec)',
                        'risque': 'moyen',
                        'action_preventive': 'surveiller jeunes pousses, traiter preventivement si sensible',
                    }
                ],
            },
            # REGLES DE RECOMMANDATIONS SPECIFIQUES PAR STADE
            {
                'id': 'R009',
                'name': 'Traitement mildiou - Stade precoce',
                'conditions': {'diagnostic': 'Mildiou', 'stade_maladie': 'precoce'},
                'actions': [
                    {
                        'type': 'recommandation',
                        'message': "Traitement preventif: purin d'ortie ou bouillie bordelaise a 1%",
                    },
                    {'type': 'conseil', 'message': 'Eliminer les premieres feuilles touchees'},
                ],
            },
            {
                'id': 'R010',
                'name': 'Traitement mildiou - Stade intermediaire',
                'conditions': {'diagnostic': 'Mildiou', 'stade_maladie': 'intermediaire'},
                'actions': [
                    {
                        'type': 'recommandation',
                        'message': 'Traitement curatif: bouillie bordelaise 2% + cuivre',
                    },
                    {'type': 'conseil', 'message': 'Arracher et bruler les plants trop atteints'},
                ],
            },
            # REGLES DE CONSEILS CULTURAUX
            {
                'id': 'R011',
                'name': 'Conseil rotation mildiou',
                'conditions': {
                    'diagnostic': 'Mildiou',
                    'culture_previous': ['tomate', 'pomme_de_terre'],
                },
                'actions': [
                    {
                        'type': 'conseil_long_terme',
                        'message': 'Rotation des cultures: ne pas replanter de solanacees avant 3-4 ans',
                    }
                ],
            },
            {
                'id': 'R012',
                'name': 'Conseil prevention generale',
                'conditions': {'partie_affectee': 'feuilles'},
                'actions': [
                    {
                        'type': 'conseil_prevention',
                        'message': 'Arrosage au pied plutot que sur le feuillage pour eviter propagation',
                    }
                ],
            },
        ]

        # Dictionnaire des maladies avec leurs caracteristiques
        self.maladies_info = {
            'Mildiou': {
                'nom': 'Mildiou (Phytophthora infestans)',
                'description': 'Maladie cryptogamique redoutable affectant principalement les solanacees',
                'symptomes': 'Taches huileuses sur feuilles devenant brunes, puis noires. Feutrage blanc sous feuilles par temps humide.',
                'conditions_favorables': 'Humidite elevee (>90%) et temperatures douces (10-25C)',
                'plantes_hotes': ['Tomate', 'Pomme de terre', 'Aubergine'],
                'traitements': {
                    'preventif': 'Bouillie bordelaise 1%, purin de prele, bon espacement',
                    'curatif': 'Bouillie bordelaise 2%, fongicides cupriques, arrachage plants infectes',
                },
                'prevention': 'Rotation des cultures, varietes resistantes, arrosage au pied',
            },
            'Oidium': {
                'nom': 'Oidium (Erysiphales)',
                'description': 'Maladie cryptogamique reconnaissable a son aspect de farine blanche',
                'symptomes': 'Feutrage blanc poudreux sur feuilles et tiges, deformation des tissus',
                'conditions_favorables': 'Temps chaud et sec, ecarts de temperature importants',
                'plantes_hotes': ['Cucurbitacees', 'Rosacees', 'Vigne', 'Cereales'],
                'traitements': {
                    'preventif': 'Soufre, lait dilue, decoction de prele',
                    'curatif': 'Soufre micronise, bicarbonate de soude',
                },
                'prevention': "Aeration des cultures, eviter exces d'azote",
            },
            'Rouille': {
                'nom': 'Rouille (Pucciniales)',
                'description': 'Maladie fongique caracterisee par des pustules colorees',
                'symptomes': 'Pustules oranges, brunes ou noires sur feuilles',
                'conditions_favorables': 'Humidite elevee, printemps humides',
                'plantes_hotes': ['Cereales', 'Allium', 'Rosiers', 'Haricots'],
                'traitements': {
                    'preventif': "Purins de prele, decoction d'ail",
                    'curatif': 'Soufre, bouillie bordelaise',
                },
                'prevention': 'Elimination feuilles atteintes, espacement',
            },
            'Botrytis': {
                'nom': 'Botrytis / Pourriture grise (Botrytis cinerea)',
                'description': 'Champignon provoquant une pourriture molle avec duvet gris',
                'symptomes': 'Moisissure grise, taches brunes sur fruits et fleurs',
                'conditions_favorables': 'Humidite tres elevee, temps frais, blessures',
                'plantes_hotes': ['Fraise', 'Tomate', 'Raisin', 'Laitue'],
                'traitements': {
                    'preventif': 'Aeration, eviter blessures, purin de prele',
                    'curatif': 'Suppression parties atteintes, fongicides specifiques',
                },
                'prevention': 'Espacement, paillage, arrosage matinal',
            },
            'Alternariose': {
                'nom': 'Alternariose (Alternaria solani)',
                'description': 'Maladie causant des taches concentriques sur les feuilles',
                'symptomes': 'Taches brunes avec cercles concentriques, necroses',
                'conditions_favorables': 'Alternance humidite/secheresse, chaleur',
                'plantes_hotes': ['Tomate', 'Pomme de terre', 'Chou'],
                'traitements': {
                    'preventif': "Rotation, paillage, purin d'ortie",
                    'curatif': 'Fongicides cuivriques, bouillie bordelaise',
                },
                'prevention': 'Rotation des cultures sur 3-4 ans',
            },
        }

    def get_rules(self):
        """Retourne toutes les regles"""
        return self.rules

    def get_maladie_info(self, maladie):
        """Retourne les informations detaillees sur une maladie"""
        return self.maladies_info.get(maladie, {})

    def get_facts(self):
        """Retourne les faits actuels"""
        return self.facts

    def update_fact(self, key, value):
        """Met a jour un fait"""
        self.facts[key] = value

    def reset_facts(self):
        """Reinitialise les faits"""
        self.facts = {
            'plante': None,
            'symptomes_observes': [],
            'partie_affectee': None,
            'couleur_taches': None,
            'forme_taches': None,
            'texture_feuille': None,
            'presence_insectes': False,
            'conditions_meteo': None,
            'stade_maladie': 'precoce',
            'temperature': None,
            'humidite': None,
            'saison': None,
            'culture_previous': None,
        }
