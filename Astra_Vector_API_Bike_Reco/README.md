## Converted Bike Reco Engine Demo to use vector API

# Bike Recommendation Engine
Uses a small set of bike review/description to generate bike recommendations.

## Setup
- Create .env file with following values
```sh
OPENAI_API_KEY=""
ASTRA_DB_TOKEN=""
ASTRA_NAMESPACE=""
ASTRA_COLLECTION=""
LIMIT_TOP_K=""
ASTRA_DB_API_ENDPOINT=""
REVIEWS_FILE_URL=""
```
Namespace is keyspace and reviews file is the data which needs to be embedded

## Load data
```sh
python load_embeddings.py
```
## Run demo from command line
```sh
python demo.py
```
## Launch UI
This app uses streamlit to run UI
```sh
streamlit run demo-ui.py
```


