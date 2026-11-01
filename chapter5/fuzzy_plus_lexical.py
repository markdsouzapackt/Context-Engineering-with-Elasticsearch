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
user_query = 'Rocketshp X-M'

response = es.search(
    index=INDEX_NAME,
    query={
        'bool': {
            'should': [
                {
                    'multi_match': {
                        'query': user_query,
                        'fields': [
                            'title^4',
                            'description'
                        ]
                    }
                },
                {
                    'multi_match': {
                        'query': user_query,
                        'fields': [
                            'title^3',
                            'description'
                        ],
                        'fuzziness': 'AUTO',
                        'prefix_length': 1,
                        'max_expansions': 25
                    }
                }
            ],
            'minimum_should_match': 1
        }
    }
)

for hit in response['hits']['hits']:
    print(hit['_score'], hit['_source']['title'])
