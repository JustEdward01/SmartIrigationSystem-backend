#!/bin/sh
# Setup local dev environment

if [ ! -f .env ]; then
    cp .env.example .env
fi

python -m pip install -r requirements.txt
