# Service de Prédiction d'Admission — BentoML

## Contenu de l'archive

- `admission_prediction_service.tar` : image Docker du service (contient le modèle et l'API)
- `requirements.txt` : dépendances Python nécessaires pour exécuter les tests
- `tests/` : tests unitaires pytest
- `README.md` : ce fichier

## 1. Charger l'image Docker

```bash
docker load -i admission_prediction_service.tar
```

## 2. Lancer le service

```bash
docker run --rm -d -p 3000:3000 --name admission_service admission_prediction_service:latest
```

Le service est accessible sur `http://localhost:3000`.

Vérifier qu'il est bien démarré :

```bash
docker logs admission_service
```

## 3. Installer les dépendances pour les tests

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 4. Lancer les tests

```bash
pytest -v tests/
```

## 5. Arrêter le service

```bash
docker stop admission_service
```

## Endpoints de l'API

- `POST /login` : authentification, retourne un token JWT
  - Body : `{"credentials": {"username": "user123", "password": "password123"}}`
- `POST /predict` : prédiction (nécessite un token JWT valide dans le header `Authorization: Bearer <token>`)
  - Body : `{"input_data": {"gre_score": 320, "toefl_score": 110, "university_rating": 4, "sop": 4.0, "lor": 4.5, "cgpa": 8.9, "research": 1}}`
