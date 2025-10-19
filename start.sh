#!/bin/bash
APP_DIR="app"

# Roda o Uvicorn na porta 8000
uvicorn app.main:app
