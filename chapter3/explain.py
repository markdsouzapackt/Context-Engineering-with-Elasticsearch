# Code example from Context Engineering with Elasticsearch book
# Copyright 2026 by Enrico Zimuel. All rights reserved.

import os

from elasticsearch import Elasticsearch
from dotenv import load_dotenv

load_dotenv()  # reads variables from a .env file and sets them in os.environ

es = Elasticsearch(
    os.environ["ELASTICSEARCH_URL"],
    api_key=os.environ["ELASTICSEARCH_API_KEY"],
)

INDEX_NAME = "rag_context_chunks"

# Recursive function to print the explanation tree
def print_score_tree(node, prefix="", is_last=True):
    connector = "└── " if is_last else "├── "
    child_prefix = "    " if is_last else "│   "

    value = node.get("value")
    description = node.get("description", "")

    print(f"{prefix}{connector}{value}: {description}")

    details = node.get("details", [])
    for index, child in enumerate(details):
        print_score_tree(
            child,
            prefix=prefix + child_prefix,
            is_last=index == len(details) - 1,
        )

resp = es.explain(
    index=INDEX_NAME,
    id="chunk-100",
    query={
        "match": {
            "chunk_text": "context engineering"
        }
    }
)

print("Explanation for document chunk-100:")
print_score_tree(resp["explanation"])
    