# Code example from Context Engineering with Elasticsearch book
# Copyright 2026 by Enrico Zimuel. All rights reserved.

import spacy

nlp = spacy.load("en_core_web_sm")

def analyze_for_indexing(text: str) -> list[str]:
    doc = nlp(text)
    terms = [
        token.text.lower()
        for token in doc
        if not token.is_stop and not token.is_punct and not token.is_space
    ]
    return terms

text = "The inverted index is one of the key structures in information retrieval."
print(analyze_for_indexing(text))