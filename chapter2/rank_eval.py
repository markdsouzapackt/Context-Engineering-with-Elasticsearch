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

index_name = "movie_reviews"

# Clean setup
if es.indices.exists(index=index_name):
    es.indices.delete(index=index_name)

es.indices.create(
    index=index_name,
    mappings={
        "properties": {
            "text": {"type": "text"}
        }
    }
)

# Sample documents about movies reviews
docs = [
    {"_id": "doc1", "text": "DiCaprio's performance in The Revenant was breathtaking."},
    {"_id": "doc2", "text": "Inception shows Leonardo DiCaprio in one of his most iconic roles."},
    {"_id": "doc3", "text": "Brad Pitt delivers a solid performance in this crime thriller."},
    {"_id": "doc4", "text": "An action-packed adventure with stunning visual effects."},
    {"_id": "doc5", "text": "A heartbreaking story of love and loss that made me cry for hours."},
    {"_id": "doc6", "text": "One of the saddest movies ever made, bring tissues."},
    {"_id": "doc7", "text": "A lighthearted comedy that will make you laugh."},
    {"_id": "doc8", "text": "A science-fiction epic full of action and excitement."},
]

# Store the documents in the index, assigning a unique ID to each document
for doc in docs:
    es.index(index=index_name, id=doc["_id"], document={"text": doc["text"]})

# Make sure the documents are searchable before running the query
es.indices.refresh(index=index_name) 
print("Documents indexed successfully.")

# Judgment list:
# 0 = irrelevant
# 1 = relevant
# 2 or 3 = more relevant, useful for graded metrics like DCG / NDCG
requests = [
    {
        "id": "dicaprio_performance",
        "request": {
            "query": {
                "match": {
                    "text": {
                        "query": "DiCaprio performance"
                    }
                }
            }
        },
        "ratings": [
            {"_index": index_name, "_id": "doc1", "rating": 3},
            {"_index": index_name, "_id": "doc2", "rating": 2},
            {"_index": index_name, "_id": "doc3", "rating": 1},
            {"_index": index_name, "_id": "doc4", "rating": 0},
        ],
    },
    {
        "id": "sad_movies",
        "request": {
            "query": {
                "match": {
                    "text": {
                        "query": "sad movies that make you cry"
                    }
                }
            }
        },
        "ratings": [
            {"_index": index_name, "_id": "doc5", "rating": 3},
            {"_index": index_name, "_id": "doc6", "rating": 2},
            {"_index": index_name, "_id": "doc7", "rating": 0},
            {"_index": index_name, "_id": "doc8", "rating": 0},
        ],
    },
]

def run_rank_eval(metric: dict, label: str):
    resp = es.rank_eval(
        index=index_name,
        requests=requests,
        metric=metric,
    )
    print(f"{label}: {resp['metric_score']:.4f}")
    return resp

k = 3
relevant_threshold = 1

# Precision@k
precision_resp = run_rank_eval(
    {
        "precision": {
            "k": k,
            "relevant_rating_threshold": relevant_threshold,
            "ignore_unlabeled": False,
        }
    },
    f"Precision@{k}",
)

# Recall@k
recall_resp = run_rank_eval(
    {
        "recall": {
            "k": k,
            "relevant_rating_threshold": relevant_threshold,
        }
    },
    f"Recall@{k}",
)

# Mean Reciprocal Rank
mrr_resp = run_rank_eval(
    {
        "mean_reciprocal_rank": {
            "k": k,
            "relevant_rating_threshold": relevant_threshold,
        }
    },
    f"MRR@{k}",
)

# NDCG, via dcg with normalize=True
ndcg_resp = run_rank_eval(
    {
        "dcg": {
            "k": k,
            "normalize": True,
        }
    },
    f"NDCG@{k}",
)