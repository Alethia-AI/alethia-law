# Privocia-APIs
The core restful APIs for Retrieval Orchestration for Privocia.

## Setup

### Create a virtual environment:

```
python3 -m venv .venv
source .venv/bin/activate
export PYTHONPATH=$PWD
```

### Install Requirements:

`pip install -r requirements.txt`

### Setup environment variables:

```
cd app
touch .env
```

#### Add the following to the `.env` file:

```
SUPABASE_URL = supabase_url
SUPABASE_API_KEY = supabase_api_key
```

### Run the server:

```
cd ..
python run.py
```

### Open your browser and go to:

`http://0.0.0.0:8080/docs`
