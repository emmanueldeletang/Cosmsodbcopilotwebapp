import streamlit as st
import  time
import config
import json
import os
import sys
import uuid
import datetime
import glob
import time
import uuid
import csv
from dotenv import load_dotenv
from openai import AzureOpenAI
from tenacity import retry, wait_random_exponential, stop_after_attempt
from dotenv import dotenv_values
from openai import AzureOpenAI
from azure.core.exceptions import AzureError
from azure.cosmos import CosmosClient, PartitionKey
from azure.cosmos import ThroughputProperties
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import UnstructuredWordDocumentLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_experimental.text_splitter import SemanticChunker
from azure.identity import DefaultAzureCredential
from openai import AzureOpenAI
from azure.core.exceptions import AzureError
from azure.cosmos import CosmosClient, PartitionKey
from dotenv import dotenv_values
from azure.cosmos import ThroughputProperties
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import UnstructuredWordDocumentLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from tempfile import NamedTemporaryFile


load_dotenv()


env_name = "configuration.env" # following example.env template change to your own .env file name
config = dotenv_values(env_name)



# specify the name of the .env file name 
env_name = "example.env" # following example.env template change to your own .env file name
config = dotenv_values(env_name)
# Azure Cosmos DB connection details
HOST = config['cosmos_host']
key = config['cosmos_key']


container_name = "ChatMessages"


# Azure OpenAI connection details
openai_endpoint = config['openai_endpoint']
openai_key = config['openai_key']
openai_version = config['openai_version']
openai_embeddings_model = config['openai_embeddings_deployment']
openai_chat_model = config['AZURE_OPENAI_CHAT_MODEL']



dbsource = config['cosmosdbsourcedb'] 
colvector = config['cosmosdbsourcecol']
cachecol = config['cosmsodbcache']
cosmosdbcolcompletion = config['cosmosdbcolcompletion']
container_name = config['cosmosdbcolcompletion']

# Create the OpenAI client
openai_client = AzureOpenAI(
  api_key = openai_key,  
  api_version = openai_version,  
  azure_endpoint =openai_endpoint 
)



ENDPOINT =  config['cosmos_host']

client = CosmosClient(ENDPOINT, key)



def createvectordb(collection):
    
   
    mydbt = client.get_database_client(dbsource)
    
   
    
    vector_embedding_policy = { "vectorEmbeddings": [ {  "path": "/embedding",  "dataType": "float32",  "distanceFunction": "cosine",  "dimensions": 1536  } ] }
    indexing_policy = { "includedPaths": [ { "path": "/*" } ], "excludedPaths": [  {  "path": "/\"_etag\"/?" }  ], "vectorIndexes": [ {"path": "/embedding", "type": "diskANN"  }] }

    try:
        container = mydbt.create_container_if_not_exists( 
        id= collection, 
        partition_key=PartitionKey(path='/id'), 
        offer_throughput=ThroughputProperties(auto_scale_max_throughput=1000, auto_scale_increment_percent=0),
        indexing_policy=indexing_policy, 
        vector_embedding_policy=vector_embedding_policy) 
     
              
    except : 
         raise


def loaddata(db,collection, filepath) :
    
  
    mydbt = client.get_database_client(db)   
  

    try:
        container = mydbt.create_container_if_not_exists( 
        id= collection, 
        partition_key=PartitionKey(path='/id'), 
         offer_throughput=ThroughputProperties(auto_scale_max_throughput=1000, auto_scale_increment_percent=0))
        
        filename = filepath
        with open(filename,encoding="utf8") as file:
            docu = json.load(file)
            for d in docu:
                d['text']= json.dumps(d)
                container.upsert_item(d)
        
# count products
        query = "SELECT VALUE COUNT(1) FROM c"

        total_count = 0

        result = container.query_items(
            query=query,
            enable_cross_partition_query=True)

        for item in result:
            total_count += item

        print("Total count json:", total_count)
        
       
    
    except : 
     raise  
       

def loadpdffile(db,collection,name,file) :
    
   
    mydbt = client.get_database_client(db)   
    
    loader = PyPDFLoader(file)
    data = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    docs = text_splitter.split_documents(data)
    
    
   
    
    try:
        container = mydbt.create_container_if_not_exists( 
        id= collection, 
        partition_key=PartitionKey(path='/id'), 
        offer_throughput=ThroughputProperties(auto_scale_max_throughput=1000, auto_scale_increment_percent=0))
        
       
        for d in docs : 
            docu= {} 
            docu["id"] = str(uuid.uuid4())
            docu["file"] = name
            docu["text"] = str(d)
            container.upsert_item(docu)
    except : 
     raise     
