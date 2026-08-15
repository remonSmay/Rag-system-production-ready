# mini-rag-app
This is a minimal implementation of the RAG model for question answering.

## Requirements

- Python 3.12.2 or later

### Install Python using Miniconda

1. Download and install Miniconda from [here](https://www.anaconda.com/docs/getting-started/miniconda/install).
2. Create a new environment using the following command:
    ```bash
    $ conda create -n mini-rag python=3.11
    ```
3. Activate the environment:
    ```bash
    $ conda activate mini-rag
    ```
## Installatin 
### install the required packags :
```bash
$ python -m pip install -r requirements.txt
```
### setup the environment variables :
 ```bash
 cp .env.example .env
```
set your envirement variavles in the `.env` file. Like `OPENAI_API_KEY` value.

## Run the FastApi server 
```bash
$ uvicorn main:app --reload --host 0.0.0.0 --port 5000
```
## POSTMAN Collection

Downlaod the POSTMAN collection form [/assets/mini-rag-app.postman_collection.json](/mini-rag-app/assets/mini-rag-app.postman_collection.json)