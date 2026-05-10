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

INDEX_NAME = "rag-ready-index"
PIPELINE_ID = "rag_chunk_pipeline"

# Step 1: Create the ingest pipeline
print(f"Creating ingest pipeline '{PIPELINE_ID}'...")

es.ingest.put_pipeline(
    id=PIPELINE_ID,
    processors=[
        {
            "gsub": {
                "field": "chunk_text",
                "pattern": "\\s+",
                "replacement": " "
            }
        },
        {
            "gsub": {
                "field": "title",
                "pattern": "\\s+",
                "replacement": " "
            }
        },
        {
            "script": {
                "lang": "painless",
                "source": """
                if (ctx.containsKey('chunk_text') && ctx.chunk_text != null) {
                    ctx.chunk_length = ctx.chunk_text.length();
                }
                """
            }
        }
    ]
)

# Step 2: Create the index with RAG oriented mappings
print(f"Creating index '{INDEX_NAME}' with RAG-oriented mappings...")

es.indices.create(
    index=INDEX_NAME,
    settings={
        "analysis": {
            "normalizer": {
                "lowercase_normalizer": {
                    "type": "custom",
                    "filter": ["lowercase", "asciifolding"]
                }
            }
        }
    },
    mappings={
        "properties": {
            "doc_id": {"type": "keyword"},
            "chunk_id": {"type": "keyword"},
            "source_uri": {"type": "keyword"},
            "tenant_id": {"type": "keyword"},
            "language": {"type": "keyword"},
            "source_type": {"type": "keyword"},
            "title": {
                "type": "text",
                "fields": {
                    "raw": {
                        "type": "keyword",
                        "normalizer": "lowercase_normalizer"
                    }
                }
            },
            "section_heading": {
                "type": "text",
                "fields": {
                    "raw": {
                        "type": "keyword",
                        "normalizer": "lowercase_normalizer"
                    }
                }
            },
            "chunk_text": {"type": "text"},
            "tags": {"type": "keyword"},
            "published_at": {"type": "date"},
            "chunk_length": {"type": "integer"},
            "popularity": {"type": "float"}
        }
    }
)

# Step 3: Bulk ingest example chunks
print(f"Ingesting example documents with pipeline '{PIPELINE_ID}'...")

docs = [
    {
        "_index": INDEX_NAME,
        "_id": "chunk-1",
        "pipeline": PIPELINE_ID,
        "_source": {
            "doc_id": "doc-100",
            "chunk_id": "chunk-1",
            "source_uri": "kb://climate/report-2025",
            "tenant_id": "acme",
            "language": "en",
            "source_type": "report",
            "title": "Heat wave adaptation in southern Europe",
            "section_heading": "Urban response measures",
            "chunk_text": "Cities in southern Europe are expanding cooling centers, shade infrastructure, and emergency heat protocols.",
            "tags": ["climate", "adaptation", "europe"],
            "published_at": "2025-06-01",
            "popularity": 12.5
        }
    },
    {
        "_index": INDEX_NAME,
        "_id": "chunk-2",
        "pipeline": PIPELINE_ID,
        "_source": {
            "doc_id": "doc-101",
            "chunk_id": "chunk-2",
            "source_uri": "kb://energy/grid-resilience",
            "tenant_id": "acme",
            "language": "en",
            "source_type": "guide",
            "title": "Cooling infrastructure planning",
            "section_heading": "Grid resilience",
            "chunk_text": "Electric grid resilience is critical during prolonged heat events, especially when air conditioning demand increases.",
            "tags": ["energy", "infrastructure"],
            "published_at": "2025-07-10",
            "popularity": 8.0
        }
    }
]

bulk(es, docs)
es.indices.refresh(index=INDEX_NAME)

# Step 4: Run a baseline lexical retrieval query
print(f"Running a baseline lexical retrieval query against index '{INDEX_NAME}'...")

user_query = "How are cities in southern Europe adapting to heat waves?"

resp = es.search(
    index=INDEX_NAME,
    size=5,
    query={
        "function_score": {
            "query": {
                "bool": {
                    "must": [
                        {
                            "multi_match": {
                                "query": user_query,
                                "fields": ["title^4", "section_heading^2", "chunk_text"]
                            }
                        }
                    ],
                    "filter": [
                        {"term": {"tenant_id": "acme"}},
                        {"term": {"language": "en"}}
                    ]
                }
            },
            "field_value_factor": {
                "field": "popularity",
                "factor": 0.05,
                "missing": 1.0
            },
            "boost_mode": "sum"
        }
    }
)

print("Search results:")
for hit in resp["hits"]["hits"]:
    print(hit["_id"], hit["_score"], hit["_source"]["title"])

# chunk-1 10.384513 Heat wave adaptation in southern Europe
# chunk-2 0.5797854 Cooling infrastructure planning