# Code example from Context Engineering with Elasticsearch book
# Copyright 2026 by Enrico Zimuel. All rights reserved.

import tiktoken

text = "Basketball is a great game."

enc = tiktoken.encoding_for_model("gpt-4o")
token_ids = enc.encode(text)
round_trip = enc.decode(token_ids)

print("Text:", text)
print("Token IDs:", token_ids)
for token_id in token_ids:
    decoded_token = enc.decode([token_id])
    print (f"\tToken ID: {token_id}, Decoded: '{decoded_token}'")
print("Decoded:", round_trip)
print("Token count:", len(token_ids))
