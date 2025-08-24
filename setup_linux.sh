#!/bin/bash

echo "========================================"
echo "     SETUP DO PROJETO CONNECT_SYNC"
echo "========================================"
echo

echo "[1/6] Criando virtual environment..."
python3 -m venv .venv

echo "[2/6] Ativando virtual environment..."
source .venv/bin/activate

echo "[3/6] Instalando dependências..."
pip install -r requirements.txt

echo "[4/6] Aplicando migrações..."
python manage.py migrate

echo "[5/6] Criando superusuário..."
echo "Por favor, crie seu superusuário:"
python manage.py createsuperuser

echo "[6/6] Iniciando servidor..."
echo
echo "========================================"
echo "     SETUP CONCLUÍDO COM SUCESSO!"
echo "========================================"
echo
echo "Para acessar o admin: http://127.0.0.1:8000/admin/"
echo
python manage.py runserver
