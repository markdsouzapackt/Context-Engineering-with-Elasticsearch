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
INDEX_NAME = "scifi_movies_completion"

# Create index with completion field

es.indices.create(
    index=INDEX_NAME,
    mappings={
        'properties': {
            'title': {
                'type': 'text'
            },
            'title_suggest': {
                'type': 'completion'
            }
        }
    }
)

# Ingest movies
movies = [
    {
        'title': 'Destination Moon',
        'weight': 20
    },
    {
        'title': 'Rocketship X-M',
        'weight': 18
    },
    {
        'title': 'The Flying Saucer',
        'weight': 16
    },
    {
        'title': 'King of the Rocket Men',
        'weight': 14
    }
]

for movie in movies:
    es.index(
        index=INDEX_NAME,
        document={
            'title': movie['title'],
            'title_suggest': {
                'input': movie['title'],
                'weight': movie['weight']
            }
        }
    )

es.indices.refresh(
    index=INDEX_NAME
)

# Request completion
response = es.search(
    index=INDEX_NAME,
    suggest={
        'movie_titles': {
            'prefix': 'rock',
            'completion': {
                'field': 'title_suggest',
                'size': 5,
                'skip_duplicates': True
            }
        }
    }
)

print(response)

options = response['suggest']['movie_titles'][0]['options']
for option in options:
    print(option['text'])