# count 
    try : 
     query = "SELECT VALUE COUNT(1) FROM c"

     total_count = 0

     result = container.query_items(
     query=query,
     enable_cross_partition_query=True)

     for item in result:
        total_count += item

        print("Total count pdf :", total_count)
        
       
    
    except : 
     raise  

def generate_embeddings(openai_client, text):
    """
    Generates embeddings for a given text using the OpenAI API v1.x
    """
    
    response = openai_client.embeddings.create(
        input = text,
        model= openai_embeddings_model
    
    )
    embeddings = response.data[0].embedding
    return embeddings

def loadcsvfile(db,collection,name,file) :
    
    
    mydbt = client.get_database_client(db)   
   
    try:
        container = mydbt.create_container_if_not_exists( 
        id= collection, 
        partition_key=PartitionKey(path='/id'), 
        offer_throughput=ThroughputProperties(auto_scale_max_throughput=1000, auto_scale_increment_percent=0))
        
 
    # Read CSV file and convert to JSON
        with open(file, mode='r', encoding='utf-8-sig') as file:
         csv_reader = csv.DictReader(file)
         for row in csv_reader:
                row["id"] = str(uuid.uuid4())
                row["file"] = name
                row["text"] = json.dumps(row)
                         
                json_data = json.dumps(row)
                # Insert JSON data into Cosmos DB
                container.create_item(body=json.loads(json_data))
    
    except : 
        raise


   
# count 
    try : 
     query = "SELECT VALUE COUNT(1) FROM c"

     total_count = 0

     result = container.query_items(
     query=query,
     enable_cross_partition_query=True)

     for item in result:
        total_count += item

        print("Total count csv:", total_count)
        
       
    
    except : 
     raise  

def loadwordfile(db,collection,name,file) :
    
   
    mydbt = client.get_database_client(db)   
    
    from langchain_community.document_loaders import Docx2txtLoader

    loader = Docx2txtLoader(file)

    data = loader.load()    
    
    
    
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    docs = text_splitter.split_documents(data)
   
  
    
    try:
        container = mydbt.create_container_if_not_exists( 
        id= collection, 
        partition_key=PartitionKey(path='/id'), 
        offer_throughput=ThroughputProperties(auto_scale_max_throughput=1000, auto_scale_increment_percent=0))
        
       
        for d in docs : 
            docu= {} 
            docu["id"] = str(uuid.uuid4())
            docu["file"] = name
            docu["text"] = str(d)
            container.upsert_item(docu)
    except : 
     raise     
# count 
    try : 
     query = "SELECT VALUE COUNT(1) FROM c"

     total_count = 0

     result = container.query_items(
     query=query,
     enable_cross_partition_query=True)

     for item in result:
        total_count += item

        print("Total count word:", total_count)
        
       
    
    except : 
     raise  
       


def add_doc(openai_client, collection, doc,name):
   
    try:
        doc1 = {}
        doc1["id"] = doc["id"]
        doc1["source"]= name
        
        doc1["embedding"] = generate_embeddings(openai_client, json.dumps(doc))
        
    
        
        collection.upsert_item(doc1)
       
    except Exception as e:
        print(str(e))
       
        
        
def get_completion(openai_client, model, prompt: str):    
   
    response = openai_client.chat.completions.create(
        model = model,
        messages =   prompt,
        temperature = 0.1
    )   
    return response.model_dump()

def chat_completion(user_message):
    # Dummy implementation of chat_completion
    # Replace this with the actual implementation
    response_payload = f"Response to: {user_message}"
    cached = False
    return response_payload, cached

