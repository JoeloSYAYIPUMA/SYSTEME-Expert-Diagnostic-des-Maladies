# Systeme Expert Agricole - Diagnostic des Maladies des Plantes

 ## LISTE DES PARTICIPANTS
 KAMBALE SYAYIPUMA JOEL
 
 ELOGE MUYISA MUMBERE
 
 KAVUGHO VOLONTE VITAL

## Description
Systeme expert base sur des regles pour le diagnostic precoce des maladies des plantes, avec analyse d'images, recommandations de traitement et alertes epidemiologiques.

## Fonctionnalites
- Analyse d'images : detection des caracteristiques visuelles des maladies
- Moteur d'inference : chainage avant avec 12+ regles expertes
- Alertes meteo : prediction des risques epidemiologiques
- Recommandations : traitements adaptes au stade de la maladie
- Interface intuitive : web interface responsive

## Installation

1. Cloner le repository
```bash
git clone https://github.com/votre-compte/agri-expert.git
cd agri-expert
```

2. Installer les dependances
```bash
pip install -r requirements.txt
```

3. Lancer l'application
```bash
python app.py
```

4. Ouvrir le navigateur
```text
http://localhost:5000
```

## Utilisation

1. Demarrer un diagnostic
2. Telecharger une photo de la plante malade
3. Repondre aux questions pour affiner le diagnostic
4. Obtenir les resultats : maladie, traitements, conseils

## Architecture

```text
├── app.py
├── expert_system.py
├── knowledge_base.py
├── inference_engine.py
├── templates/
│   └── index.html
└── static/
    ├── style.css
    ├── uploads/
    └── sessions/
```



