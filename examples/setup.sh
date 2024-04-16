#!/bin/bash
python -m venv venv
if [ -e "venv/bin" ]; then
    venv/bin/python -m pip install -e ..[openai]
    venv/bin/python -m pip install jupyter jupyterlab ipykernel
else
    venv/Scripts/python -m pip install -e ..[openai]
    venv/Scripts/python -m pip install jupyter jupyterlab ipykernel
fi
touch .env
echo "Input your OpenAI API key in the .env file"
