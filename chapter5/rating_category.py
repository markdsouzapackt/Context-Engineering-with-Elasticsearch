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
        'rating_tier': {
            'type': 'keyword',
            'script': {
                'source': '''
                    if (doc['aggregateRating'].size() == 0) {
                        emit('unrated');
                    } else if (doc['aggregateRating'].value >= 60) {
                        emit('high');
                    } else {
                        emit('standard');
                    }
                '''
            }
        }
    },
    query={
        'bool': {
            'must': {
                'match': {
                    'description': 'science fiction'
                }
            },
            'filter': {
                'term': {
                    'rating_tier': 'high'
                }
            }
        }
    },
    fields=[
        'rating_tier'
    ]
)
for hit in response['hits']['hits']:
    print(hit['_score'], hit['_source']['title'], hit['fields']['rating_tier'])


response = client.search(
    index='scifi-movies',
    runtime_mappings={
        'has_rating': {
            'type': 'boolean',
            'script': {
                'source': '''
                    emit(
                        doc['aggregateRating'].size() != 0
                    );
                '''
            }
        }
    },
    query={
        'bool': {
            'must': {
                'match': {
                    'description': 'space'
                }
            },
            'filter': {
                'term': {
                    'has_rating': True
                }
            }
        }
    }
)
