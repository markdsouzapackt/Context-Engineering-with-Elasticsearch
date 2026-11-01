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

response = es.search(
    index=INDEX_NAME,
    runtime_mappings={
        'release_decade': {
            'type': 'long',
            'script': {
                'source': '''
                    if (doc['datePublished'].size() != 0) {
                        long year = doc['datePublished'].value;
                        emit((year / 10) * 10);
                    }
                '''
            }
        }
    },
    query={
        'bool': {
            'must': {
                'match': {
                    'description': 'Moon expedition'
                }
            },
            'filter': {
                'term': {
                    'release_decade': 1950
                }
            }
        }
    },
    fields=[
        'release_decade'
    ]
)

for hit in response['hits']['hits']:
    print(hit['_score'], hit['_source']['title'], hit['fields']['release_decade'])