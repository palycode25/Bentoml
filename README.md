# Prédiction de la Chance d'Admission — Projet BentoML

Projet MLOps de bout en bout : entraînement d'un modèle de régression, exposition via une API sécurisée par JWT, packaging avec BentoML, et conteneurisation Docker.

## Contexte

Ce projet prédit la chance d'admission d'un étudiant dans une université à partir de 7 variables :

| Variable | Description |
|---|---|
| gre_score | Score GRE (sur 340) |
| toefl_score | Score TOEFL (sur 120) |
| university_rating | Note de l'université (sur 5) |
| sop | Statement of Purpose (sur 5) |
| lor | Letter of Recommendation (sur 5) |
| cgpa | Cumulative Grade Point Average (sur 10) |
| research | Expérience de recherche (0 ou 1) |

Cible : chance_of_admit (probabilité entre 0 et 1)

## Architecture du projet

    examen_bentoml/
    ├── data/
    │   ├── raw/                    Données brutes (admission.csv)
    │   └── processed/              Données nettoyées et splitées
    ├── models/                     (non utilisé, modèle stocké dans le Model Store BentoML)
    ├── src/
    │   ├── prepare_data.py         Nettoyage + split train/test
    │   ├── train_model.py          Entraînement + évaluation + sauvegarde du modèle
    │   └── service.py              Service BentoML : API sécurisée (JWT)
    ├── tests/
    │   └── test_endpoints.py       Tests pytest de l'API
    ├── bentofile.yaml               Configuration du build Bento
    ├── requirements.txt
    └── README.md

## Stack technique

- Python 3.12
- scikit-learn — modèle de régression linéaire
- BentoML 1.4.35 — packaging, Model Store, serving
- FastAPI / Starlette — middleware ASGI pour l'authentification
- PyJWT — génération et validation des tokens
- Docker — conteneurisation
- pytest — tests automatisés

## Installation et exécution locale

### 1. Cloner et configurer l'environnement

    git clone https://github.com/<votre-login>/examen_bentoml.git
    cd examen_bentoml
    python3 -m venv .venv
    source .venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt

### 2. Récupérer les données

    curl -L -o data/raw/admission.csv https://assets-datascientest.s3.eu-west-1.amazonaws.com/MLOPS/bentoml/admission.csv

### 3. Préparer les données

    python src/prepare_data.py

Génère X_train.csv, X_test.csv, y_train.csv, y_test.csv dans data/processed/.

### 4. Entraîner le modèle

    python src/train_model.py
    bentoml models list

Affiche les métriques (R², RMSE, MAE) et enregistre le modèle dans le Model Store BentoML sous le nom admission_lr.

### 5. Lancer le service API en local

    bentoml serve src.service:AdmissionPredictionService --port 3001

