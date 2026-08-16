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

# Be sure to have the index created by chapter3/mapping_and_index.py before running this script.
INDEX_NAME = "rag_context_chunks"

## Step 1
@dataclass(frozen=True)
class SearchRequest:
    query: str
    product: str | None = None
    language: str = "en"
    content_type: str = "documentation"
    size: int = 10

## Step 2
def build_documentation_query(request: SearchRequest) -> dict[str, Any]:
    filters: list[dict[str, Any]] = [
        {"term": {"language": request.language}},
        {"term": {"content_type": request.content_type}},
        {"term": {"status": "published"}},
    ]

    if request.product:
        filters.append({"term": {"product": request.product}})

    return {
        "bool": {
            "must": [
                {
                    "dis_max": {
                        "queries": [
                            {
                                "multi_match": {
                                    "query": request.query,
                                    "fields": [
                                        "title^5",
                                        "section_heading^3",
                                        "chunk_text",
                                    ],
                                    "type": "best_fields",
                                    "minimum_should_match": "70%",
                                }
                            },
                            {
                                "match_phrase": {
                                    "title": {
                                        "query": request.query,
                                        "boost": 6,
                                        "slop": 1,
                                    }
                                }
                            },
                            {
                                "match_phrase": {
                                    "section_heading": {
                                        "query": request.query,
                                        "boost": 3,
                                        "slop": 2,
                                    }
                                }
                            },
                        ],
                        "tie_breaker": 0.2,
                    }
                }
            ],
            "filter": filters,
        }
    }

## Step 3
class DocumentationSearchService:
    def __init__(self, client: Elasticsearch, index: str) -> None:
        self.client = client
        self.index = index

    def search(self, request: SearchRequest) -> list[dict[str, Any]]:
        query = build_documentation_query(request)

        response = self.client.search(
            index=self.index,
            size=request.size,
            query=query,
            source=[
                "doc_id",
                "chunk_id",
                "title",
                "section_heading",
                "chunk_text",
                "source_path",
                "product",
                "updated_at",
            ],
            highlight={
                "fields": {
                    "title": {},
                    "section_heading": {},
                    "chunk_text": {
                        "fragment_size": 180,
                        "number_of_fragments": 2,
                    },
                }
            },
        )

        hits = response.body["hits"]["hits"]

        return [
            {
                "score": hit["_score"],
                "id": hit["_id"],
                "source": hit["_source"],
                "highlight": hit.get("highlight", {}),
            }
            for hit in hits
        ]

## Step 4
class RelevanceDebugger:
    def __init__(self, client: Elasticsearch, index: str) -> None:
        self.client = client
        self.index = index

    def explain(self, request: SearchRequest, doc_id: str) -> dict[str, Any]:
        query = build_documentation_query(request)

        response = self.client.explain(
            index=self.index,
            id=doc_id,
            query=query,
        )

        return response.body

    def profile(self, request: SearchRequest) -> dict[str, Any]:
        query = build_documentation_query(request)

        response = self.client.search(
            index=self.index,
            size=request.size,
            query=query,
            profile=True,
        )

        return response.body

## Step 5
def assert_expected_doc_in_top_k(
    service: DocumentationSearchService,
    request: SearchRequest,
    expected_doc_id: str,
    k: int = 5,
) -> None:
    results = service.search(request)
    top_doc_ids = [
        result["source"]["doc_id"]
        for result in results[:k]
    ]

    if expected_doc_id not in top_doc_ids:
        raise AssertionError(
            f"Expected {expected_doc_id} in top {k}, got {top_doc_ids}"
        )

## Step 6
def analyze_chunk_lengths(client: Elasticsearch) -> dict[str, Any]:
    response = client.esql.query(
        query="""
        FROM docs-chunks
        | WHERE status == "published"
        | EVAL chunk_chars = LENGTH(chunk_text)
        | STATS
            chunks = COUNT(*),
            avg_chars = AVG(chunk_chars),
            max_chars = MAX(chunk_chars)
          BY product, source_type
        | SORT avg_chars DESC
        """
    )

    return response.body

def analyze_missing_metadata(client: Elasticsearch) -> dict[str, Any]:
    response = client.esql.query(
        query="""
        FROM docs-chunks
        | WHERE status == "published"
        | EVAL missing_title = title IS NULL
        | EVAL missing_heading = section_heading IS NULL
        | STATS
            chunks = COUNT(*),
            missing_titles = COUNT(*) WHERE missing_title,
            missing_headings = COUNT(*) WHERE missing_heading
          BY product
        | SORT chunks DESC
        """
    )

    return response.body
