import json

# JSON vuoto
empty_data = {}

# Scrivi nel file ratings.json
with open("ratings.json", "w") as f:
    json.dump(empty_data, f)

print("File ratings.json ripristinato con un JSON vuoto.")
