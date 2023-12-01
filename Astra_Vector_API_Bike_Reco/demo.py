import os, json
from dotenv import load_dotenv, find_dotenv
from astrapy.db import AstraDB
from openai import OpenAI

# Load the .env file
if not load_dotenv(find_dotenv(),override=True):
    raise Exception("Couldn't load .env file")

#declare constant
ASTRA_DB_API_ENDPOINT=os.getenv('ASTRA_DB_API_ENDPOINT')
ASTRA_DB_APPLICATION_TOKEN=os.getenv('ASTRA_DB_TOKEN')
ASTRA_NAMESPACE=os.getenv('ASTRA_NAMESPACE')
ASTRA_COLLECTION=os.getenv('ASTRA_COLLECTION')
model_id = "text-embedding-ada-002"

client = OpenAI(
  api_key=os.getenv('OPENAI_API_KEY')
)


def create_collection(astra_db_api_endpoint,astra_db_token, astra_namespace,astra_create_collection):
    #Establish Connectivity
    astra_db = AstraDB(
    api_endpoint=astra_db_api_endpoint,
    token=astra_db_token,
    namespace=astra_namespace
    )
    astra_collection_obj = astra_db.collection(astra_create_collection)
    return astra_collection_obj

def embed_query(customer_input):
    # Create embedding based on same model
    embedding = client.embeddings.create(input= customer_input, model=model_id).data[0].embedding
    return embedding

def execute_simple_query(customer_input, astra_collection_obj, k):
    embedding = embed_query(customer_input)
    bike_results = astra_collection_obj.vector_find(embedding, limit=k, fields=["model", "brand", "price", "type", "image", "description"])
    return bike_results

def execute_hybrid_query(customer_input, astra_collection_obj, metadata_filter, k):
    embedding = embed_query(customer_input)
    bike_results = astra_collection_obj.vector_find(embedding,limit=k,filter={"type": metadata_filter}, fields=["model", "brand", "price", "type", "image", "description"])
    return bike_results

def ask_user_query_mode(option1, option2):
   print("Please choose between the following options:")
   print(f"1. {option1}")
   print(f"2. {option2}")
   
   user_choice = input("Enter your choice (1 or 2): ")
   # Check the user's input and execute the appropriate code.
   if user_choice == "1":
       return option1
   elif user_choice == "2":
       return option2
   else:
    print("Invalid choice. Please enter 1 or 2.")
    return ask_user_query_mode(option1, option2)

def execute_demo():
    astra_collection_obj = create_collection(ASTRA_DB_API_ENDPOINT,ASTRA_DB_APPLICATION_TOKEN,ASTRA_NAMESPACE,ASTRA_COLLECTION)
    query = input("Please Enter your Bike Question: ")
    k = input("Please Enter Number of Results: ")
    query_mode = ask_user_query_mode("simple", "hybrid")

    if(query_mode == "hybrid"):
        filter = input("Please Enter Bike Type: (e.g. Kids bikes or eBikes)")
        bikes_results = execute_hybrid_query(query, astra_collection_obj, filter, k)
    else:
        bikes_results = execute_simple_query(query, astra_collection_obj, k)

    if len(bikes_results) > 0:
        print(json.dumps(bikes_results,indent=2))
    else:
        print("No Recommendations Found")

execute_demo()