# Code example from Context Engineering with Elasticsearch book
# Copyright 2026 by Enrico Zimuel. All rights reserved.

import os

from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan, bulk
from dotenv import load_dotenv

load_dotenv()  # reads variables from a .env file and sets them in os.environ

es = Elasticsearch(
    os.environ["ELASTICSEARCH_URL"],
    api_key=os.environ["ELASTICSEARCH_API_KEY"],
)

# Be sure to have the index created by chapter5/ingest_scifi_movies.py before running this script.
LAB_INDEX = "scifi-movies-context-lab"

# Create a lab index

if es.indices.exists(index=LAB_INDEX):
    es.indices.delete(index=LAB_INDEX)

es.indices.create(
    index=LAB_INDEX,
    mappings={
        'properties': {
            'title': {
                'type': 'text'
            },
            'title_autocomplete': {
                'type': 'search_as_you_type'
            },
            'description': {
                'type': 'text'
            },
            'director': {
                'type': 'text',
                'fields': {
                    'keyword': {
                        'type': 'keyword'
                    }
                }
            },
            'datePublished': {
                'type': 'integer'
            },
            'aggregateRating': {
                'type': 'float'
            },
            'inLanguage': {
                'type': 'keyword'
            }
        }
    }
)

# Copy documents from the scifi index
actions = []
for hit in scan(
    es,
    index='scifi_movies',
    query={
        'query': {
            'match_all': {}
        }
    }
):
    source = hit['_source']
    source['title_autocomplete'] = source['title']
    actions.append({
        '_index': LAB_INDEX,
        '_id': hit['_id'],
        '_source': source
    })

bulk(es, actions)

es.indices.refresh(
    index=LAB_INDEX
)

# Create baseline retrieval

def baseline_search(client, query_text, size=5):
    response = client.search(
        index=LAB_INDEX,
        size=size,
        query={
            'multi_match': {
                'query': query_text,
                'fields': [
                    'title^4',
                    'description',
                    'director^2'
                ],
                'operator': 'and'
            }
        }
    )

    return [
        {
            'id': hit['_id'],
            'title': hit['_source']['title'],
            'score': hit['_score']
        }
        for hit in response['hits']['hits']
    ]

# Try correcting spelled queries
print(baseline_search(es, 'Destination Moon'))
print(baseline_search(es, 'flying saucer'))

# Try spelling errors
print(baseline_search(es, 'Destinaton Moon'))
print(baseline_search(es, 'Rocketshp X-M'))

# Implement autocomplete
def autocomplete(client, prefix, size=5):
    response = client.search(
        index=LAB_INDEX,
        size=size,
        query={
            'multi_match': {
                'query': prefix,
                'type': 'bool_prefix',
                'fields': [
                    'title_autocomplete',
                    'title_autocomplete._2gram',
                    'title_autocomplete._3gram'
                ]
            }
        }
    )

    return [
        hit['_source']['title']
        for hit in response['hits']['hits']
    ]

# Try several partial queries

print(autocomplete(es, 'dest'))
print(autocomplete(es, 'rocket'))
print(autocomplete(es, 'flying sau'))

# Implement spell correction
def spelling_suggestions(client, query_text):
    response = client.search(
        index=LAB_INDEX,
        suggest={
            'spellcheck': {
                'text': query_text,
                'term': {
                    'field': 'title',
                    'suggest_mode': 'always',
                    'size': 3
                }
            }
        }
    )

    return response['suggest']['spellcheck']

# Build a candidate correct query
def corrected_query(client, query_text):
    entries = spelling_suggestions(client, query_text)

    terms = []

    for entry in entries:
        if entry['options']:
            terms.append(
                entry['options'][0]['text']
            )
        else:
            terms.append(
                entry['text']
            )

    return ' '.join(terms)

# Test
original = 'Destinaton Moon'

candidate = corrected_query(es, original)

print('Original:', original)
print('Candidate:', candidate)


# Add fuzzy recovery
def fuzzy_search(client, query_text, size=5):
    response = client.search(
        index=LAB_INDEX,
        size=size,
        query={
            'multi_match': {
                'query': query_text,
                'fields': [
                    'title^4',
                    'description',
                    'director^2'
                ],
                'operator': 'and',
                'fuzziness': 'AUTO',
                'prefix_length': 1,
                'max_expansions': 25
            }
        }
    )

    return [
        {
            'id': hit['_id'],
            'title': hit['_source']['title'],
            'score': hit['_score']
        }
        for hit in response['hits']['hits']
    ]

