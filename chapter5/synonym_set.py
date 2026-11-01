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

# Be sure to have the index created by chapter5/ingest_scifi_movies.py before running this script.
INDEX_NAME = "scifi_movies"
synonym_id = "scifi-vocabulary"

# Search for "movie about a robot woman" should not match "robotic" in the Perfect Woman movie
print("-- Search without the synonyms")

response = es.search(
    index=INDEX_NAME,
    query={
        "match": {
            "description": {
                "query": "movie about a robot woman"
            }
        }
    }
)
for hit in response['hits']['hits']:
    print(hit['_score'], hit['_source']['title'])

# Add synonym for robot, robotic
response = es.synonyms.put_synonym(
    id=synonym_id,
    synonyms_set=[
        {
            'id': 'ufo',
            'synonyms': 'ufo, flying saucer'
        },
        {
            'id': 'spacecraft',
            'synonyms': 'spacecraft, spaceship'
        },
        {
            'id': 'moon',
            'synonyms': 'moon, lunar'
        },
        {
            'id': 'robot',
            'synonyms': 'robot, robotic'
        }
    ]
)

# Add the analyzer with synonym_graph
es.indices.close(index=INDEX_NAME)

es.indices.put_settings(
    index=INDEX_NAME,
    settings={
        "analysis": {
            "filter": {
                "movie_synonyms_filter": {
                    "type": "synonym_graph",
                    "synonyms_set": synonym_id,
                    "updateable": True
                }
            },
            "analyzer": {
                "movie_synonyms_analyzer": {
                    "type": "custom",
                    "tokenizer": "standard",
                    "filter": [
                        "lowercase",
                        "movie_synonyms_filter"
                    ]
                }
            }
        }
    }
)

es.indices.open(index=INDEX_NAME)

# Re-execute the previous search with the analyzer
print(f"\n-- Search with the synonyms")

response = es.search(
    index=INDEX_NAME,
    query={
        "match": {
            "description": {
                "query": "movie about a robot woman",
                 "analyzer": "movie_synonyms_analyzer"
            }
        }
    }
)
for hit in response['hits']['hits']:
    print(hit['_score'], hit['_source']['title'])
 