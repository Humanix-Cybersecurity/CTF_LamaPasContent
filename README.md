# LLM CTF — OWASP Top 10 for LLM Applications

CTF pédagogique illustrant le **Top 10 OWASP des applications LLM (2025)**.
Entièrement conteneurisé, **100 % offline** : un micro-LLM (`qwen2.5:3b`)
tourne en CPU dans un conteneur Ollama, une application FastAPI sert les
challenges (API REST + interface web).

> ⚠️ Projet à but **éducatif**. Les vulnérabilités sont volontaires.

## Prérequis

- Docker + Docker Compose
- ~3 Go de RAM libre, ~2 Go de disque (modèle compris)

## Démarrage

```bash
docker compose up --build
```

Au premier lancement, le conteneur Ollama télécharge le modèle (~1.3 Go) ;
patientez quelques minutes. L'app attend automatiquement que le modèle soit prêt.

Puis ouvrez : **http://localhost:8000**

> ℹ️ Sans configuration, l'app démarre avec des **flags/secrets de
> démonstration** (placeholders). Pour une vraie instance, voir
> [Configuration des flags/secrets](#configuration-des-flagssecrets).

Vérifier que le LLM répond :

```bash
curl -s http://localhost:8000/api/health
```

### Choisir un autre modèle

```bash
LLM_CTF_MODEL=qwen2.5:1.5b docker compose up --build
```

## Architecture

```
┌────────────┐      HTTP       ┌─────────────┐
│  Navigateur │ ─────────────▶ │   app        │  FastAPI (UI + API)
└────────────┘                 │  :8000       │
                               └──────┬──────┘
                                      │ /api/chat
                               ┌──────▼──────┐
                               │  ollama      │  micro-LLM CPU
                               │  :11434      │
                               └─────────────┘
```

## Challenges

| Code | Titre | Statut |
|------|-------|--------|
| LLM01 | Injection de prompt directe | ✅ disponible |
| LLM02 | Divulgation d'informations sensibles | ✅ disponible |
| LLM03 | Supply Chain | ✅ disponible |
| LLM04 | Empoisonnement de données / modèle | ✅ disponible |
| LLM05 | Mauvaise gestion des sorties (injection SQL) | ✅ disponible |
| LLM06 | Agence excessive | ✅ disponible |
| LLM07 | Fuite du system prompt | ✅ disponible |
| LLM08 | Faiblesses vectorielles / embeddings | ✅ disponible |
| LLM09 | Désinformation | ✅ disponible |
| LLM10 | Consommation non maîtrisée | ✅ disponible |

> 🔒 Les **solutions détaillées** (dossier `writeups/`) et les **vraies réponses**
> (`app/ctf_secrets.json`) sont **volontairement absentes de ce dépôt public**
> pour ne pas divulguer les flags. À chacun de résoudre — ou de définir ses
> propres flags/secrets.

## Configuration des flags/secrets

Les flags `CTF{...}` et les valeurs secrètes (mots de passe, jetons, etc.) sont
**externalisés** hors du code, dans un fichier **non versionné**. Le dépôt ne
contient qu'un modèle à placeholders.

```bash
cp app/ctf_secrets.example.json app/ctf_secrets.json
# éditez app/ctf_secrets.json avec VOS propres flags et secrets
```

- Si `app/ctf_secrets.json` est absent → l'app utilise `ctf_secrets.example.json`
  (placeholders), pratique pour tester mais flags non secrets.
- `app/ctf_secrets.json` est listé dans `.gitignore` : il ne doit jamais être
  committé.

## Structure du projet

```
docker-compose.yml      # orchestration ollama + app
ollama/entrypoint.sh    # démarrage serveur + pull du modèle
app/
  main.py               # FastAPI : UI + API + scoring
  core/                 # client LLM, registre des challenges
  challenges/           # 1 module par challenge (LLMxx_*.py)
  templates/ static/    # interface web
writeups/               # solutions détaillées
```

## Note sur le déterminisme

Les micro-LLM ne sont pas 100 % déterministes, même à `temperature=0` : un même
exploit peut occasionnellement échouer puis réussir. La détection de réussite
est toujours faite **côté serveur** (jamais sur la confiance accordée au modèle).

## Ajouter un challenge

1. Créer `app/challenges/llmXX_nom.py`, sous-classe de `BaseChallenge`.
2. L'enregistrer dans `app/core/registry.py` (`_MODULES`).
3. La réussite doit être détectée **côté serveur**, jamais sur la confiance
   accordée au texte du modèle.
