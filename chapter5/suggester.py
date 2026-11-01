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

def spelling_suggestions(client, text):
    response = es.search(
        index=INDEX_NAME,
        suggest={
            'movie_spellcheck': {
                'text': text,
                'term': {
                    'field': 'title',
                    'suggest_mode': 'always',
                    'size': 3
                }
            }
        }
    )

    return response['suggest']['movie_spellcheck']


suggestions = spelling_suggestions(
    es,
    'Destinaton Moon'
)

for token in suggestions:
    print('Original:', token['text'])

    for option in token['options']:
        print(
            '  suggestion:',
            option['text'],
            'score:',
            option['score']
        )
