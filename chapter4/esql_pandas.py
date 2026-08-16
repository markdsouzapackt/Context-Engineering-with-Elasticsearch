# Code example from Context Engineering with Elasticsearch book
# Copyright 2026 by Enrico Zimuel. All rights reserved.

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
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

print(f"Search 1: ES|QL query with Pandas DataFrame...")

query = f"""
FROM {INDEX_NAME}
| WHERE language == "en"
| KEEP doc_id, chunk_id, title, section_heading, source_path
| LIMIT 20
"""

response = es.esql.query(query=query, format="csv")

# Convert the CSV response to a Pandas DataFrame
df = pd.read_csv(StringIO(response.body))

print("Results:")
print(df)
