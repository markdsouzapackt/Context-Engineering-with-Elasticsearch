# Code example from Context Engineering with Elasticsearch book
# Copyright 2026 by Enrico Zimuel. All rights reserved.

import spacy

nlp = spacy.load("en_core_web_sm")

def analyze_with_lemmas(text: str) -> list[str]:
    doc = nlp(text)
    return [
        token.lemma_.lower()
        for token in doc
        if not token.is_stop and not token.is_punct and not token.is_space
    ]

text = "Users retrieved documents and retrieving passages improved answers."
print(analyze_with_lemmas(text))