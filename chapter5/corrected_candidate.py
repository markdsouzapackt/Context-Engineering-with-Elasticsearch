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

def build_corrected_query(client, text):
    suggestions = spelling_suggestions(
        client,
        text
    )

    corrected_terms = []

    for entry in suggestions:
        if entry['options']:
            corrected_terms.append(
                entry['options'][0]['text']
            )
        else:
            corrected_terms.append(
                entry['text']
            )

    return ' '.join(corrected_terms)

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

original = 'Destinaton Moon'

corrected = build_corrected_query(es, original)

print('Original:', original)
print('Candidate:', corrected)