def get_similar_docs(openai_client, db, query_text, limit,sim):
    """ 
        Get similar documents from Cosmos DB for NoSQL 

        input: 
            container: name of the container
            query_text: user question
            limit: max number of documents to return
        output:
            documents: json documents similar to the user question
            elapsed_time
    """
    # vectorize the question
  
    mydbt = client.get_database_client(db)   
    cvector = mydbt.get_container_client(colvector)
    
   
    query_vector = generate_embeddings(openai_client, query_text)
    query = f"""
        SELECT TOP @num_results  c.id,c.source, VectorDistance(c.embedding, @embedding) as SimilarityScore 
        FROM c
        WHERE VectorDistance(c.embedding,@embedding) > @similarity_score
        ORDER BY VectorDistance(c.embedding,@embedding)
    """
    results = cvector.query_items(
        query=query,
         parameters=[
            {"name": "@embedding", "value": query_vector},
            {"name": "@num_results", "value": limit},
            {"name": "@similarity_score", "value": sim}
        ],
        enable_cross_partition_query=True, populate_query_metrics=True
    )   
    
           
    listid = []
    source = ""
    # get products from list of id
    id_list = [id for id in results]

    for i in id_list:
            listid.append(i['id'])
            source = (i['source'])
                                  
        
    if listid == []:
        products = []
    else : 
        id_list_str = ', '.join([f"'{id}'" for id in listid]) 
        
      
        mycolt = mydbt.get_container_client(source)
            
        query = f"""
                    SELECT * FROM c 
                    WHERE  c.id IN ({id_list_str})
                """
                
            
        results = mycolt.query_items(
                    query=query,
                    enable_cross_partition_query=True
        )

        products = []
        for product in results:
            products.append(product)    

    return products


def ReadFeed(collection):
        
       
        
        mydbt = client.get_database_client(dbsource)   
        mycolt = mydbt.get_container_client(collection)
        mycoltembed = mydbt.get_container_client("vector") 
        name = collection
        
     
        # Define a point in time to start reading the feed from
        time = datetime.datetime.now()
        
    
        time = time - datetime.timedelta(days=1)
       
           
        
         #response = mycolt.query_items_change_feed(start_time=time)
        response = mycolt.query_items_change_feed( )
        
        for doc in response:
            add_doc(openai_client, mycoltembed, doc,name)

def get_chat_history(  username,completions=1):
    
   
    mydbt = client.get_database_client(dbsource)   
    container = mydbt.get_container_client(cachecol)
    
    results = container.query_items(
        query= '''
        SELECT TOP @completions *
        FROM c
        where c.name = @username
        ORDER BY c._ts DESC
        ''',
        parameters=[
            {"name": "@completions", "value": completions},
            {"name": "@cusername", "value": username},
        ], enable_cross_partition_query=True)
    results = list(results)
    return results

def cachesearch( vectors, username,similarity_score , num_results):
    # Execute the query
   
    mydbt = client.get_database_client(dbsource)   
    container = mydbt.get_container_client(cachecol)
    
    results = container.query_items(
        query= '''
        SELECT TOP @num_results  c.completion, VectorDistance(c.vector, @embedding) as SimilarityScore 
        FROM c
        WHERE VectorDistance(c.vector,@embedding) > @similarity_score and c.name = @usernames
        ORDER BY VectorDistance(c.vector,@embedding)
        ''',
        parameters=[
            {"name": "@embedding", "value": vectors},
            {"name": "@num_results", "value": num_results},
            {"name": "@usernames", "value": username},
            {"name": "@similarity_score", "value": similarity_score}
        ],
        enable_cross_partition_query=True, populate_query_metrics=True)
   
    formatted_results = []
    for result in results:
     
        formatted_results.append(result)

  
    return formatted_results


def cacheresponse(user_prompt, prompt_vectors, response, username):
    
   
    mydbt = client.get_database_client(dbsource)   
    container = mydbt.get_container_client(cachecol)
    

    
    
    # Create a dictionary representing the chat document
    chat_document = {
        'id':  str(uuid.uuid4()),  
        'prompt': user_prompt,
        'completion': response['choices'][0]['message']['content'],
        'completionTokens': str(response['usage']['completion_tokens']),
        'promptTokens': str(response['usage']['prompt_tokens']),
        'totalTokens': str(response['usage']['total_tokens']),
        'model': response['model'],
        'name': username,
        'vector': prompt_vectors
    }
    # Insert the chat document into the Cosmos DB container
    container.create_item(body=chat_document)
 

def clearall(): 
    mydbt = client.get_database_client(dbsource)
    cont = mydbt.list_containers()
    for c in cont : 
       mydbt.delete_container(c)


def createcachecollection():
    mydbt = client.get_database_client(dbsource)   
      
