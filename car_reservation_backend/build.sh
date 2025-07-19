#!/bin/bash

# Build script pro render.com

echo "Spouštím build proces..."

# Instalace Python závislostí
echo "Instaluji Python závislosti..."
pip install -r requirements.txt

# Příprava statické složky
echo "Připravuji statickou složku..."
mkdir -p src/static

# Pokud existuje frontend, zkusíme ho buildnout
if [ -d "../car_reservation_frontend" ]; then
    echo "Nalezen frontend, spouštím build..."
    cd ../car_reservation_frontend
    
    # Instalace Node.js závislostí s legacy peer deps
    echo "Instaluji Node.js závislosti..."
    npm install --legacy-peer-deps
    
    # Build frontendu
    echo "Buildím frontend..."
    npm run build
    
    # Kopírování do backend static složky
    if [ -d "dist" ]; then
        echo "Kopíruji frontend do backend static složky..."
        cp -r dist/* ../car_reservation_backend/src/static/
    else
        echo "Frontend build se nezdařil, pokračuji bez frontendu..."
    fi
    
    cd ../car_reservation_backend
else
    echo "Frontend nenalezen, pokračuji pouze s backend API..."
fi

echo "Build dokončen!"

