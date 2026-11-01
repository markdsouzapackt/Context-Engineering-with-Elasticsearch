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
user_query = 'Destnation Moon'

def search_movies(client, index_name, query_text, size=5):
    response = client.search(
        index=index_name,
        size=size,
        query={
            'multi_match': {
                'query': query_text,
                'fields': [
                    'title^4',
                    'description',
                    'director^2'
                ]
            }
        }
    )

    if response['hits']['hits']:
        return {
            'strategy': 'baseline',
            'hits': response['hits']['hits']
        }

    response = client.search(
        index='scifi-movies',
        size=size,
        query={
            'multi_match': {
                'query': query_text,
                'fields': [
                    'title^4',
                    'description',
                    'director^2'
                ],
                'fuzziness': 'AUTO',
                'prefix_length': 1,
                'max_expansions': 25
            }
        }
    )

    return {
        'strategy': 'fuzzy_fallback',
        'hits': response['hits']['hits']
    }

response = search_movies(es, INDEX_NAME, user_query)

print(f"Search result from {response['strategy']} strategy")
for hit in response['hits']:
    print(hit['_score'], hit['_source']['title'])
