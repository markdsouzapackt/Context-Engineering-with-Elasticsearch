# Context Engineering with Elasticsearch

This repository contains the source code of the book [Context Engineering with Elasticsearch]() by [Enrico Zimuel](https://www.zimuel.it).

The examples are divided by Chapters, as follows:

- [Chapter 1](chapter1/): Context Engineering for LLM Apps
- [Chapter 2](chapter2/): Information Retrieval Fundamentals, and How to Measure It
- [Chapter 3](chapter3/): Elasticsearch Core Retrieval Mechanics
- Chapter 4:
- Chapter 5:
- Chapter 6:
- Chapter 7:
- Chapter 8:
- Chapter 9:
- Chapter 10:

## Install the project examples

To install the Python examples, you can create and activate a virtual
environment ([venv](https://docs.python.org/3/library/venv.html)).

Use the following commands from the root folder of the repository:

```bash
python -m venv .venv
source .venv/bin/activate
```

After, you can install all the required packages as follows:

```bash
pip install -r requirements.txt
```

To be able to use the spaCY libraries, we need to install also the [en_core_web_sm](https://spacy.io/models/en) model for manipulating english sentences.
This can be done using the following command:

```bash
python -m spacy download en_core_web_sm
```

In order to execute the examples, you need to configure the `.env` file.
You can generate this file copying the `.env.dev` template file, as follows:

```bash
cp .env.dev .env
```

And then you can edit the `.env` file with your settings about Elasticsearch and OpenAI.Some of the examples require an API key, read the next section for Elasticsearch.

## Install Elasticsearch

To execute the examples reported in this repository you need to have an
instance of [Elasticsearch](https://www.elastic.co/elasticsearch) running. You can register for a free trial on
[Elastic Cloud](https://www.elastic.co/cloud/cloud-trial-overview) or install a local instance of Elasticsearch on your computer.

To install locally, you need to execute this command in the terminal:

```bash
curl -fsSL https://elastic.co/start-local | sh
```

This will install Elasticsearch and [Kibana](https://www.elastic.co/kibana) on macOS, Linux and Windows (using WSL).

## Execute the Python examples

You can execute the python examples from the command line, as follows:

```bash
python -m chapter1.token
```

This will execute the Python script [chapter1/token.py](chapter1/token.py).
For some chapters is important to execute the examples in order because they use some data stored in some previous scripts in Elasticsearch.
Below is reported the order of execution for each chapter. This order reflects also the position of the examples in each chapter of the book.

### Chapter 1

1. [token.py](chapter1/token.py)
2. [tool_calling.py](chapter1/tool_calling.py)
3. [elasticsearch.py](chapter1/elasticsearch.py)
4. [simple_rag.py](chapter1/simple_rag.py)

### Chapter 2

1. [stopwords.py](chapter2/stopwords.py)
2. [custom_stopwords.py](chapter2/custom_stopwords.py)
3. [lemmization.py](chapter2/lemmization.py)
4. [analyzer.py](chapter2/analyzer.py)
5. [analyzer_filter.py](chapter2/analyze_filter.py)
6. [simple_search.py](chapter2/simple_search.py)
7. [rank_eval.py](chapter2/rank_eval.py)

### Chapter 3

1. [mapping_and_index.py](chapter3/mapping_and_index.py) (create the `rag_context_chunks` index)
2. [queries.py](chapter3/queries.py)
3. [filter.py](chapter3/filter.py)
4. [function_score.py](chapter3/function_score.py)
5. [esql.py](chapter3/esql.py)
6. [profile.py](chapter3/profile.py)
7. [explain.py](chapter3/explain.py)
8. [ingest_pipeline_rag.py](chapter3/ingest_pipeline_rag.py)
