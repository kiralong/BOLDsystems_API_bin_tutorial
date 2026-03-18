# BOLDsystems API BIN Tutorial

Tutorial on how to use the new BOLDsystems (Barcode of Life Database) v5 API to get data based on BINs (Barcode Index Numbers). This tutorial is for beginners trying to use an API for the first time. We will be using the BOLDsystems API to request data from their database based on BIN IDs. This tutorial will hopefully also be a good starting point to use the API for other data requests as well.

## Table of Contents

1. [Introduction to APIs](#introduction-to-apis)
2. [The BOLDsystems API](#the-boldsystems-api)
3. [Scripting your API requests with python](#scripting-your-api-requests-with-python)

## Introduction to APIs

If you are a biologist, like me, who has never used an API before but suddenly needs to download a bunch of data from the BOLDsystems database... then this is the tutorial for you! Let's start off with some basics first.

### What is an API????

API stands for "Application Programming Interface", and an API allows two systems to talk to each other and share data over the internet with a set of rules, largely consisting of "requests" from one system, and "responses" from the other. The API is essentailly a go-between or fence between you (The user wanting data) and a large online system (in our particualr case, this is the BOLDsystems database). APIs allow users to query a large database without the data host giving users free reign to muck about in their database/system. Most large companies have APIs (Amazon web services, Google, etc) which allow users to script ways to request data from their systems.

### What is a REST API???

REST APIs are the most common type of API found online today. And, as you may have guessed, the BOLDsystems API is a REST API... but how can an API rest???? REST stands for Representational State Transfer. The main thing that sets a REST API apart from the other flavors of API's (e.g. SOAP APIs, RPC APIs, and Websocket APIs) is that REST APIs are stateless. This means that each interaction with the system is independent and infromation is not stored between requests (e.g., the client's state is not retained by the server). This, however, does mean that the user (or client) needs to provide the API with EVERYTHING it needs to process your requests EVERY time, and then the server (in this case, BOLD) will provide a response in plain text. Overall, REST defines a set of functions like `GET`, `PUT`, `DELETE`, etc. that users can use to access server data. Most of the time, if you are trying to get data off of a web service, you will be using `GET`. This limited defined list of functions allows the API to get you what you need from the server without every user on the internet having a free for all with the data. Under the hood, this is using HTTP/HTTPS (which you may recognize as the part at the being of website URLs) to send and receive data over the internet.

>Fun Fact: REST APIs were first introduced in a PhD disseration in 2000!

## The BOLDsystems API

[BOLDsystems](https://www.boldsystems.org/) has recently (as of March 2026) introduced a new version (version 5) of their database, with a more streamlined [barcode search function](https://id.boldsystems.org/) and fancy new [API](https://boldsystems.org/data/api/). See the BOLD API [documentation page](https://portal.boldsystems.org/api/docs) that lists each of the main fucntions of the API and it allows you to "try out" each of the protocols, which we will be using in the below steps to get used to how these work.

### Step 1: parse

First, we need to format our request correctly with all the information the API needs. If you're starting from scratch, it may be best to start with /api/query/parse to format your request correctly.

From the BOLD API docs on [/api/query/parse](https://portal.boldsystems.org/api/docs#/query/query_terms_parsing_api_query_parse_get):
> A service that accepts a free text query string and parse it into a semicolon separated list of triplets of search terms in the following format scope:rank:term.
> query: String where multiple search terms are separated by space with the optional scope specified as [scope] after a term. Double quote (") must be used to specify multi-word search term. Single quote can be used as part of a word/phrase. Example: Ontario "Homo sapiens" [tax] will be parsed into tax:na:Homo sapiens;na:na:Ontario

Essentially, "parse" just makes a best effort to understand your plain language query and convert it to a possible query in the "triplets" format. The format for each triplet is [scope]:[subscope]:[value]. Note that you don't always have to use all 3 parts of a "triplet" with BOLD, you could use only 1 or 2 parts.

For example, we gave it `"BOLD:ACQ9269" [bin]` in the `Query` field of [/api/query/parse](https://portal.boldsystems.org/api/docs#/query/query_terms_parsing_api_query_parse_get).

We are given the following `curl` command from the docs page. This `curl` command is the code for the request we are sending the API. `curl` is a command-line tool that transfers data primarily using HTTP/HTTPS and is how we are sending out `GET` reqeust to the API over the internet. See the actual command for the request below:

```bash
/api/query/parse
    curl -X 'GET' \
    'https://portal.boldsystems.org/api/query/parse?query=%22BOLD%3AACQ9269%22%20%5Bbin%5D' \
    -H 'accept: application/json'
```

And "parse" responds with:

```json
    {
    "terms": "bin:na:BOLD:ACQ9269",
    "ignored_terms": []
    }
```

In the term we have received from the API, we have `bin` as the scope, `na` as the subscope, and `BOLD:ACQ9269` (the BIN ID we actually want information/data on) as the value. Notice the "na" as the subscope - we're closer to formulating a full query term, but we're still not done.

### Step 2: preprocessor

Now, we need to preprocess the parsed bin triplet with the "na" - essentially another step to validate and correct anything about the triplet identifier to ensure it's as correct as it can be.

The BOLD docs on [/api/query/preprocessor](https://portal.boldsystems.org/api/docs#/query/resolve_query_api_query_preprocessor_get):
> Processes and resolves query tokens if matches are found. If matches are not found, will attempt to infer possible values for the intended search and return successfully. If triplet token cannot be resolved unambiguously, will return possible values but return as an error. If no tokens are processed, will also return an error.
> query: A semicolon delimited set of "triplet" tokens. The format for each triplet is [scope]:[subscope]:[value], but can also accept "doublet" ([scope]:[value]) and "singleton" ([value]) tokens.

For example, we next give [/api/query/preprocessor](https://portal.boldsystems.org/api/docs#/query/resolve_query_api_query_preprocessor_get) `bin:na:BOLD:ACQ9269` (the search term given to us in the previous step by `/api/query/parse`) into the `Query` field.

We are given the following `curl` command request. We can see it very similar to the prevous one:

```bash
curl -X 'GET' \
  'https://portal.boldsystems.org/api/query/preprocessor?query=%22bin%3Ana%3ABOLD%3AACQ9269%22' \
  -H 'accept: application/json'
```

And "preprocessor" responds with:

```json
{
  "successful_terms": [
    {
      "submitted": "\"bin:na:BOLD:ACQ9269\"",
      "matched": "bin:uri:BOLD:ACQ9269\""
    }
  ]
}
```

We now have our correctly formatted search term: `bin:uri:BOLD:ACQ9269`! To review the completed triplet format, we have the scope `bin`, the subscope `uri`, and the value `BOLD:ACQ9269`. Note that `uri` here stands for universal resource identifer.

### Step 3: query

Now that we have a preprocessed query, we make the actual query to get our query id. The query id is then used by subsequent API commands.

From the BOLD API docs on [/api/query](https://portal.boldsystems.org/api/docs#/query/query_records_api_query_get):
>A query endpoint to retrieve records from "triplet" search terms. Scopes are tax, geo, ids, bin, and recordsetcode. This queries the DB and saves the results to a tmp location, then it returns the query_id to the user.
>query: A semicolon delimited set of "triplet" tokens. The format for each triplet is [scope]:[subscope]:[value]
>extent: Set the number of document IDs to fetch (zero = 0 (query not run), full = all, others mappings found in EXTENT_MAP)

Now, we give `/api/query` our formatted triplet search term `bin:uri:BOLD:ACQ9269`. Again, the command-line request is:

```bash
curl -X 'GET' \
  'https://portal.boldsystems.org/api/query?query=bin%3Auri%3ABOLD%3AACQ9269&extent=limited' \
  -H 'accept: application/json'
```

And "query" responds with:

```json
{
  "query_id": "eAFLysyzKi3KtHLy93GxcnQOtDQys7TOyczNLElNAQCEUgkr",
  "extent_limit": 1000
}
```

Now we have our query id `eAFLysyzKi3KtHLy93GxcnQOtDQys7TOyczNLElNAQCEUgkr`, which we can finally use to get to some real data!

### Step 4: Get a BIN's taxonomy summary

Next, let's pull a summary of the taxonomy of our BIN of interest.

From the BOLD docs on [/api/taxonomy/{query_id}](https://portal.boldsystems.org/api/docs#/taxonomy/generate_taxonomy_summary_api_taxonomy__query_id__get):
>Generate a taxonomy summary from an encoded query (query_id). Returns a frequency of taxonomy names found in query by rank.
>query_id: Encoded triplets query from /api/query

Now give `/api/taxonomy/{query_id}` the query id we got from `query`: `eAFLysyzKi3KtHLy93GxcnQOtDQys7TOyczNLElNAQCEUgkr` and `/api/taxonomy/{query_id}` responds with:

```json
{
  "taxonomy": {
    "kingdom": {
      "Animalia": 13
    },
    "phylum": {
      "Arthropoda": 13
    },
    "class": {
      "Insecta": 13
    },
    "order": {
      "Diptera": 13
    },
    "family": {
      "Chironomidae": 13
    },
    "subfamily": {
      "Diamesinae": 13
    },
    "tribe": {
      "Diamesini": 13
    },
    "genus": {
      "Diamesa": 13
    },
    "species": {
      "Diamesa hamaticornis": 1,
      "Diamesa nr. hyperborea": 4,
      "Diamesa hyperborea": 1
    },
    "subspecies": {}
  }
}
```

And now we have successfully extracted data on a BIN based on it's URI from the BOLDsystems database!!!! Every API protol that lists {query_id} we can now use!

## Scripting your API requests with python

Now that we have successfully navigated getting data for a single BIN request using the BOLD API docs page, we want to be able to write a script to make and aggregate a bunch of requests for us, instead of doing each request manually.

While there was an R package to connect to BOLD v4 (and I'm sure they're updating the R package for use with v5), this guide is exploring an alternative way to interface with the API using python. We will be using the python library [requests](https://requests.readthedocs.io/en/latest/user/quickstart/). This python library uses, you guessed it, HTTP to make data requests over the internet! Exactly what we need to work with an API.

First, for our header line of our script, we are going to use:

```python
#!/usr/bin/env -S uv run --script --with requests
```

Here, we are using `uv` to manage our `python` project. [`uv`](https://docs.astral.sh/uv/) is a python package manager, follow the `uv` [installation instructions](https://docs.astral.sh/uv/getting-started/installation/) to get started. You'll notice you can use `curl` once again to install `uv` too!

Our header line says to run an environment in python running a script with the `requests` package.

Next, we need to [install `requests`](https://requests.readthedocs.io/en/latest/user/install/#install). And then import it at the top of your script.

```python
import requests
```

Now, because we already know how to structure our "triplet" requests, we can skip `parse` and `preprocessor` and jump straight to `query` to get our `query_id`.
