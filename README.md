# Cosmsodbcopilotwebapp
a full web application where you can load file( csv , json , word , pdf ) and make llm and vector search with sample code to bulid your copilot and load your data inside and put question and answer in cache to save time


## Features
- Vector search using Azure Cosmos DB for NoSQL
- Create embeddings using Azure OpenAI text-embedding
- Use cosmosdb Nosql as cache to save latency

## Requirements
- Tested only with Python 3.11
- Azure OpenAI account
- Azure Cosmos DB for NoSQL account

## Setup
- Create virtual environment: python -m venv .venv
- Activate virtual ennvironment: .venv\scripts\activate
- Install required libraries: pip install -r requirements.txt
- Replace keys with your own values in example.env
- don't forget to have the model openAI one text-embbeding and one GPT ( can be 4.0 ,3.5 ) ...
- TO LAUNCH THE APPLICATION JUST do Streamlit run app.py
- enter a login name and after in the first login and all the collections will be create just push the button ( create vector db  )
- have fun
- some sample document are in the dataset folder
- I have add the capacity to load the data from the from ARGUS ACCELERATOR : https://github.com/Azure-Samples/ARGUS made by some collegues 
