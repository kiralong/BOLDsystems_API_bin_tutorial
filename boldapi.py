#!/usr/bin/env -S uv run --script --with requests

# Get Genus and List of Species from BINs in the BoldSystem database.

import requests
import time
import json
from datetime import datetime

# We had some problems with 503 Service Unavialable responses, which we suspect is due to rate limitng.
# So if we encounter API errors, we'll back off and wait to give the API time to recover and give us
# access again.
REQUEST_MAX_RETRIES = 3
BASE_BACKOFF_SECONDS = 20

# https://portal.boldsystems.org/api/docs
API_BASE_URL = "https://portal.boldsystems.org/api"
HEADERS = {"accept": "application/json"}

# Now to make a loop to read in list of BINs, pull the taxonomy info, and populate a final list with the genus
FILE_PATH = "BIN_list.tsv"

bins = []
# Load bins from file.
try:
    with open(FILE_PATH, "r") as file:
        # Assumes no header line.
        for line in file:
            # The 'line' variable contains the current line, including the newline character '\n'
            # Use line.strip() to remove leading/trailing whitespace and the newline
            bins.append(line.strip())
except FileNotFoundError:
    print(f"Error: The file '{FILE_PATH}' was not found.")


# NOTE: While we can supply a list of bins to the query at the same time, 
# it returns an aggregate taxonomy summary which conflates all the bins together - so we won't be doing that.
# Instead, we'll request each bin - one by one.
# However, querying one-by-one can trigger rate limits to our usage, resulting in errors such as 503 Service unavailable.
# To avoid this, we capture errors and wait to let the system recover. We also sleep for 1 second in betweeen each query.
total_bins_count = len(bins)
count = 1
retries = 0
bin_to_taxonomy = {}
bin_errors = []
# TODO: Add caching by bin - bins may repeat!
for bin in bins:
    time.sleep(1) 
    print(f"Processing bin #{count}/{total_bins_count}: {bin}")
    bin_query = f"bin:uri:{bin}"
    for i in range(1, REQUEST_MAX_RETRIES):
        try:
            response = requests.get(
                f"{API_BASE_URL}/query",
                headers=HEADERS,
                params={"extent": "limited", "query": bin_query},
            )
            print(f"Response for /query {bin}: {response.status_code} {response.text}")
            response_json = response.json()
        except requests.exceptions.JSONDecodeError as err:
            backoff_seconds = BASE_BACKOFF_SECONDS * (retries + 1)
            print(f"{bin_query} request failed - {type(err)}. Waiting {backoff_seconds} seconds.")
            time.sleep(backoff_seconds)
            # Note: Even if we skip one that hit max retries, we still should wait, to give the API
            # a chance for the next one.
            if retries == REQUEST_MAX_RETRIES and count != total_bins_count:
                print(f"ERROR: Max retries for {bin} /query. Skipping")
                bin_errors.append((bin, "/query"))
                break
            retries += 1
    
    # Reset retries for that try-except    
    retries = 0
    query_id = response_json["query_id"]
    print(f"bin: {bin} query_id: {query_id}")

    # Get taxonomy for the target bin using the query_id
    for i in range(1, REQUEST_MAX_RETRIES):
        try:
            response = requests.get(
                f"{API_BASE_URL}/taxonomy/{query_id}",
                headers=HEADERS,
                params={"format": "json"},
            )
            print(f"/taxonomy/{query_id} response - {response.status_code} {response.text}")
            response_json = response.json()
        except requests.exceptions.JSONDecodeError as err:
            backoff_seconds = BASE_BACKOFF_SECONDS * (retries + 1)
            print(f"{query_id} request failed - {type(err)}. Waiting {backoff_seconds} seconds.")
            time.sleep(backoff_seconds)
            # Note: Even if we skip one that hit max retries, we still should wait, to give the API
            # a chance for the next one.
            if retries == REQUEST_MAX_RETRIES and count != total_bins_count:
                print(f"ERROR: Max retries for {bin} /taxonomy/{query_id}. Skipping")
                bin_errors.append((bin, "/taxonomy/{query_id}"))
                break
            retries += 1

    genus = str(list(response_json["taxonomy"]["genus"].keys()))
    print(f"{count}:{genus}")
    bin_to_taxonomy[bin] = {
        "all": response_json,
        "genus": genus
    }

    count += 1
    print()

print(f"Summary of errors: {bin_errors}")

file_timestamp = datetime.today().strftime('%Y%m%d-%H%M%S')
print(f"Outputting to files {file_timestamp}*")

with open(f"{file_timestamp}-bin-taxa.json", "w") as output_json_file:
    json.dump(bin_to_taxonomy, output_json_file, indent=4)

# Create a new TSV with original bins and adding genuses.
with open(f"{file_timestamp}-bin-taxa.tsv", "w") as output_tsv_file:
    output_tsv_file.write("BIN\tBIN_Genus\n")
    for bin in bins:
        # Add NA when empty, and simple comma separated list otherwise.
        genus = bin_to_taxonomy[bin]["genus"]
        rendered_genus = "NA" if len(genus) == 0 else ','.join(genus)
        output_tsv_file.write(f"{bin}\t{rendered_genus}\n")

