# Code example from Context Engineering with Elasticsearch book
# Copyright 2026 by Enrico Zimuel. All rights reserved.

from elasticsearch import Elasticsearch

def explain_document(client: Elasticsearch, index: str, doc_id: str, query: dict) -> dict:
    response = client.explain(
        index=index,
        id=doc_id,
        query=query,
    )
    return response.body

def print_explanation(node: dict, indent: int = 0) -> None:
    value = node.get("value")
    description = node.get("description", "")
    prefix = "  " * indent

    if value is not None:
        print(f"{prefix}{value:.4f}  {description}")
    else:
        print(f"{prefix}{description}")

    for child in node.get("details", []):
        print_explanation(child, indent + 1)

