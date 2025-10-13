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


try:
        # Execute query
        items = list(container.query_items(
            query=query,
            parameters=parameters,
            enable_cross_partition_query=True
        ))
        
        # Create list of dictionaries with required keys
        result = [
            {
                "con_id": item.get("con_id"),
                "title": item.get("title"),
                "createdAt": item.get("createdAt")
            }
            for item in items
        ]
        
        return result
        
    except exceptions.CosmosHttpResponseError as e:
        print(f"An error occurred: {e.message}")
        return []
