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

INDEX_NAME = "scifi-movies-typeahead"

def create_index(client: Elasticsearch, index_name: str):
    client.indices.create(
        index=index_name,
        mappings={
            'properties': {
                'title': {
                    'type': 'text'
                },
                'title_autocomplete': {
                    'type': 'search_as_you_type'
                },
                'description': {
                    'type': 'text'
                },
                'director': {
                    'type': 'keyword'
                }
            }
        }
    )


def ingest_movie(client: Elasticsearch, index_name: str):
    client.index(
        index=index_name,
        document={
            'title': 'Destination Moon',
            'title_autocomplete': 'Destination Moon',
            'description': (
                'A science-fiction film about '
                'a crewed expedition to the Moon.'
            ),
            'director': 'Irving Pichel'
        }
    )

def autocomplete_movies(client: Elasticsearch, index_name: str, prefix, size=5):
    response = client.search(
        index=index_name,
        size=size,
        query={
            'multi_match': {
                'query': prefix,
                'type': 'bool_prefix',
                'fields': [
                    'title_autocomplete',
                    'title_autocomplete._2gram',
                    'title_autocomplete._3gram'
                ]
            }
        }
    )

    return [
        hit['_source']['title']
        for hit in response['hits']['hits']
    ]


if not(es.indices.exists(index=INDEX_NAME)):
    create_index(es, index_name=INDEX_NAME)
    ingest_movie(es, index_name=INDEX_NAME)

# This search should return the movie Destination Moon
print(
    autocomplete_movies(
        es,
        index_name=INDEX_NAME,
        prefix='dest mo'
    )
)


