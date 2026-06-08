#!/bin/sh
# Démarre le serveur Ollama, télécharge le micro-LLM, puis pose un marqueur
# de disponibilité utilisé par le healthcheck docker-compose.
set -e

ollama serve &
SERVE_PID=$!

echo "[ollama] attente du démarrage du serveur..."
until ollama list >/dev/null 2>&1; do
  sleep 1
done

MODEL="${LLM_CTF_MODEL:-qwen2.5:3b}"
echo "[ollama] pull du modèle ${MODEL} (peut prendre quelques minutes la première fois)..."
ollama pull "${MODEL}"

EMBED_MODEL="${LLM_CTF_EMBED_MODEL:-all-minilm}"
echo "[ollama] pull du modèle d'embedding ${EMBED_MODEL}..."
ollama pull "${EMBED_MODEL}"

echo "[ollama] modèles prêts."
touch /tmp/model-ready

wait "${SERVE_PID}"
