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

print(f"Search 1: multi match with boost...")

response = es.search(
    index=INDEX_NAME,
    query={
        "multi_match": {
            "query": "rag system chunks",
            "fields": [
                "title^4",
                "section_heading^2",
                "chunk_text"
            ],
            "type": "best_fields",
            "minimum_should_match": "70%"
        }
    }
)

print("Results:")
for hit in response["hits"]["hits"]:
    print(hit["_id"], hit["_score"], hit["_source"]["section_heading"])

print(f"Search 2: bool with multi match, filter and should...")

response = es.search(
    index=INDEX_NAME,
    query={
        "bool": {
            "must": [
                {
                "multi_match": {
                    "query": "rag system chunks",
                    "fields": ["title^4", "section_heading^2", "chunk_text"],
                    "minimum_should_match": "70%"
                }
                }
            ],
            "filter": [
                { "term": { "language": "en" } },
                { "term": { "source_type": "book" } },
                { "term": { "status": "published" } }
            ],
            "should": [
                { "term": { "tags": { "value": "elasticsearch", "boost": 1.5 } } }
            ]
        }
    }
)

print("Results:")
for hit in response["hits"]["hits"]:
    print(hit["_id"], hit["_score"], hit["_source"]["section_heading"])


