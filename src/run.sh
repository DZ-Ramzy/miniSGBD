#!/bin/bash

MAIN_FILE="main.py"

if [ ! -f "$MAIN_FILE" ]; then
    echo "Erreur : le fichier $MAIN_FILE n'existe pas."
    exit 1
fi

# Exécution du programme Python
echo "Lancement de l'application..."
python3 "$MAIN_FILE"

# Vérifier si l'exécution s'est bien passée
if [ $? -eq 0 ]; then
    echo "Application lancée avec succès."
else
    echo "Erreur lors de l'exécution de l'application."
    exit 1
fi
