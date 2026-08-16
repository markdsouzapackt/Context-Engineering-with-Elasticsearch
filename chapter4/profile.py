# Code example from Context Engineering with Elasticsearch book
# Copyright 2026 by Enrico Zimuel. All rights reserved.

from elasticsearch import Elasticsearch

def profiled_search(client: Elasticsearch, index: str, query: dict, size: int = 10) -> dict:
    response = client.search(
        index=index,
        size=size,
        profile=True,
        query=query,
    )
    return response.body
