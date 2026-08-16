# Code example from Context Engineering with Elasticsearch book
# Copyright 2026 by Enrico Zimuel. All rights reserved.

import os

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from dotenv import load_dotenv

load_dotenv()  # reads variables from a .env file and sets them in os.environ

es = Elasticsearch(
    os.environ["ELASTICSEARCH_URL"],
    api_key=os.environ["ELASTICSEARCH_API_KEY"],
)

# Be sure to have the index created by chapter3/mapping_and_index.py before running this script.
INDEX_NAME = "rag_context_chunks"

print(f"Search 1: dis_max...")

response = es.search(
    index=INDEX_NAME,
    query={
        "dis_max": {
            "queries": [
            {
                "match": {
                    "title": {
                        "query": "rag system chunks",
                        "boost": 4
                    }
                }
            },
            {
                "match": {
                    "section_heading": {
                        "query": "refresh api",
                        "boost": 2
                    }
                }
            },
            {
                "match": {
                    "chunk_text": {
                        "query": "elasticsearch visibility test"
                    }
                }
            }
            ],
            "tie_breaker": 0.2
        }
    }
)

print("Results:")
for hit in response["hits"]["hits"]:
    print(hit["_id"], hit["_score"], hit["_source"]["section_heading"])
