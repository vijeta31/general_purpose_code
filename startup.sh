#!/bin/bash
set -e

echo "Installing uv..."
curl -LsSf https://astral.sh/uv/install.sh | sh

echo "Setting up PATH..."
export PATH="$HOME/.cargo/bin:$PATH"

echo "Verifying uv installation..."
which uv
uv --version

echo "Starting FastAPI application..."
uv run fastapi run --host 0.0.0.0 --port ${PORT:-8000}


curl -LsSf https://astral.sh/uv/install.sh | sh && source $HOME/.cargo/env && uv run fastapi run --host 0.0.0.0 --port ${PORT:-8000}

curl -LsSf https://astral.sh/uv/install.sh | sh && . $HOME/.local/bin/env && uv run fastapi run app.main:app --host 0.0.0.0 --port ${PORT:-8000}

curl -LsSf https://astral.sh/uv/install.sh | sh && export PATH="/root/.local/bin:$PATH" && uv run fastapi run app.main:app --host 0.0.0.0 --port ${PORT:-8000}

curl -LsSf https://astral.sh/uv/install.sh | sh && export PATH="/root/.local/bin:$PATH" && cd /home/site/wwwroot && uv run fastapi run app.main:app --host 0.0.0.0 --port ${PORT:-8000}

curl -LsSf https://astral.sh/uv/install.sh | sh && export PATH="/root/.local/bin:$PATH" && cd /home/site/wwwroot && uv run uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}

curl -LsSf https://astral.sh/uv/install.sh | sh && export PATH="/root/.local/bin:$PATH" && cd /home/site/wwwroot/app && uv run fastapi run main.py --host 0.0.0.0 --port ${PORT:-8000}

curl -LsSf https://astral.sh/uv/install.sh | sh && export PATH="/root/.local/bin:$PATH" && cd /home/site/wwwroot && uv run uvicorn app.main:app --host 0.0.0.0 --port 8000

curl -LsSf https://astral.sh/uv/install.sh | sh && export PATH="/root/.local/bin:$PATH" && cd /home/site/wwwroot && export PYTHONPATH=/home/site/wwwroot && uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
