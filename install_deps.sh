#!/bin/bash

# Use poetry to manage the virtual environment and dependencies

# Activate the poetry shell if it's not already active
if ! poetry env info > /dev/null 2>&1; then
  echo "Activating poetry shell..."
  poetry shell
fi

# Install dependencies using poetry
echo "Installing dependencies using poetry..."
poetry install
