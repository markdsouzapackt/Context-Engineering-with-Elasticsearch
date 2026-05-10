# Code example from Context Engineering with Elasticsearch book
# Copyright 2026 by Enrico Zimuel. All rights reserved.

import os
import json

from elasticsearch import Elasticsearch
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()  # reads variables from a .env file and sets them in os.environ

es = Elasticsearch(
    os.environ["ELASTICSEARCH_URL"],
    api_key=os.environ["ELASTICSEARCH_API_KEY"],
)

INDEX_NAME = "rag_context_chunks"
jsonl_path = Path(__file__).resolve().parents[1] / "data/rag_context_chunks.jsonl"

print(f"Reading documents from {jsonl_path}...")
documents = []
with jsonl_path.open("r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line:
            # Keep each JSON document as a unique JSON string in the list
            documents.append(json.loads(line))

mapping = {
    "mappings": {
        "properties": {
            # Searchable text fields
            "title": {
                "type": "text",
                "fields": {
                    "keyword": {
                        "type": "keyword"
                    }
                }
            },
            "section_heading": {
                "type": "text",
                "fields": {
                    "keyword": {
                        "type": "keyword"
                    }
                }
            },
            "chunk_text": {
                "type": "text"
            },

            # Exact metadata fields
            "doc_id": {
                "type": "keyword"
            },
            "chunk_id": {
                "type": "keyword"
            },
            "source_type": {
                "type": "keyword"
            },
            "source_path": {
                "type": "keyword"
            },
            "tenant_id": {
                "type": "keyword"
            },
            "language": {
                "type": "keyword"
            },
            "permissions": {
                "type": "keyword"
            },

            # Sortable and filterable values
            "created_at": {
                "type": "date"
            },
            "updated_at": {
                "type": "date"
            },
            "version": {
                "type": "integer"
            },
            "tags": {
                "type": "keyword"
            },
            "status": {
                "type": "keyword"
            },

            # Optional ranking features
            "popularity": {
                "type": "float"
            },
            "freshness_score": {
                "type": "float"
            },
            "business_priority": {
                "type": "integer"
            },

            # Structured metadata
            "metadata": {
                "type": "object"
            }
        }
    }
}

if es.indices.exists(index=INDEX_NAME):
    es.indices.delete(index=INDEX_NAME)

# Create the index with the defined mapping
print(f"Creating index '{INDEX_NAME}' with mapping...")
es.indices.create(index=INDEX_NAME, **mapping)


# Index the documents into Elasticsearch
print(f"Indexing {len(documents)} documents into '{INDEX_NAME}'...")
for document in documents:
    es.index(
        index=INDEX_NAME,
        id=document["chunk_id"],
        document=document
    )

es.indices.refresh(index=INDEX_NAME)