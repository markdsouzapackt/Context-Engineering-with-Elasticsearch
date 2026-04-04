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

# Test a custom analysis chain inline
response = es.indices.analyze(
    tokenizer="standard",
    filter=["lowercase", "stop"],
    text="The Quick Brown Foxes Jumped"
)

print([token["token"] for token in response["tokens"]])