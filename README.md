# BOLDsystems API BIN Tutorial

Tutorial on how to use the new BOLDsystems V5 API to get data based on BINs.
This tutorial is for beginners trying to use an API for the first time. We will be using the BOLDsystems API to request data from their database based on BIN IDs. This tutorial will hopefully also be a good starting point to use the API for other data requests as well.

## Table of Contents

1. [Introduction to APIs](#introduction-to-apis)
2. [The BOLDsystems API](#the-boldsystems-api)

## Introduction to APIs

If you are a biologist, like me, who has never used an API before but suddenly needs to download a bunch of data from the BOLDsystems database... then this is the tutorial for you! Let's start off with some basics first.

### What is an API????

API stands for "Application Programming Interface", and an API allows two systems to talk to each other and share data over the internet with a set of rules, largely consisting of "requests" from one system, and "responses" from the other. The API is essentailly a go-between or fence between you (The user wanting data) and a large online system (in our particualr case, this is the BOLDsystems database). APIs allow users to query a large database without the data host giving users free reign to muck about in their database/system. Most large companies have APIs (Amazon web services, Google, etc) which allow users to script ways to request data from their systems.

### What is a REST API???

REST APIs are the most common type of API found online today. And, as you may have guessed, the BOLDsystems API is a REST API... but how can an API rest???? REST stands for Representational State Transfer. The main thing that sets a REST API apart from the other flavors of API's (e.g. SOAP APIs, RPC APIs, and Websocket APIs) is that REST APIs have "statelessness".

## The BOLDsystems API

[BOLDsystems](https://www.boldsystems.org/) has recently (as of March 2026) introduced a new version (version 5) of their database, with a more streamlined [barcode search function](https://id.boldsystems.org/) and fancy new [API](https://boldsystems.org/data/api/).

### Step 1: parse

First, we could start with /api/query/parse
> A service that accepts a free text query string and parse it into a semicolon separated list of triplets of search terms in the following format <scope>:<rank>:<term>.
> query: String where multiple search terms are separated by space with the optional scope specified as [scope] after a term. Double quote (") must be used to specify multi-word search term. Single quote can be used as part of a word/phrase. Example) Ontario "Homo sapiens" [tax] will be parsed into tax:na:Homo sapiens;na:na:Ontario

Essentially, "parse" just makes a best effort to understand your plain language query and convert it to a possible query in the "triplets" format.

For example, we gave it `"BOLD:ACQ9269" [bin]`.

```bash
/api/query/parse
    curl -X 'GET' \
    'https://portal.boldsystems.org/api/query/parse?query=%22BOLD%3AACQ9269%22%20%5Bbin%5D' \
    -H 'accept: application/json'
```

And "parse" responds with:

```bash
    {
    "terms": "bin:na:BOLD:ACQ9269",
    "ignored_terms": []
    }
```

Notice the "na" as the subscope - we're closer, but we're still not done.

### Step 2: preprocessor

Now, let's preprocess the parsed bin triplet with the "na" - essentially another step to validate and correct anything about the triplet identifier to ensure it's as correct as it can be.

/api/query/preprocessor
> Processes and resolves query tokens if matches are found. If matches are not found, will attempt to infer possible values for the intended search and return successfully. If triplet token cannot be resolved unambiguously, will return possible values but return as an error. If no tokens are processed, will also return an error.
> query: A semicolon delimited set of "triplet" tokens. The format for each triplet is [scope]:[subscope]:[value], but can also accept "doublet" ([scope]:[value]) and "singleton" ([value]) tokens.
