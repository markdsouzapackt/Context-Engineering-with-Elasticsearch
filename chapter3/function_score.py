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

INDEX_NAME = "rag_context_chunks"

resp = es.search(
    index=INDEX_NAME,
    query={
        "function_score": {
            "query": {
                "bool": {
                    "must": [
                        {
                            "multi_match": {
                                "query": "ranking business",
                                "fields": ["title^3", "chunk_text"]
                            }
                        }
                    ],
                    "filter": [
                        {"term": {"tenant_id": "tenant-a"}},
                        {"term": {"language": "en"}}
                    ]
                }
            },
            "field_value_factor": {
                "field": "popularity",
                "factor": 0.1,
                "missing": 1.0
            },
            "boost_mode": "sum",
            "score_mode": "sum"
        }
    }
)

print("Results:")
for hit in resp["hits"]["hits"]:
    print(
        hit["_id"], 
        hit["_score"], 
        hit["_source"]["title"], 
        hit["_source"]["section_heading"]
    )

