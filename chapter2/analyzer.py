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

# Test a built-in analyzer
response = es.indices.analyze(
    analyzer="whitespace",
    text="The quick brown fox."
)

for token in response["tokens"]:
    print(token["token"], token["position"], token["start_offset"], token["end_offset"])