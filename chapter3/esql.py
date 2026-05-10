# Code example from Context Engineering with Elasticsearch book
# Copyright 2026 by Enrico Zimuel. All rights reserved.

import os

from dotenv import load_dotenv
from elasticsearch import Elasticsearch
from elasticsearch.esql import ESQL, E, functions
from tabulate import tabulate

load_dotenv()  # reads variables from a .env file and sets them in os.environ

es = Elasticsearch(
    os.environ["ELASTICSEARCH_URL"],
    api_key=os.environ["ELASTICSEARCH_API_KEY"],
)

INDEX_NAME = "rag_context_chunks"
query= (
    ESQL.from_(INDEX_NAME)
    .where(E("tenant_id") == 'tenant-a')
    .stats(chunk_count=functions.count(E("")), avg_popularity=functions.avg(E("popularity")))
    .by("source_type", "language")
    .sort("chunk_count DESC")
    .limit(5)
)

print("Generated ES|QL query:")
gen_esql= str(query)
print(gen_esql)

resp = es.esql.query(query=gen_esql, format="txt")

print("\nJson result:")
print(resp)

print("\nTabulated result:")
headers = [column["name"] for column in resp["columns"]]
rows = resp["values"]
print(tabulate(rows, headers=headers, tablefmt="grid"))

