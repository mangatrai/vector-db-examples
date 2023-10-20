from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from cassandra.query import dict_factory, SimpleStatement
import openai, os, uuid, time, requests, traceback
from traceloop.sdk import Traceloop
from traceloop.sdk.tracing import tracing as Tracer
from traceloop.sdk.decorators import workflow, task, agent
from dotenv import load_dotenv, find_dotenv
import pandas as pd
import streamlit as st

# Load the .env file
if not load_dotenv(find_dotenv(),override=True):
    raise Exception("Couldn't load .env file")

#Add Telemetry
TRACELOOP_API_KEY=os.getenv('TRACELOOP_API_KEY')
Traceloop.init(app_name="Bike Recommendation App", disable_batch=True)
# Generate a UUID
uuid_obj = str(uuid.uuid4())
Tracer.set_correlation_id(uuid_obj)

#declare constant
ASTRA_DB_SECURE_BUNDLE_PATH=os.getenv('ASTRA_SECUREBUNDLE_PATH')
ASTRA_DB_APPLICATION_TOKEN=os.getenv('ASTRA_DB_TOKEN')
ASTRA_DB_KEYSPACE=os.getenv('ASTRA_KEYSPACE')
k=os.getenv('LIMIT_TOP_K')
openai.api_key = os.getenv('OPENAI_API_KEY')
model_id = "text-embedding-ada-002"

@task(name="Create Cassandra Connection")
def create_connection():
    #Establish Connectivity
    st.write(":hourglass: Establishing AstraDB Connection...")
    cluster = Cluster(
    cloud={
        "secure_connect_bundle": ASTRA_DB_SECURE_BUNDLE_PATH,
    },
    auth_provider=PlainTextAuthProvider(
        "token",
        ASTRA_DB_APPLICATION_TOKEN,
    ),
    )
    session = cluster.connect()
    keyspace = ASTRA_DB_KEYSPACE
    return session, keyspace

@task(name="Embed Input Query")
def embed_query(customer_input):
    # Create embedding based on same model
    st.write(":hourglass: Using OpenAI to Create Embeddings for Input Query...")
    embedding = openai.Embedding.create(input=customer_input, model=model_id)['data'][0]['embedding']
    return embedding

@task(name="Build top k simple query")
def build_simple_query(customer_input, keyspace, k):
    st.write(":hourglass: Building Simple Database Query...")
    embedding = embed_query(customer_input)
    query = SimpleStatement(
    f"""
    SELECT *
    FROM {keyspace}.bikes
    ORDER BY description_embedding ANN OF {embedding} LIMIT {k};
    """
    )
    return query

@task(name="Build top k hybrid query")
def build_hybrid_query(customer_input, keyspace, filter, k):
    st.write(":hourglass: Building Hybrid Search Query...")
    embedding = embed_query(customer_input)
    hybrid_query = SimpleStatement(
    f"""
    SELECT *
    FROM {keyspace}.bikes
    WHERE type : '{filter}'
    ORDER BY description_embedding ANN OF {embedding} LIMIT {k};
    """
    )
    return hybrid_query

@task(name="Perform ANN search on Astra DB")
def query_astra_db(session, query):
    st.write(":hourglass: Retrieving results from Astra DB...")
    results = session.execute(query)
    top_results = results._current_rows
    bikes_results = pd.DataFrame(top_results)
    return bikes_results

@workflow(name="Bike Recommendation Demo UI")
def execute_demo_ui():
    ##################################
    st.title('🚲 Bike Recommendation Engine')
    st.write("These Bike Recommendations are based on sample dataset.")
    with st.expander('**Scenario Details**'):
        st.write("""
    The Bike Review and Descriptions have been embedded using [OpenAI's Text Embedding API](https://beta.openai.com/docs/api-reference/text-embeddings),
    and stored in DataStax Astra.

    Based on the bike recommendation asked, this demo will:

    1. Search the vector database for the best bike matches, using these reviews and descrition;
    2. User have the ability to further instruct on what type of bike;

    """)

    query = st.text_input('Please Enter your Bike Question:')
    filter = st.text_input("Please Enter Bike Type: (e.g. Kids Bike or eBikes) ***Optional***")

    if st.button('Ask Me! :bicyclist:'):
        if query:
            if filter:
                session, keyspace = create_connection()
                db_query = build_hybrid_query(query, keyspace, filter, k)
                bikes_results = query_astra_db(session, db_query)
                if bikes_results.notnull:
                    st.write(bikes_results)
            else:
                session, keyspace = create_connection()
                db_query = build_simple_query(query, keyspace, k)
                bikes_results = query_astra_db(session, db_query)
                if bikes_results.notnull:
                    st.write(bikes_results)
        else:
            st.error("Please provide a question to start!")

#call main method
execute_demo_ui()