Dans un second terminal, tester l'authentification et la prédiction :

    TOKEN=$(curl -s -X POST "http://127.0.0.1:3001/login" -H "Content-Type: application/json" -d '{"credentials":{"username":"user123","password":"password123"}}' | python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")
    curl -X POST "http://127.0.0.1:3001/predict" -H "Content-Type: application/json" -H "Authorization: Bearer $TOKEN" -d '{"input_data":{"gre_score":320,"toefl_score":110,"university_rating":4,"sop":4.0,"lor":4.5,"cgpa":8.9,"research":1}}'

## Packaging et conteneurisation

    bentoml build
    bentoml containerize admission_prediction_service:latest
    docker run --rm -d -p 3000:3000 --name admission_service admission_prediction_service:latest
    docker save admission_prediction_service:latest -o admission_prediction_service.tar
    docker load -i admission_prediction_service.tar

## Sécurité — Authentification JWT

- POST /login : vérifie les identifiants (user123 / password123 par défaut) et retourne un token JWT valide 1h
- POST /predict : protégé par un middleware ASGI (JWTAuthMiddleware) qui vérifie le header Authorization: Bearer avant d'autoriser l'accès

Les identifiants et la clé secrète JWT sont en dur dans service.py à des fins pédagogiques. Ne pas utiliser tel quel en production.

## Tests

    pytest -v tests/

Couvre : authentification réussie/échouée, accès /predict refusé sans token ou avec token invalide/mal formé, prédiction valide avec token correct, rejet des données d'entrée invalides.

## Performances du modèle

| Métrique | Valeur |
|---|---|
| R² | ~0.82 |
| RMSE | ~0.06 |
| MAE | ~0.04 |

Modèle : LinearRegression (scikit-learn), entraîné sur un split 80/20.

## Endpoints de l'API

| Méthode | Route | Auth requise | Description |
|---|---|---|---|
| POST | /login | Non | Authentification, retourne un JWT |
| POST | /predict | Oui (Bearer token) | Prédiction de la chance d'admission |

## Architecture BentoML

Le service est composé de deux classes avec bentoml.depends :

- AdmissionModelService : charge le modèle et expose predict_array
- AdmissionPredictionService : expose les routes publiques /login et /predict, délègue l'inférence à AdmissionModelService, et porte le middleware JWT

## Licence

Projet réalisé dans le cadre du module BentoML — DataScientest.# Prédiction de la Chance d'Admission — Projet BentoML

Projet MLOps de bout en bout : entraînement d'un modèle de régression, exposition via une API sécurisée par JWT, packaging avec BentoML, et conteneurisation Docker.

## Contexte

Ce projet prédit la chance d'admission d'un étudiant dans une université à partir de 7 variables :

| Variable | Description |
|---|---|
| gre_score | Score GRE (sur 340) |
| toefl_score | Score TOEFL (sur 120) |
| university_rating | Note de l'université (sur 5) |
| sop | Statement of Purpose (sur 5) |
| lor | Letter of Recommendation (sur 5) |
| cgpa | Cumulative Grade Point Average (sur 10) |
| research | Expérience de recherche (0 ou 1) |

Cible : chance_of_admit (probabilité entre 0 et 1)

## Architecture du projet

    examen_bentoml/
    ├── data/
    │   ├── raw/                    Données brutes (admission.csv)
    │   └── processed/              Données nettoyées et splitées
    ├── models/                     (non utilisé, modèle stocké dans le Model Store BentoML)
    ├── src/
    │   ├── prepare_data.py         Nettoyage + split train/test
    │   ├── train_model.py          Entraînement + évaluation + sauvegarde du modèle
    │   └── service.py              Service BentoML : API sécurisée (JWT)
    ├── tests/
    │   └── test_endpoints.py       Tests pytest de l'API
    ├── bentofile.yaml               Configuration du build Bento
    ├── requirements.txt
    └── README.md

## Stack technique

- Python 3.12
- scikit-learn — modèle de régression linéaire
- BentoML 1.4.35 — packaging, Model Store, serving
- FastAPI / Starlette — middleware ASGI pour l'authentification
- PyJWT — génération et validation des tokens
- Docker — conteneurisation
- pytest — tests automatisés

## Installation et exécution locale

### 1. Cloner et configurer l'environnement

    git clone https://github.com/<votre-login>/examen_bentoml.git
    cd examen_bentoml
    python3 -m venv .venv
    source .venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt

### 2. Récupérer les données

    curl -L -o data/raw/admission.csv https://assets-datascientest.s3.eu-west-1.amazonaws.com/MLOPS/bentoml/admission.csv

### 3. Préparer les données

    python src/prepare_data.py

Génère X_train.csv, X_test.csv, y_train.csv, y_test.csv dans data/processed/.

### 4. Entraîner le modèle

    python src/train_model.py
    bentoml models list

Affiche les métriques (R², RMSE, MAE) et enregistre le modèle dans le Model Store BentoML sous le nom admission_lr.

### 5. Lancer le service API en local

    bentoml serve src.service:AdmissionPredictionService --port 3001

Dans un second terminal, tester l'authentification et la prédiction :

    TOKEN=$(curl -s -X POST "http://127.0.0.1:3001/login" -H "Content-Type: application/json" -d '{"credentials":{"username":"user123","password":"password123"}}' | python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")
    curl -X POST "http://127.0.0.1:3001/predict" -H "Content-Type: application/json" -H "Authorization: Bearer $TOKEN" -d '{"input_data":{"gre_score":320,"toefl_score":110,"university_rating":4,"sop":4.0,"lor":4.5,"cgpa":8.9,"research":1}}'

## Packaging et conteneurisation

    bentoml build
    bentoml containerize admission_prediction_service:latest
    docker run --rm -d -p 3000:3000 --name admission_service admission_prediction_service:latest
    docker save admission_prediction_service:latest -o admission_prediction_service.tar
    docker load -i admission_prediction_service.tar

## Sécurité — Authentification JWT

- POST /login : vérifie les identifiants (user123 / password123 par défaut) et retourne un token JWT valide 1h
- POST /predict : protégé par un middleware ASGI (JWTAuthMiddleware) qui vérifie le header Authorization: Bearer avant d'autoriser l'accès

Les identifiants et la clé secrète JWT sont en dur dans service.py à des fins pédagogiques. Ne pas utiliser tel quel en production.

## Tests

    pytest -v tests/

Couvre : authentification réussie/échouée, accès /predict refusé sans token ou avec token invalide/mal formé, prédiction valide avec token correct, rejet des données d'entrée invalides.

## Performances du modèle

| Métrique | Valeur |
|---|---|
| R² | ~0.82 |
| RMSE | ~0.06 |
| MAE | ~0.04 |

Modèle : LinearRegression (scikit-learn), entraîné sur un split 80/20.

## Endpoints de l'API

| Méthode | Route | Auth requise | Description |
|---|---|---|---|
| POST | /login | Non | Authentification, retourne un JWT |
| POST | /predict | Oui (Bearer token) | Prédiction de la chance d'admission |

## Architecture BentoML

Le service est composé de deux classes avec bentoml.depends :

- AdmissionModelService : charge le modèle et expose predict_array
- AdmissionPredictionService : expose les routes publiques /login et /predict, délègue l'inférence à AdmissionModelService, et porte le middleware JWT

## Licence

Projet réalisé dans le cadre du module BentoML — DataScientest.# Prédiction de la Chance d'Admission — Projet BentoML

Projet MLOps de bout en bout : entraînement d'un modèle de régression, exposition via une API sécurisée par JWT, packaging avec BentoML, et conteneurisation Docker.

## Contexte

Ce projet prédit la chance d'admission d'un étudiant dans une université à partir de 7 variables :

| Variable | Description |
|---|---|
| gre_score | Score GRE (sur 340) |
| toefl_score | Score TOEFL (sur 120) |
| university_rating | Note de l'université (sur 5) |
| sop | Statement of Purpose (sur 5) |
| lor | Letter of Recommendation (sur 5) |
| cgpa | Cumulative Grade Point Average (sur 10) |
| research | Expérience de recherche (0 ou 1) |

Cible : chance_of_admit (probabilité entre 0 et 1)

## Architecture du projet

    examen_bentoml/
    ├── data/
    │   ├── raw/                    Données brutes (admission.csv)
    │   └── processed/              Données nettoyées et splitées
    ├── models/                     (non utilisé, modèle stocké dans le Model Store BentoML)
    ├── src/
    │   ├── prepare_data.py         Nettoyage + split train/test
    │   ├── train_model.py          Entraînement + évaluation + sauvegarde du modèle
    │   └── service.py              Service BentoML : API sécurisée (JWT)
    ├── tests/
    │   └── test_endpoints.py       Tests pytest de l'API
    ├── bentofile.yaml               Configuration du build Bento
    ├── requirements.txt
    └── README.md

## Stack technique

- Python 3.12
- scikit-learn — modèle de régression linéaire
- BentoML 1.4.35 — packaging, Model Store, serving
- FastAPI / Starlette — middleware ASGI pour l'authentification
- PyJWT — génération et validation des tokens
- Docker — conteneurisation
- pytest — tests automatisés

## Installation et exécution locale

### 1. Cloner et configurer l'environnement

    git clone https://github.com/<votre-login>/examen_bentoml.git
    cd examen_bentoml
    python3 -m venv .venv
    source .venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt

### 2. Récupérer les données

    curl -L -o data/raw/admission.csv https://assets-datascientest.s3.eu-west-1.amazonaws.com/MLOPS/bentoml/admission.csv

### 3. Préparer les données

    python src/prepare_data.py

Génère X_train.csv, X_test.csv, y_train.csv, y_test.csv dans data/processed/.

### 4. Entraîner le modèle

    python src/train_model.py
    bentoml models list

Affiche les métriques (R², RMSE, MAE) et enregistre le modèle dans le Model Store BentoML sous le nom admission_lr.

### 5. Lancer le service API en local

    bentoml serve src.service:AdmissionPredictionService --port 3001

Dans un second terminal, tester l'authentification et la prédiction :

    TOKEN=$(curl -s -X POST "http://127.0.0.1:3001/login" -H "Content-Type: application/json" -d '{"credentials":{"username":"user123","password":"password123"}}' | python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")
    curl -X POST "http://127.0.0.1:3001/predict" -H "Content-Type: application/json" -H "Authorization: Bearer $TOKEN" -d '{"input_data":{"gre_score":320,"toefl_score":110,"university_rating":4,"sop":4.0,"lor":4.5,"cgpa":8.9,"research":1}}'

## Packaging et conteneurisation

    bentoml build
    bentoml containerize admission_prediction_service:latest
    docker run --rm -d -p 3000:3000 --name admission_service admission_prediction_service:latest
    docker save admission_prediction_service:latest -o admission_prediction_service.tar
    docker load -i admission_prediction_service.tar

## Sécurité — Authentification JWT

- POST /login : vérifie les identifiants (user123 / password123 par défaut) et retourne un token JWT valide 1h
- POST /predict : protégé par un middleware ASGI (JWTAuthMiddleware) qui vérifie le header Authorization: Bearer avant d'autoriser l'accès

Les identifiants et la clé secrète JWT sont en dur dans service.py à des fins pédagogiques. Ne pas utiliser tel quel en production.

## Tests

    pytest -v tests/

Couvre : authentification réussie/échouée, accès /predict refusé sans token ou avec token invalide/mal formé, prédiction valide avec token correct, rejet des données d'entrée invalides.

## Performances du modèle

| Métrique | Valeur |
|---|---|
| R² | ~0.82 |
| RMSE | ~0.06 |
| MAE | ~0.04 |

Modèle : LinearRegression (scikit-learn), entraîné sur un split 80/20.

## Endpoints de l'API

| Méthode | Route | Auth requise | Description |
|---|---|---|---|
| POST | /login | Non | Authentification, retourne un JWT |
| POST | /predict | Oui (Bearer token) | Prédiction de la chance d'admission |

## Architecture BentoML

Le service est composé de deux classes avec bentoml.depends :

- AdmissionModelService : charge le modèle et expose predict_array
- AdmissionPredictionService : expose les routes publiques /login et /predict, délègue l'inférence à AdmissionModelService, et porte le middleware JWT

## Licence

Projet réalisé dans le cadre du module BentoML — DataScientest.# Prédiction de la Chance d'Admission — Projet BentoML

Projet MLOps de bout en bout : entraînement d'un modèle de régression, exposition via une API sécurisée par JWT, packaging avec BentoML, et conteneurisation Docker.

## Contexte

Ce projet prédit la chance d'admission d'un étudiant dans une université à partir de 7 variables :

| Variable | Description |
|---|---|
| gre_score | Score GRE (sur 340) |
| toefl_score | Score TOEFL (sur 120) |
| university_rating | Note de l'université (sur 5) |
| sop | Statement of Purpose (sur 5) |
| lor | Letter of Recommendation (sur 5) |
| cgpa | Cumulative Grade Point Average (sur 10) |
| research | Expérience de recherche (0 ou 1) |

Cible : chance_of_admit (probabilité entre 0 et 1)

## Architecture du projet

    examen_bentoml/
    ├── data/
    │   ├── raw/                    Données brutes (admission.csv)
    │   └── processed/              Données nettoyées et splitées
    ├── models/                     (non utilisé, modèle stocké dans le Model Store BentoML)
    ├── src/
    │   ├── prepare_data.py         Nettoyage + split train/test
    │   ├── train_model.py          Entraînement + évaluation + sauvegarde du modèle
    │   └── service.py              Service BentoML : API sécurisée (JWT)
    ├── tests/
    │   └── test_endpoints.py       Tests pytest de l'API
    ├── bentofile.yaml               Configuration du build Bento
    ├── requirements.txt
    └── README.md

## Stack technique

- Python 3.12
- scikit-learn — modèle de régression linéaire
- BentoML 1.4.35 — packaging, Model Store, serving
- FastAPI / Starlette — middleware ASGI pour l'authentification
- PyJWT — génération et validation des tokens
- Docker — conteneurisation
- pytest — tests automatisés

## Installation et exécution locale

### 1. Cloner et configurer l'environnement

    git clone https://github.com/<votre-login>/examen_bentoml.git
    cd examen_bentoml
    python3 -m venv .venv
    source .venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt

### 2. Récupérer les données

    curl -L -o data/raw/admission.csv https://assets-datascientest.s3.eu-west-1.amazonaws.com/MLOPS/bentoml/admission.csv

### 3. Préparer les données

    python src/prepare_data.py

Génère X_train.csv, X_test.csv, y_train.csv, y_test.csv dans data/processed/.

### 4. Entraîner le modèle

    python src/train_model.py
    bentoml models list

Affiche les métriques (R², RMSE, MAE) et enregistre le modèle dans le Model Store BentoML sous le nom admission_lr.

### 5. Lancer le service API en local

    bentoml serve src.service:AdmissionPredictionService --port 3001

Dans un second terminal, tester l'authentification et la prédiction :

    TOKEN=$(curl -s -X POST "http://127.0.0.1:3001/login" -H "Content-Type: application/json" -d '{"credentials":{"username":"user123","password":"password123"}}' | python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")
    curl -X POST "http://127.0.0.1:3001/predict" -H "Content-Type: application/json" -H "Authorization: Bearer $TOKEN" -d '{"input_data":{"gre_score":320,"toefl_score":110,"university_rating":4,"sop":4.0,"lor":4.5,"cgpa":8.9,"research":1}}'

## Packaging et conteneurisation

    bentoml build
    bentoml containerize admission_prediction_service:latest
    docker run --rm -d -p 3000:3000 --name admission_service admission_prediction_service:latest
    docker save admission_prediction_service:latest -o admission_prediction_service.tar
    docker load -i admission_prediction_service.tar

## Sécurité — Authentification JWT

- POST /login : vérifie les identifiants (user123 / password123 par défaut) et retourne un token JWT valide 1h
- POST /predict : protégé par un middleware ASGI (JWTAuthMiddleware) qui vérifie le header Authorization: Bearer avant d'autoriser l'accès

Les identifiants et la clé secrète JWT sont en dur dans service.py à des fins pédagogiques. Ne pas utiliser tel quel en production.

## Tests

    pytest -v tests/

Couvre : authentification réussie/échouée, accès /predict refusé sans token ou avec token invalide/mal formé, prédiction valide avec token correct, rejet des données d'entrée invalides.

## Performances du modèle

| Métrique | Valeur |
|---|---|
| R² | ~0.82 |
| RMSE | ~0.06 |
| MAE | ~0.04 |

Modèle : LinearRegression (scikit-learn), entraîné sur un split 80/20.

## Endpoints de l'API

| Méthode | Route | Auth requise | Description |
|---|---|---|---|
| POST | /login | Non | Authentification, retourne un JWT |
| POST | /predict | Oui (Bearer token) | Prédiction de la chance d'admission |

## Architecture BentoML

Le service est composé de deux classes avec bentoml.depends :

- AdmissionModelService : charge le modèle et expose predict_array
- AdmissionPredictionService : expose les routes publiques /login et /predict, délègue l'inférence à AdmissionModelService, et porte le middleware JWT

## Licence

Projet réalisé dans le cadre du module BentoML — DataScientest.# Prédiction de la Chance d'Admission — Projet BentoML

Projet MLOps de bout en bout : entraînement d'un modèle de régression, exposition via une API sécurisée par JWT, packaging avec BentoML, et conteneurisation Docker.

## Contexte

Ce projet prédit la chance d'admission d'un étudiant dans une université à partir de 7 variables :

| Variable | Description |
|---|---|
| gre_score | Score GRE (sur 340) |
| toefl_score | Score TOEFL (sur 120) |
| university_rating | Note de l'université (sur 5) |
| sop | Statement of Purpose (sur 5) |
| lor | Letter of Recommendation (sur 5) |
| cgpa | Cumulative Grade Point Average (sur 10) |
| research | Expérience de recherche (0 ou 1) |

Cible : chance_of_admit (probabilité entre 0 et 1)

## Architecture du projet

    examen_bentoml/
    ├── data/
    │   ├── raw/                    Données brutes (admission.csv)
    │   └── processed/              Données nettoyées et splitées
    ├── models/                     (non utilisé, modèle stocké dans le Model Store BentoML)
    ├── src/
    │   ├── prepare_data.py         Nettoyage + split train/test
    │   ├── train_model.py          Entraînement + évaluation + sauvegarde du modèle
    │   └── service.py              Service BentoML : API sécurisée (JWT)
    ├── tests/
    │   └── test_endpoints.py       Tests pytest de l'API
    ├── bentofile.yaml               Configuration du build Bento
    ├── requirements.txt
    └── README.md

## Stack technique

- Python 3.12
- scikit-learn — modèle de régression linéaire
- BentoML 1.4.35 — packaging, Model Store, serving
- FastAPI / Starlette — middleware ASGI pour l'authentification
- PyJWT — génération et validation des tokens
- Docker — conteneurisation
- pytest — tests automatisés

## Installation et exécution locale

### 1. Cloner et configurer l'environnement

    git clone https://github.com/<votre-login>/examen_bentoml.git
    cd examen_bentoml
    python3 -m venv .venv
    source .venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt

### 2. Récupérer les données

    curl -L -o data/raw/admission.csv https://assets-datascientest.s3.eu-west-1.amazonaws.com/MLOPS/bentoml/admission.csv

### 3. Préparer les données

    python src/prepare_data.py

Génère X_train.csv, X_test.csv, y_train.csv, y_test.csv dans data/processed/.

### 4. Entraîner le modèle

    python src/train_model.py
    bentoml models list

Affiche les métriques (R², RMSE, MAE) et enregistre le modèle dans le Model Store BentoML sous le nom admission_lr.

### 5. Lancer le service API en local

    bentoml serve src.service:AdmissionPredictionService --port 3001

Dans un second terminal, tester l'authentification et la prédiction :

    TOKEN=$(curl -s -X POST "http://127.0.0.1:3001/login" -H "Content-Type: application/json" -d '{"credentials":{"username":"user123","password":"password123"}}' | python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")
    curl -X POST "http://127.0.0.1:3001/predict" -H "Content-Type: application/json" -H "Authorization: Bearer $TOKEN" -d '{"input_data":{"gre_score":320,"toefl_score":110,"university_rating":4,"sop":4.0,"lor":4.5,"cgpa":8.9,"research":1}}'

## Packaging et conteneurisation

    bentoml build
    bentoml containerize admission_prediction_service:latest
    docker run --rm -d -p 3000:3000 --name admission_service admission_prediction_service:latest
    docker save admission_prediction_service:latest -o admission_prediction_service.tar
    docker load -i admission_prediction_service.tar

## Sécurité — Authentification JWT

- POST /login : vérifie les identifiants (user123 / password123 par défaut) et retourne un token JWT valide 1h
- POST /predict : protégé par un middleware ASGI (JWTAuthMiddleware) qui vérifie le header Authorization: Bearer avant d'autoriser l'accès

Les identifiants et la clé secrète JWT sont en dur dans service.py à des fins pédagogiques. Ne pas utiliser tel quel en production.

## Tests

    pytest -v tests/

Couvre : authentification réussie/échouée, accès /predict refusé sans token ou avec token invalide/mal formé, prédiction valide avec token correct, rejet des données d'entrée invalides.

## Performances du modèle

| Métrique | Valeur |
|---|---|
| R² | ~0.82 |
| RMSE | ~0.06 |
| MAE | ~0.04 |

Modèle : LinearRegression (scikit-learn), entraîné sur un split 80/20.

## Endpoints de l'API

| Méthode | Route | Auth requise | Description |
|---|---|---|---|
| POST | /login | Non | Authentification, retourne un JWT |
| POST | /predict | Oui (Bearer token) | Prédiction de la chance d'admission |

## Architecture BentoML

Le service est composé de deux classes avec bentoml.depends :

- AdmissionModelService : charge le modèle et expose predict_array
- AdmissionPredictionService : expose les routes publiques /login et /predict, délègue l'inférence à AdmissionModelService, et porte le middleware JWT

## Licence

Projet réalisé dans le cadre du module BentoML — DataScientest.# Prédiction de la Chance d'Admission — Projet BentoML

Projet MLOps de bout en bout : entraînement d'un modèle de régression, exposition via une API sécurisée par JWT, packaging avec BentoML, et conteneurisation Docker.

## Contexte

Ce projet prédit la chance d'admission d'un étudiant dans une université à partir de 7 variables :

| Variable | Description |
|---|---|
| gre_score | Score GRE (sur 340) |
| toefl_score | Score TOEFL (sur 120) |
| university_rating | Note de l'université (sur 5) |
| sop | Statement of Purpose (sur 5) |
| lor | Letter of Recommendation (sur 5) |
| cgpa | Cumulative Grade Point Average (sur 10) |
| research | Expérience de recherche (0 ou 1) |

Cible : chance_of_admit (probabilité entre 0 et 1)

## Architecture du projet

    examen_bentoml/
    ├── data/
    │   ├── raw/                    Données brutes (admission.csv)
    │   └── processed/              Données nettoyées et splitées
    ├── models/                     (non utilisé, modèle stocké dans le Model Store BentoML)
    ├── src/
    │   ├── prepare_data.py         Nettoyage + split train/test
    │   ├── train_model.py          Entraînement + évaluation + sauvegarde du modèle
    │   └── service.py              Service BentoML : API sécurisée (JWT)
    ├── tests/
    │   └── test_endpoints.py       Tests pytest de l'API
    ├── bentofile.yaml               Configuration du build Bento
    ├── requirements.txt
    └── README.md

## Stack technique

- Python 3.12
- scikit-learn — modèle de régression linéaire
- BentoML 1.4.35 — packaging, Model Store, serving
- FastAPI / Starlette — middleware ASGI pour l'authentification
- PyJWT — génération et validation des tokens
- Docker — conteneurisation
- pytest — tests automatisés

## Installation et exécution locale

### 1. Cloner et configurer l'environnement

    git clone https://github.com/<votre-login>/examen_bentoml.git
    cd examen_bentoml
    python3 -m venv .venv
    source .venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt

### 2. Récupérer les données

    curl -L -o data/raw/admission.csv https://assets-datascientest.s3.eu-west-1.amazonaws.com/MLOPS/bentoml/admission.csv

### 3. Préparer les données

    python src/prepare_data.py

Génère X_train.csv, X_test.csv, y_train.csv, y_test.csv dans data/processed/.

### 4. Entraîner le modèle

    python src/train_model.py
    bentoml models list

Affiche les métriques (R², RMSE, MAE) et enregistre le modèle dans le Model Store BentoML sous le nom admission_lr.

### 5. Lancer le service API en local

    bentoml serve src.service:AdmissionPredictionService --port 3001

Dans un second terminal, tester l'authentification et la prédiction :

    TOKEN=$(curl -s -X POST "http://127.0.0.1:3001/login" -H "Content-Type: application/json" -d '{"credentials":{"username":"user123","password":"password123"}}' | python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")
    curl -X POST "http://127.0.0.1:3001/predict" -H "Content-Type: application/json" -H "Authorization: Bearer $TOKEN" -d '{"input_data":{"gre_score":320,"toefl_score":110,"university_rating":4,"sop":4.0,"lor":4.5,"cgpa":8.9,"research":1}}'

## Packaging et conteneurisation

    bentoml build
    bentoml containerize admission_prediction_service:latest
    docker run --rm -d -p 3000:3000 --name admission_service admission_prediction_service:latest
    docker save admission_prediction_service:latest -o admission_prediction_service.tar
    docker load -i admission_prediction_service.tar

## Sécurité — Authentification JWT

- POST /login : vérifie les identifiants (user123 / password123 par défaut) et retourne un token JWT valide 1h
- POST /predict : protégé par un middleware ASGI (JWTAuthMiddleware) qui vérifie le header Authorization: Bearer avant d'autoriser l'accès

Les identifiants et la clé secrète JWT sont en dur dans service.py à des fins pédagogiques. Ne pas utiliser tel quel en production.

## Tests

    pytest -v tests/

Couvre : authentification réussie/échouée, accès /predict refusé sans token ou avec token invalide/mal formé, prédiction valide avec token correct, rejet des données d'entrée invalides.

## Performances du modèle

| Métrique | Valeur |
|---|---|
| R² | ~0.82 |
| RMSE | ~0.06 |
| MAE | ~0.04 |

Modèle : LinearRegression (scikit-learn), entraîné sur un split 80/20.

## Endpoints de l'API

| Méthode | Route | Auth requise | Description |
|---|---|---|---|
| POST | /login | Non | Authentification, retourne un JWT |
| POST | /predict | Oui (Bearer token) | Prédiction de la chance d'admission |

## Architecture BentoML

Le service est composé de deux classes avec bentoml.depends :

- AdmissionModelService : charge le modèle et expose predict_array
- AdmissionPredictionService : expose les routes publiques /login et /predict, délègue l'inférence à AdmissionModelService, et porte le middleware JWT

## Licence

Projet réalisé dans le cadre du module BentoML — DataScientest.
