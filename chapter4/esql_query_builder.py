# Code example from Context Engineering with Elasticsearch book
# Copyright 2026 by Enrico Zimuel. All rights reserved.

from elasticsearch import Elasticsearch
from elasticsearch.esql import ESQL
from dotenv import load_dotenv
from io import StringIO

import os
import pandas as pd


load_dotenv()  # reads variables from a .env file and sets them in os.environ

es = Elasticsearch(
    os.environ["ELASTICSEARCH_URL"],
    api_key=os.environ["ELASTICSEARCH_API_KEY"],
)

# Be sure to have the index created by chapter3/mapping_and_index.py before running this script.
INDEX_NAME = "rag_context_chunks"

print(f"Search 1: ES|QL query using string...")

query = f"""
FROM {INDEX_NAME}
| WHERE language == "en"
| EVAL chunk_chars = LENGTH(chunk_text)
| STATS avg_chars = AVG(chunk_chars), chunks = COUNT(*) BY source_type
| SORT avg_chars DESC
"""
print(query)

response = es.esql.query(query=query)
print(response.body)

print(f"Search 2: ES|QL query builder...\n")

query_dsl = (
    ESQL.from_(INDEX_NAME)
    .where('language == "en"')
    .eval(chunk_chars="LENGTH(chunk_text)")
    .stats("avg_chars = AVG(chunk_chars), chunks = COUNT(*) BY source_type")
    .sort("avg_chars DESC")
)
print(query_dsl)

response2 = es.esql.query(query=query_dsl)
print(response2.body)

if (query.strip() == str(query_dsl)):
    print("Success: the queries are the same")
else:
    print("Error: the queries are not the same!")
