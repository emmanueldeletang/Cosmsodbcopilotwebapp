# Cosmsodbcopilotwebapp
a full web application where you can load file( csv , json , word , pdf , ppt , excel too ) and make llm and vector search with sample code to bulid your copilot and load your data inside and put question and answer in cache to save time
you can test with this new version de full text search and hybrid search in cosmsodb ... be sure you have activate the feature in preview as present here https://learn.microsoft.com/en-us/azure/cosmos-db/gen-ai/full-text-search


## Features
- Vector search using Azure Cosmos DB for NoSQL
- full text and hybrid search using Azure Cosmos DB for NoSQL
- Create embeddings using Azure OpenAI text-embedding
- Use cosmosdb Nosql as cache to save latency

## Requirements
- Tested only with Python 3.12
- Azure OpenAI account
- Azure Cosmos DB for NoSQL account

## Setup
- Create virtual environment: python -m venv .venv
- Activate virtual ennvironment: .venv\scripts\activate
- Install required libraries: pip install -r requirements.txt
- Replace keys with your own values in example.env
- don't forget to have the model openAI one text-embbeding and one GPT ( can be 4.0 ,3.5 ) ...
- use an languages service to get the sentiment of the question and make stats after .... 
- in some case you can have a bug when you create the collection , create a collection vector manually with the full text search policy for "/text"
- TO LAUNCH THE APPLICATION JUST do Streamlit run app.py
- enter a login name and after in the first login and all the collections will be create just push the button ( create vector db  )
- have fun
- some sample document are in the dataset folder
- I have add the capacity to load the data from the from ARGUS ACCELERATOR : https://github.com/Azure-Samples/ARGUS made by some collegues 
