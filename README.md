# Context Engineering with Elasticsearch

This repository contains the source code of the book [Context Engineering with Elasticsearch]() by [Enrico Zimuel](https://www.zimuel.it).

The examples are divided by Chapters, as follows:

- [Chapter 1](chapter1/): Context Engineering for LLM Apps
- [Chapter 2](chapter2/): Information Retrieval Fundamentals, and How to Measure It
- Chapter 3:
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
