#!/bin/bash

# Verifica que se ha pasado una descripción
if [ -z "$1" ]; then
  echo "❌ Error: Debes proporcionar una descripción para el commit."
  echo "Uso: ./gitpush.sh \"mensaje del commit\""
  exit 1
fi

# Añade todos los cambios
git add .

# Crea commit con el mensaje dado
git commit -m "$1"

# Hace push a la rama actual
git push