# Code example from Context Engineering with Elasticsearch book
# Copyright 2026 by Enrico Zimuel. All rights reserved.

import os
from elasticsearch import Elasticsearch
from dotenv import load_dotenv

load_dotenv()

es = Elasticsearch(
    os.environ["ELASTICSEARCH_URL"],
    api_key=os.environ["ELASTICSEARCH_API_KEY"]
)

index_name = "analysis_mismatch_demo"

if es.indices.exists(index=index_name):
    es.indices.delete(index=index_name)

es.indices.create(
    index=index_name,
    mappings={
        "properties": {
            "title": {
                "type": "text",
                "analyzer": "whitespace",
                "search_analyzer": "standard"
            }
        }
    }
)

es.index(
    index=index_name,
    id="1",
    document={
        "title": "Quick-Fox search adapter"
    },
    refresh=True
)

response = es.indices.analyze(
    index=index_name,
    analyzer="whitespace",
    text="Quick-Fox search adapter"
)

print([token["token"] for token in response["tokens"]])

# ['Quick-Fox', 'search', 'adapter']


response = es.indices.analyze(
    index=index_name,
    analyzer="standard",
    text="quick fox"
)

print([token["token"] for token in response["tokens"]])

# ['quick', 'fox']

response = es.search(
    index=index_name,
    query={
        "match": {
            "title": "quick fox"
        }
    }
)

print(response["hits"]["total"]["value"])

# 0


fixed_index_name = "analysis_match_demo"

if es.indices.exists(index=fixed_index_name):
    es.indices.delete(index=fixed_index_name)

es.indices.create(
    index=fixed_index_name,
    mappings={
        "properties": {
            "title": {
                "type": "text",
                "analyzer": "standard",
                "search_analyzer": "standard"
            }
        }
    }
)

es.index(
    index=fixed_index_name,
    id="1",
    document={
        "title": "Quick-Fox search adapter"
    },
    refresh=True
)

response = es.indices.analyze(
    index=fixed_index_name,
    field="title",
    text="Quick-Fox search adapter"
)

print([token["token"] for token in response["tokens"]])

# ['quick', 'fox', 'search', 'adapter']

response = es.indices.analyze(
    index=fixed_index_name,
    field="title",
    text="quick fox"
)

print([token["token"] for token in response["tokens"]])

# ['quick', 'fox']

response = es.search(
    index=fixed_index_name,
    query={
        "match": {
            "title": "quick fox"
        }
    }
)

print(response["hits"]["total"]["value"])
print(response["hits"]["hits"][0]["_source"]["title"])

# 1
# Quick-Fox search adapter
