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

print(f"Search 1: query 'context engineering'...")

response = es.search(
    index=INDEX_NAME,
    query={
        "match": {
            "chunk_text": "context engineering"
        }
    }
)

print("Results:")
for hit in response["hits"]["hits"]:
    print(hit["_id"], hit["_score"], hit["_source"]["section_heading"])

print(f"\nSearch 2: filter by tenant_id 'tenant-a', status 'published', permissions 'group:engineering'...")

response = es.search(
    index=INDEX_NAME,
    query={
        "bool": {
            "filter": [
                {
                    "term": {
                        "tenant_id": "tenant-a"
                    }
                },
                {
                    "term": {
                        "status": "published"
                    }
                },
                {
                    "term": {
                        "permissions": "group:engineering"
                    }
                }
            ]
        }
    }
)

print("Results:")
for hit in response["hits"]["hits"]:
    print(hit["_id"], hit["_source"]["tenant_id"], hit["_source"]["status"])

print(f"\nSearch 3: Mistake use of term for chunk_text...")
response = es.search(
    index=INDEX_NAME,
    query={
        "term": {
            "chunk_text": "context engineering"
        }
    }
)

print("Results:")
print(response["hits"]["total"])

print(f"\nSearch 4: Aggregation by tags...")
response = es.search(
    index=INDEX_NAME,
    size=0,
    aggs={
        "chunks_by_tag": {
            "terms": {
                "field": "tags"
            }
        }
    }
)

print("Results:")
for bucket in response["aggregations"]["chunks_by_tag"]["buckets"]:
    print(bucket["key"], bucket["doc_count"])

print(f"\nSearch 5: Sort by keyword on multiple fields...")
response = es.search(
    index=INDEX_NAME,
    query={
        "match_all": {}
    },
    sort=[
        {
            "section_heading.keyword": {
                "order": "asc"
            }
        }
    ]
)

print("Results:")
for hit in response["hits"]["hits"]:
    print(hit["_source"]["section_heading"])