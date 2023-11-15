from fastapi import FastAPI
from langserve import add_routes
from astradb_entomology_rag import chain as astradb_entomology_rag_chain

app = FastAPI()

add_routes(app, astradb_entomology_rag_chain, path="/rag-astradb")
