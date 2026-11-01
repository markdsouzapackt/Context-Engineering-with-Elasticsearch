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
# Be sure to have the synonyms set created and the analyzer by chapter5/synonym_set.py
analyzer_id = "movie_synonyms_analyzer"

# Test synonyms
print(f"\n-- Test with synonyms")

TEST_CASES = [
    {
        'query': 'UFO film',
        'expected_title': 'The Flying Saucer'
    },
    {
        'query': 'robot woman',
        'expected_title': 'The Perfect Woman'
    },
    {
        'query': 'lunar expedition',
        'expected_title': 'Destination Moon'
    }
]


def search_titles(query_text, size=10):
    response = es.search(
        index=INDEX_NAME,
        size=size,
        query={
            'multi_match': {
                'query': query_text,
                'fields': [
                    'title^4',
                    'description'
                ],
                "analyzer": analyzer_id
            }
        }
    )

    return [
        hit['_source']['title']
        for hit in response['hits']['hits']
    ]

def rank_of(title, results):
    try:
        return results.index(title) + 1
    except ValueError:
        return None

for case in TEST_CASES:
    results = search_titles(case['query'])

    print(
        case['query'],
        case['expected_title'] in results,
        results
    )
    print(f"Rank: {rank_of(case['expected_title'], results)}")