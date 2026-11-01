# Code example from Context Engineering with Elasticsearch book
# Copyright 2026 by Enrico Zimuel. All rights reserved.

import json
import os
import elasticsearch.helpers

from elasticsearch import Elasticsearch
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()  # reads variables from a .env file and sets them in os.environ

es = Elasticsearch(
    os.environ["ELASTICSEARCH_URL"],
    api_key=os.environ["ELASTICSEARCH_API_KEY"],
)

# This script ingest the data/scifi_movies.jsonl file in Elasticsearch
INDEX_NAME = "scifi_movies"
DATA_PATH = Path(__file__).resolve().parents[1] / "data/scifi_movies.jsonl"

if not es.indices.exists(index=INDEX_NAME):
	print(f"Creating index '{INDEX_NAME}'...")
	mappings = {
		"properties": {
			"title": {"type": "text"},
			"description": {"type": "text"},
			"director": {"type": "keyword"},
			"datePublished": {"type": "integer"},
			"aggregateRating": {"type": "float"},
			"url": {"type": "keyword"},
			"inLanguage": {"type": "keyword"},
		}
	}
	es.indices.create(index=INDEX_NAME, mappings=mappings)

	print("Ingesting data into the index...")
	# Ingest the movies in batches of 100 using the Bulk API
	with DATA_PATH.open("r", encoding="utf-8") as file:
		actions = []
		count = 0
		for line in file:
			if count % 50 == 0:
				if actions:
					elasticsearch.helpers.bulk(es, actions, refresh=True)
					print(f"  {count} movies")
				actions = []
			line = line.strip()
			if not line:
				continue
			movie = json.loads(line)
			actions.append({"_op_type": "create", "_index": INDEX_NAME, "_source": movie})
			count += 1

        # Insert the last batch if any
		if actions:
			elasticsearch.helpers.bulk(es, actions, refresh=True)
			print(f"  {count} movies")
else:
	print(f"The Elasticsearch index '{INDEX_NAME}' already exists")