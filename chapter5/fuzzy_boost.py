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

response = es.search(
    index=INDEX_NAME,
    query={
        'bool': {
            'should': [
                {
                    'match': {
                        'title': {
                            'query': user_query,
                            'fuzziness': 'AUTO',
                            'boost': 4
                        }
                    }
                },
                {
                    'match': {
                        'description': {
                            'query': user_query,
                            'fuzziness': 'AUTO'
                        }
                    }
                }
            ]
        }
    }
)

for hit in response['hits']['hits']:
    print(hit['_score'], hit['_source']['title'])