# Create the vector embedding policy to specify vector details
    vector_embedding_policy = {
    "vectorEmbeddings": [ 
        { 
            "path":"/vector" ,
             "dataType":"float32",
            "distanceFunction":"cosine",
            "dimensions":1536
        }, 
    ]
}

# Create the vector index policy to specify vector details
    indexing_policy = { 
    "vectorIndexes": [ 
        {
            "path": "/vector", 
            "type": "diskANN"
            
        }
    ]
    } 
   
  
# Create the cache collection with vector index
    try:
        mydbt.create_container_if_not_exists( id=cachecol, 
                                                  partition_key=PartitionKey(path='/id'), 
                                                  indexing_policy=indexing_policy,
                                                  vector_embedding_policy=vector_embedding_policy
                                                ) 
 

    except exceptions.CosmosHttpResponseError: 
        raise 
   



def clearcache ():
   
 
    mydbt = client.get_database_client(dbsource)   
  
    
      
# Create the vector embedding policy to specify vector details
    vector_embedding_policy = {
    "vectorEmbeddings": [ 
        { 
            "path":"/vector" ,
             "dataType":"float32",
            "distanceFunction":"cosine",
            "dimensions":1536
        }, 
    ]
}

# Create the vector index policy to specify vector details
    indexing_policy = { 
    "vectorIndexes": [ 
        {
            "path": "/vector", 
            "type": "diskANN"
            
        }
    ]
    } 
   
    mydbt.delete_container(cachecol)


# Create the cache collection with vector index
    try:
        mydbt.create_container_if_not_exists( id=cachecol, 
                                                  partition_key=PartitionKey(path='/id'), 
                                                  indexing_policy=indexing_policy,
                                                  vector_embedding_policy=vector_embedding_policy
                                                ) 
 

    except exceptions.CosmosHttpResponseError: 
        raise 
    return "Cache cleared."
     
def generatecompletionede(user_prompt, vector_search_results, chat_history):
    
    system_prompt = '''
    You are an intelligent assistant for yourdata . You are designed to provide helpful answers to user questions about  your data.
    You are friendly, helpful, and informative and can be lighthearted. Be concise in your responses, but still friendly.
        - Only answer questions related to the information provided below. 
        - Write two lines of whitespace between each answer in the list.
    '''

    # Create a list of messages as a payload to send to the OpenAI Completions API

    # system prompt
    
    messages = [{'role': 'system', 'content': system_prompt}]
    
    #chat history
    for chat in chat_history:
        messages.append({'role': 'user', 'content': chat['prompt'] + " " + chat['completion']})
    
    #user prompt
    messages.append({'role': 'user', 'content': user_prompt})

    #vector search results
    for result in vector_search_results:
        messages.append({'role': 'system', 'content': result['text']})

    
    # Create the completion
    response = get_completion(openai_client, openai_chat_model, messages)
  
    
    return response

def chat_completion(user_input,username, cachecoeficient, coefficient, maxresult):

    # Generate embeddings from the user input
    user_embeddings = generate_embeddings(openai_client, user_input)
    
    # Query the chat history cache first to see if this question has been asked before
    cache_results = cachesearch(user_embeddings ,username,cachecoeficient, 1)

    if len(cache_results) > 0:
       
        return cache_results[0]['completion'], True
    else:
        # Perform vector search on the movie collection
       
        search_results = get_similar_docs(openai_client, dbsource, user_input, maxresult,coefficient)
        
        
        # Chat history
        chat_history = get_chat_history(username,1)

        # Generate the completion
        completions_results = generatecompletionede(user_input, search_results, chat_history)

        # Cache the response
        cacheresponse(user_input, user_embeddings, completions_results,username)

        
        
        return completions_results['choices'][0]['message']['content'], False



# Fonction pour authentifier l'utilisateur
def authenticate(username):
    # Pour des raisons de démonstration, nous utilisons une vérification simple
    return username 




# Fonction pour charger des documents (fonction de remplacement)

