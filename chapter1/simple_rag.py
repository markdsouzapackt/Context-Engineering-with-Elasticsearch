# Code example from Context Engineering with Elasticsearch book
# Copyright 2026 by Enrico Zimuel. All rights reserved.

import json
import os
import elasticsearch.helpers
from pathlib import Path

from dotenv import load_dotenv
from elasticsearch import Elasticsearch
from openai import OpenAI

INDEX_NAME = "scifi_movies"
DATA_PATH = Path(__file__).resolve().parents[1] / "data/scifi_movies.jsonl"
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5-nano-2025-08-07")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

load_dotenv()  # reads variables from a .env file and sets them in os.environ

es = Elasticsearch(
    os.environ["ELASTICSEARCH_URL"],
    api_key=os.environ["ELASTICSEARCH_API_KEY"],
)

llm = OpenAI(api_key=OPENAI_API_KEY)

if not es.indices.exists(index=INDEX_NAME):
	print(f"Creating index '{INDEX_NAME}'...")
	# Define the index mappings with a semantic_text field
	mappings = {
		"properties": {
			"title": {"type": "text"},
			"description": {"type": "semantic_text"},
			"director": {"type": "keyword"},
			"datePublished": {"type": "integer"},
			"aggregateRating": {"type": "float"},
			"url": {"type": "keyword"},
			"inLanguage": {"type": "keyword"},
		}
	}
	es.indices.create(index=INDEX_NAME, mappings=mappings)

	print("Ingesting data into the index...", end="")
	# Ingest the first 10 movies data
	with DATA_PATH.open("r", encoding="utf-8") as file:
		actions = []
		count = 0
		for line in file:
			if count >= 10:
				break
			line = line.strip()
			if not line:
				continue
			movie = json.loads(line)
			actions.append({"_op_type": "create", "_index": INDEX_NAME, "_source": movie})
			count += 1

		if actions:
			elasticsearch.helpers.bulk(es, actions, refresh=True)
	print("done")

# user's question
query = "Search for a movie about UFOs"
print(f"User's question: {query}")

# Semantic search using the description field
result = es.search(
	index=INDEX_NAME,
	size=3,
	query={
		"semantic": {
			"field": "description",
			"query": query,
		}
	},
)
# Get the documents that matched the query as JSON string to provide them as context to the LLM
movies = json.dumps(result["hits"]["hits"])

response = llm.responses.create(
	model=OPENAI_MODEL,
	instructions=f"Answer the question based on the following movie descriptions: {movies}. If you cannot answer the question based on the descriptions, say you don't know.",
	input=[{ "role": "user", "content": query }]
)
print("Answer from LLM:")
print(response.output_text)