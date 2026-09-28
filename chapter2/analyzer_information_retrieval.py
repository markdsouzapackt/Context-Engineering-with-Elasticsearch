# Code example from Context Engineering with Elasticsearch book
# Copyright 2026 by Enrico Zimuel. All rights reserved.

import spacy
from collections import defaultdict

nlp = spacy.load("en_core_web_sm")

def simple_analyzer(text: str) -> list[str]:
    doc = nlp(text)
    return [
        token.text.lower()
        for token in doc
        if not token.is_stop and not token.is_punct and not token.is_space
    ]


def lemmatizing_analyzer(text: str) -> list[str]:
    doc = nlp(text)
    return [
        token.lemma_.lower()
        for token in doc
        if not token.is_stop and not token.is_punct and not token.is_space
    ]


def build_index(corpus: dict[str, str], analyzer) -> dict[str, set[str]]:
    index = defaultdict(set)

    for doc_id, text in corpus.items():
        for term in analyzer(text):
            index[term].add(doc_id)

    return index


def search(query: str, index: dict[str, set[str]], analyzer) -> list[str]:
    query_terms = analyzer(query)

    candidates = set()
    for term in query_terms:
        candidates.update(index.get(term, set()))

    return sorted(candidates)

documents = {
    "doc_1": "Users retrieved documents from the search index.",
    "doc_2": "The system retrieves passages for better answers.",
    "doc_3": "Retrieving context improves the quality of generated answers.",
    "doc_4": "The index stores terms and postings lists.",
}

query = "retrieve documents"

simple_index = build_index(documents, simple_analyzer)

print(simple_analyzer(query))
print(search(query, simple_index, simple_analyzer))


lemma_index = build_index(documents, lemmatizing_analyzer)

print(lemmatizing_analyzer(query))
print(search(query, lemma_index, lemmatizing_analyzer))