# Application Streamlit
def main():
    st.title("Connection page")

    coefficient = 0.75
    cachecoeficient = 0.99
    maxresult = 5
    global chat_history
    chat_history = []
    fileload=[]

    # Initialize session state for login
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if st.session_state.logged_in:
       
        username = st.session_state.username
        display = "Welcome to the applicaton: " + username 
        st.success(display)

        # Onglets
        tab1, tab2, tab3, tab4 = st.tabs(["Configuration", "Chargement", "Chat", "Create by "])

        with tab1:
            st.header("Configuration")
            coefficient = st.slider("Coefficient de similarité", 0.0, 1.0, 0.78)
            cachecoeficient = st.slider("Coefficient de similarité pour le cache", 0.0, 1.0, 0.99)
            maxresult = st.slider("Nombre de résultats", 1, 10, 5)
            
            if st.button("create new vector DB"):
                createvectordb(colvector)
                createcachecollection()
                st.write("La base de données vectorielle a été créée et le cache.")
                
            
            if st.button("clear cache"):
                st.write("Cache cleared.")
                clearcache()
                st.write("Cache cleared.")
                st.write("delete all collection")
                

            if st.button("clear all "):
                st.write("delete all collection")
                clearall()
                st.write("all collection delete ")

        with tab2:
            st.header("Chargement de document ")
        
            uploaded_file = st.file_uploader("Choisissez un fichier", type=["pdf", "docx", "json"])
            if uploaded_file is not None:
                st.write("Fichier sélectionné:", uploaded_file.name)
        
            # Enregistrer temporairement le fichier téléchargé pour obtenir le chemin absolu
                with open(uploaded_file.name, "wb") as f:
                     f.write(uploaded_file.getbuffer())

            # Obtenir le chemin absolu du fichier
                absolute_file_path = os.path.abspath(uploaded_file.name)
                st.write(f"Le chemin absolu du fichier est : {absolute_file_path}")
                
                if ".doc" in uploaded_file.name:
                    loadwordfile(dbsource,'word',uploaded_file.name,absolute_file_path )
                    ReadFeed('word')
                   
                    st.write("Le fichier est un document Word.")
                elif ".pdf" in uploaded_file.name:
                    loadpdffile(dbsource,'pdf',uploaded_file.name,absolute_file_path )
                    ReadFeed('pdf')
                    st.write("Le fichier est un document PDF." + uploaded_file.name)
                elif ".json" in uploaded_file.name:
                    name = uploaded_file.name.replace('.json', '')
                    print("name")
                    loaddata(dbsource,name,absolute_file_path )
                    ReadFeed('pdf')
                    st.write("Le fichier est un document JSON." + uploaded_file.name )
                elif ".csv" in uploaded_file.name:
                    loadcsvfile(dbsource,'csv',uploaded_file.name,absolute_file_path )
                    ReadFeed('csv')
                    st.write("Le fichier est un document csv." + uploaded_file.name )

                os.remove(absolute_file_path)
                st.write(f"Le fichier temporaire {absolute_file_path} a été supprimé.")

         
        with tab3:
            st.header("Chat")
            reset_button_key = "reset_button"
            reset_button = st.button("Reset Chat",key=reset_button_key)
            if reset_button:
                st.session_state.messages = ""
                st.chat_message = None
                
            st.write("Chatbot goes here")
            if "messages" not in st.session_state:
                st.session_state["messages"] = [
                {"role": "assistant", "content": "Hi, I'm a chatbot who can search the web. How can I help you?"}
                ]
            for msg in st.session_state.messages:
                st.chat_message(msg["role"]).write(msg["content"])
           
                          
            if prompt := st.chat_input(placeholder="groupama"):
                st.session_state.messages.append({"role": "user", "content": prompt})
                st.chat_message("user").write(prompt)
                with st.chat_message("assistant"):
                    question = prompt
                    start_time = time.time()
                    response_payload, cached = chat_completion(question,username,cachecoeficient,coefficient, maxresult)
                    end_time = time.time()
                    elapsed_time = round((end_time - start_time) * 1000, 2)
                    response = response_payload

                    details = f"\n (Time: {elapsed_time}ms)"
                    if cached:
                        details += " (Cached)"
                        chat_history.append([question, response + "for "+ username + details])
                    else:
                        chat_history.append([question, response + details])
        
                    st.session_state.messages.append({"role": "assistant", "content":chat_history})
                    st.write(chat_history)
            
           
                
        with tab4:
            st.write("made by emmanuel")


    else:
        # Formulaire de connexion
      
        username_input = st.text_input("Nom d'utilisateur")
       

        if st.button("Connexion"):
            if authenticate(username_input):
                st.session_state.logged_in = True
                st.session_state.username = username_input
                st.rerun()
            else:
                st.error("Nom d'utilisateur ou mot de passe incorrect")


if __name__ == "__main__":
    main()