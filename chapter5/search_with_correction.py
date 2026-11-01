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

def search_with_correction(client, query_text, size=5):
    baseline = client.search(
        index='scifi-movies',
        size=size,
        query={
            'multi_match': {
                'query': query_text,
                'fields': [
                    'title^4',
                    'description'
                ]
            }
        }
    )

    baseline_hits = baseline['hits']['hits']

    if baseline_hits:
        return {
            'query': query_text,
            'strategy': 'original',
            'hits': baseline_hits
        }

    corrected = build_corrected_query(
        client,
        query_text
    )

    corrected_response = client.search(
        index='scifi-movies',
        size=size,
        query={
            'multi_match': {
                'query': corrected,
                'fields': [
                    'title^4',
                    'description'
                ]
            }
        }
    )

    return {
        'query': corrected,
        'strategy': 'spell_correction',
        'hits': corrected_response['hits']['hits']
    }
