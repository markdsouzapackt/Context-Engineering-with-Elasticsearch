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

INDEX_NAME = "scifi-movies-lab"

def create_index(index_name: str):
    es.indices.create(
        index=index_name,
        settings={
            'analysis': {
                'tokenizer': {
                    'title_edge_tokenizer': {
                        'type': 'edge_ngram',
                        'min_gram': 2,
                        'max_gram': 15,
                        'token_chars': [
                            'letter',
                            'digit'
                        ]
                    }
                },
                'analyzer': {
                    'title_autocomplete_index': {
                        'type': 'custom',
                        'tokenizer': 'title_edge_tokenizer',
                        'filter': [
                            'lowercase'
                        ]
                    }
                }
            }
        },
        mappings={
            'properties': {
                'title': {
                    'type': 'text'
                },
                'title_edge': {
                    'type': 'text',
                    'analyzer': 'title_autocomplete_index',
                    'search_analyzer': 'standard'
                },
                'description': {
                    'type': 'text'
                }
            }
        }
    )

def ingest_movie(movie: dict, index_name: str):
    es.index(
        index=index_name,
        document=movie
    )

if not(es.indices.exists(index=INDEX_NAME)):
    create_index(INDEX_NAME)
    # Ingest a movie
    movie = {
        'title': 'Rocketship X-M',
        'title_edge': 'Rocketship X-M',
        'description': (
            'A Moon expedition goes wrong and '
            'the crew reaches Mars.'
        )
    }
    ingest_movie(movie, index_name=INDEX_NAME)

# This search should return the movie Rocketship X-M
response = es.search(
    index=INDEX_NAME,
    query={
        'match': {
            'title_edge': 'rocke'
        }
    }
)

for hit in response['hits']['hits']:
    print(hit['_source']['title'])
