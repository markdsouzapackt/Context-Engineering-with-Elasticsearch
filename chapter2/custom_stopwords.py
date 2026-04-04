# Code example from Context Engineering with Elasticsearch book
# Copyright 2026 by Enrico Zimuel. All rights reserved.

import spacy

nlp = spacy.load("en_core_web_sm")

# Add a domain-specific stop word
nlp.vocab["section"].is_stop = True

# Remove a word from stop-word treatment if it matters in your domain
nlp.vocab["will"].is_stop = False

def analyze_for_indexing(text: str) -> list[str]:
    doc = nlp(text)
    return [
        token.text.lower()
        for token in doc
        if not token.is_stop and not token.is_punct and not token.is_space
    ]