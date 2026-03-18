#!/usr/bin/env -S uv run --script --with requests

# Get Genus and List of Species from BINs in the BoldSystem database.

import requests

"""
We will skip the "parse" and "preprocessor" stages, which are optional. We only need the "query" step (the part that actually does something).
We can skip the "parse" and "preprocessor" stages because we know how to format the "triplet" query specifiers properly for BINs (after
verifying their format via the preprocessor manually first i.e. for a BIN, ).

Just to demonstrate what would happen if we DID go through the "parse" and "preprocessor" steps, here's a demo.

# Parse
-------

First, we could start with /api/query/parse
> A service that accepts a free text query string and parse it into a semicolon separated list of triplets of search terms in the following format <scope>:<rank>:<term>.
> query: String where multiple search terms are separated by space with the optional scope specified as [scope] after a term. Double quote (") must be used to specify multi-word search term. Single quote can be used as part of a word/phrase. Example) Ontario "Homo sapiens" [tax] will be parsed into tax:na:Homo sapiens;na:na:Ontario

Essentially, "parse" just makes a best effort to understand your plain language query and convert it to a possible query in the "triplets" format. 
For example, we gave it `"BOLD:ACQ9269" [bin]`.
/api/query/parse
    curl -X 'GET' \
    'https://portal.boldsystems.org/api/query/parse?query=%22BOLD%3AACQ9269%22%20%5Bbin%5D' \
    -H 'accept: application/json'

And "parse" responds with:
    {
    "terms": "bin:na:BOLD:ACQ9269",
    "ignored_terms": []
    }

Notice the "na" as the subscope - we're closer, but we're still not done.

# Preprocessor
--------------

Now, let's preprocess the parsed bin triplet with the "na" - essentially another step to validate and correct anything about the triplet identifier to ensure it's as correct as it can be.
/api/query/preprocessor
> Processes and resolves query tokens if matches are found. If matches are not found, will attempt to infer possible values for the intended search and return successfully. If triplet token cannot be resolved unambiguously, will return possible values but return as an error. If no tokens are processed, will also return an error.
> query: A semicolon delimited set of "triplet" tokens. The format for each triplet is [scope]:[subscope]:[value], but can also accept "doublet" ([scope]:[value]) and "singleton" ([value]) tokens.


"""

# TODO: Replace with an input file which is a LIST of bins.
TARGET_BIN = "BOLD:ACQ9269"

# https://portal.boldsystems.org/api/docs
API_BASE_URL="https://portal.boldsystems.org/api"
HEADERS = {'accept': 'application/json'}

# STEP 1: We need to feed our bin URI (universal resource identifer) into the /api/query/preprocessor:
# > Processes and resolves query tokens if matches are found. If matches are not found, will attempt 
# > to infer possible values for the intended search and return successfully. If triplet token cannot 
# > be resolved unambiguously, will return possible values but return as an error.
# response = requests.get(f"{API_BASE_URL}/query/preprocessor", headers=HEADERS, params={"query": f"bin:na:{TARGET_BIN}"})
# assert response.status_code == 200
# We get back: A preprpocessed query to be used in the actual query step
# Response:
# {
#   "successful_terms": [
#     {
#       "submitted": "bin:uri:BOLD:ACQ9269",
#       "matched": "ids:processid:ACQ9269;ids:sampleid:ACQ9269;ids:insdcacs:ACQ9269"
#     }
#   ]
# }
# queries = [successful_term.get('matched') for successful_term in response.json()["successful_terms"]]


# # STEP 1: We need to get the query id (which we already know the format as bin:uri:TARGET_BIN from parse and preprocessor)
# # TODO Add a foreach here, but for now just do the first
# # query = queries[0]
# query = f"bin:uri:{TARGET_BIN}"
# response = requests.get(f"{API_BASE_URL}/query", headers=HEADERS, params={"extent": "limited", "query": query})
# assert response.status_code == 200
# # Response: {
# #   "query_id": "eAHLTCm2yswrTklOTC62cnQOtDQys7TOBAoWFOUnpxYXZ6agiBYn5hbkpCIJ5mTmZpakpgAAbVsYJg==",
# #   "extent_limit": 1000
# # }
# query_id = response.json()["query_id"]

# # https://portal.boldsystems.org/api/documents/<query_id>/download?format=json

# response = requests.get(f"{API_BASE_URL}/documents/{query_id}/download", headers=HEADERS, params={"format": "json"})
# #assert response.status_code == 200

# response = requests.get(f"{API_BASE_URL}/taxonomy/{query_id}", headers=HEADERS, params={"format": "json"})
# # To see what response has
# print(response.text)

# # Pull out the genus information
# # Save the taxonomy summary into a data variable
# taxa_data = response.json()

# # See the dictionary keys
# list(taxa_data.keys())

# # Returns ['taxonomy']
# list(taxa_data['taxonomy'].keys())
# # Returns ['kingdom', 'phylum', 'class', 'order', 'family', 'subfamily', 'tribe', 'genus', 'species', 'subspecies']

# # See what is in the dictionary genus
# print(taxa_data['taxonomy']["genus"])

# # Save just the key from genus into variable genus and make it a string
# genus = str(list(taxa_data['taxonomy']["genus"].keys()))

# Now to make a loop to read in list of BINs, pull the taxonomy info, and populate a final list with the genus
file_path = 'BIN_list.tsv'

count = 1
try:
    with open(file_path, 'r') as file:
        for line in file:
            # The 'line' variable contains the current line, including the newline character '\n'
            # Use line.strip() to remove leading/trailing whitespace and the newline
            processed_line = line.strip()
            
            # Perform operations on the processed line (e.g., print it, store it, etc.)
            # check processed line
            # print(processed_line)

            TARGET_BIN = processed_line
            print(TARGET_BIN)
            query = f"bin:uri:{TARGET_BIN}"
            response = requests.get(f"{API_BASE_URL}/query", headers=HEADERS, params={"extent": "limited", "query": query})
            query_id = response.json()["query_id"]

            # Check query id is as expected
            # print(query_id)

            # Get taxonomy for the target bin using the query_id
            response = requests.get(f"{API_BASE_URL}/taxonomy/{query_id}", headers=HEADERS, params={"format": "json"})
            print(response.status_code)
            print(response.text)
            # Save the taxonomy summary into a data variable
            taxa_data = response.json()
            genus = str(list(taxa_data['taxonomy']["genus"].keys()))
            print(f"{count}:{genus}")
            count += 1
            #print(count) d
            #print(genus)


except FileNotFoundError:
    print(f"Error: The file '{file_path}' was not found.")

# NOTE this is failing at DIFFERENT lines each time...
