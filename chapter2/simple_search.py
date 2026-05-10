# Code example from Context Engineering with Elasticsearch book
# Copyright 2026 by Enrico Zimuel. All rights reserved.

import os
from elasticsearch import Elasticsearch
from dotenv import load_dotenv

load_dotenv()  # reads variables from a .env file and sets them in os.environ

es = Elasticsearch(
    os.environ["ELASTICSEARCH_URL"],
    api_key=os.environ["ELASTICSEARCH_API_KEY"],
)

index_name = "ir_docs"

if not es.indices.exists(index=index_name):
    # This is the mapping (structure) of the index,
    # it defines the fields and their types
    mapping = {
        "mappings": {
            "properties": {
                "title": {"type": "text"},
                "body": {"type": "text"},
                "source": {"type": "keyword"}
            }
        }
    }
    print(f"Creating index '{index_name}'")

    # Create the index with the mapping, ignore if it already exists
    es.indices.create(index=index_name, body=mapping)

    docs = [
        {
            "title": "Introduction to information retrieval",
            "body": "An inverted index maps terms to documents and makes lexical search fast.",
            "source": "book"
        },
        {
            "title": "Ranking basics",
            "body": "TF IDF and BM25 use term statistics to score documents.",
            "source": "book"
        },
        {
            "title": "LLM retrieval pipelines",
            "body": "Better retrieval improves context quality more than larger prompts.",
            "source": "book"
        }
    ]

    print(f"Indexing {len(docs)} documents into index '{index_name}'")
    # Store the documents in the index, assigning a unique ID to each document
    for i, doc in enumerate(docs, start=1):
        es.index(index=index_name, id=i, document=doc)
    
    # Make sure the documents are searchable before running the query
    es.indices.refresh(index=index_name) 
    print("Documents indexed successfully.")

print("Searching for documents containing terms: inverted, index, lexical, retrieval")
# A basic lexical query
response = es.search(
    index=index_name,
    query={
        "match": {
            "body": "inverted index lexical retrieval"
        }
    }
)

for hit in response["hits"]["hits"]:
    print(hit["_id"], hit["_score"], hit["_source"]["title"])