# Enhanced search
def enhanced_search(client, query_text, size=5):
    baseline = baseline_search(
        client, 
        query_text, 
        size=size
    )

    if baseline:
        return {
            'strategy': 'baseline',
            'query': query_text,
            'results': baseline
        }

    candidate = corrected_query(client, query_text)

    if candidate != query_text:
        corrected_results = baseline_search(
            client,
            candidate,
            size=size
        )

        if corrected_results:
            return {
                'strategy': 'spell_correction',
                'query': candidate,
                'results': corrected_results
            }

    fuzzy_results = fuzzy_search(
        client,
        query_text,
        size=size
    )

    return {
        'strategy': 'fuzzy_fallback',
        'query': query_text,
        'results': fuzzy_results
    }


#  Test cases and recall

TEST_CASES = [
    {
        'query': 'Destination Moon',
        'relevant': {
            'Destination Moon'
        }
    },
    {
        'query': 'Destinaton Moon',
        'relevant': {
            'Destination Moon'
        }
    },
    {
        'query': 'Rocketshp X-M',
        'relevant': {
            'Rocketship X-M'
        }
    },
    {
        'query': 'Flying Saucer',
        'relevant': {
            'The Flying Saucer'
        }
    },
    {
        'query': 'Flying Sacer',
        'relevant': {
            'The Flying Saucer'
        }
    },
    {
        'query': 'King Rocket Men',
        'relevant': {
            'King of the Rocket Men'
        }
    }
]

# Recall@k
def recall_at_k(results, relevant, k):
    retrieved = {
        result['title']
        for result in results[:k]
    }

    if not relevant:
        return 0.0

    return len(
        retrieved.intersection(relevant)
    ) / len(relevant)

print("Test Recall@3")

results = baseline_search(
    es,
    'Destinaton Moon',
    size=3
)
score = recall_at_k(
    results,
    {'Destination Moon'},
    3
)
print(score)

# Reciprocal rank
def reciprocal_rank(results, relevant):
    for rank, result in enumerate(
        results,
        start=1
    ):
        if result['title'] in relevant:
            return 1.0 / rank

    return 0.0

# Evaluate
def evaluate(client):
    baseline_recall = []
    enhanced_recall = []

    baseline_rr = []
    enhanced_rr = []

    for case in TEST_CASES:
        query = case['query']
        relevant = case['relevant']

        baseline = baseline_search(
            client,
            query,
            size=3
        )

        enhanced = enhanced_search(
            client,
            query,
            size=3
        )['results']

        baseline_recall.append(
            recall_at_k(
                baseline,
                relevant,
                3
            )
        )

        enhanced_recall.append(
            recall_at_k(
                enhanced,
                relevant,
                3
            )
        )

        baseline_rr.append(
            reciprocal_rank(
                baseline,
                relevant
            )
        )

        enhanced_rr.append(
            reciprocal_rank(
                enhanced,
                relevant
            )
        )

    count = len(TEST_CASES)

    print(
        'Baseline Recall@3:',
        sum(baseline_recall) / count
    )

    print(
        'Enhanced Recall@3:',
        sum(enhanced_recall) / count
    )

    print(
        'Baseline MRR:',
        sum(baseline_rr) / count
    )

    print(
        'Enhanced MRR:',
        sum(enhanced_rr) / count
    )

evaluate(es)

# Measure latency
def measured_fuzzy_search(client, query_text):
    response = client.search(
        index=LAB_INDEX,
        size=5,
        query={
            'multi_match': {
                'query': query_text,
                'fields': [
                    'title^4',
                    'description'
                ],
                'fuzziness': 'AUTO',
                'prefix_length': 1,
                'max_expansions': 25
            }
        }
    )

    return {
        'took_ms': response['took'],
        'titles': [
            hit['_source']['title']
            for hit in response['hits']['hits']
        ]
    }

# Autocomplete tests
AUTOCOMPLETE_TESTS = [
    {
        'prefix': 'dest',
        'expected': 'Destination Moon'
    },
    {
        'prefix': 'rockets',
        'expected': 'Rocketship X-M'
    },
    {
        'prefix': 'flying sau',
        'expected': 'The Flying Saucer'
    },
    {
        'prefix': 'king rocket',
        'expected': 'King of the Rocket Men'
    }
]

def autocomplete_coverage(client, k=5):
    successes = 0

    for case in AUTOCOMPLETE_TESTS:
        suggestions = autocomplete(
            client,
            case['prefix'],
            size=k
        )

        if case['expected'] in suggestions:
            successes += 1

    return (
        successes /
        len(AUTOCOMPLETE_TESTS)
    )

print(
    'Autocomplete coverage@5:',
    autocomplete_coverage(es, 5)
)

# Autocomplete RR
def autocomplete_rr(
    suggestions,
    expected
):
    for rank, suggestion in enumerate(
        suggestions,
        start=1
    ):
        if suggestion == expected:
            return 1.0 / rank

    return 0.0
