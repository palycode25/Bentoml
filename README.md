
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

```bash
git clone https://github.com/<votre-login>/examen_bentoml.git
cd examen_bentoml

python3 -m venv .venv
source .venv/bin/activate   # Windows : .venv\Scripts\activate

pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Récupérer les données

```bash
curl -L -o data/raw/admission.csv \
  https://assets-datascientest.s3.eu-west-1.amazonaws.com/MLOPS/bentoml/admission.csv
```

### 3. Préparer les données

```bash
python src/prepare_data.py
```

Génère X_train.csv, X_test.csv, y_train.csv, y_test.csv dans data/processed/.

### 4. Entraîner le modèle

```bash
python src/train_model.py
```

Affiche les métriques (R², RMSE, MAE) et enregistre le modèle dans le Model Store BentoML sous le nom admission_lr.

Vérifier l'enregistrement :

```bash
bentoml models list
```

### 5. Lancer le service API en local

```bash
bentoml serve src.service:AdmissionPredictionService --port 3001
```

Dans un second terminal, tester l'authentification et la prédiction :

```bash
TOKEN=$(curl -s -X POST "http://127.0.0.1:3001/login" \
  -H "Content-Type: application/json" \
  -d '{"credentials":{"username":"user123","password":"password123"}}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")

curl -X POST "http://127.0.0.1:3001/predict" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"input_data":{"gre_score":320,"toefl_score":110,"university_rating":4,"sop":4.0,"lor":4.5,"cgpa":8.9,"research":1}}'
```

## Packaging et conteneurisation

### Construire le Bento

```bash
bentoml build
```

### Conteneuriser avec Docker

```bash
bentoml containerize admission_prediction_service:latest
```

### Lancer le conteneur

```bash
docker run --rm -d -p 3000:3000 --name admission_service admission_prediction_service:latest
```

### Exporter l'image

```bash
docker save admission_prediction_service:latest -o admission_prediction_service.tar
```

Recharger ailleurs :

```bash
docker load -i admission_prediction_service.tar
```

## Sécurité — Authentification JWT

- POST /login : vérifie les identifiants (user123 / password123 par défaut) et retourne un token JWT valide 1h
- POST /predict : protégé par un middleware ASGI (JWTAuthMiddleware) qui vérifie le header Authorization: Bearer <token> avant d'autoriser l'accès

Les identifiants et la clé secrète JWT sont en dur dans service.py à des fins pédagogiques. Ne pas utiliser tel quel en production — utiliser des variables d'environnement et une base d'utilisateurs réelle.

## Tests

```bash
pytest -v tests/
```

Couvre :
- Authentification réussie / échouée
- Accès /predict refusé sans token, avec token invalide ou mal formé
- Prédiction valide avec token correct
- Rejet des données d'entrée invalides

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

Cette séparation permet de faire évoluer la logique API et la logique d'inférence indépendamment.

## Licence

Projet réalisé dans le cadre du module BentoML — DataScientest.
