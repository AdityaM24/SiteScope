#!/usr/bin/env bash
# One-shot build for Render (or any Python+Node host).
set -euo pipefail

echo "▶ Installing backend dependencies..."
pip install --no-cache-dir -r backend/requirements.txt

echo "▶ Building frontend..."
cd frontend
npm install
npm run build
cd ..

echo "✅ Build complete."
