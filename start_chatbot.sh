#!/bin/bash

echo "Starting BuiltByRAVE CFO OS Chatbot..."
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

# Check if requirements.txt exists
if [ ! -f "rag-backend/requirements.txt" ]; then
    echo "ERROR: requirements.txt not found"
    exit 1
fi

# Install requirements
echo "Installing Python requirements..."
python3 -m pip install -r rag-backend/requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install requirements"
    exit 1
fi

# Start the chatbot
echo "Starting chatbot..."
cd rag-backend
python3 chatbot.py