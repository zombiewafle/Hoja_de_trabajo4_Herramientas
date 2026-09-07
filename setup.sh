#!/bin/bash

python3 -m venv .venv

source .venv/bin/activate

python -m pip install --upgrade pip

pip install -r requirements.txt

echo "Entorno configurado correctamente."
echo "Para activarlo:"
echo "source .venv/bin/activate"