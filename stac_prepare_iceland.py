import os
import json
import pystac
import requests

DATA_DIRECTORY = "/home/user/Code/devseed/data/sentinel2-l2a-iceland"

catalog_path = os.path.join(DATA_DIRECTORY, 'catalog.json')

# Load the catalog and its collection using pystac
try:
    catalog = pystac.Catalog.from_file(catalog_path)
    print("Catalog loaded successfully:")

    # Iterate over collections in the catalog
    for collection in catalog.get_collections():
        print(f"Loading collection: {collection.id}")

        # Construct the path to the collection.json file
        collection_path = os.path.join(DATA_DIRECTORY, collection.id, 'collection.json')

        # Load the collection
        collection_data = pystac.Collection.from_file(collection_path)
        print(f"Collection loaded successfully: {collection_data.id}")

        # Create a directory for items if it doesn't exist
        items_directory = os.path.join(DATA_DIRECTORY, collection.id)
        os.makedirs(items_directory, exist_ok=True)

except Exception as e:
    print(f"Error loading catalog: {e}")

# Obtain items from Earth Search API
url = "https://earth-search.aws.element84.com/v1/search"
payload = {
    "collections": ["sentinel-2-l2a"],
    "bbox": [-24.95, 63.38, -13.99, 66.56],
    "datetime": "2023-01-01T00:00:00Z/2023-12-31T23:59:59Z",
    "limit": 1,
    "query": {
        "eo:cloud_cover": {
            "lt": 5
        }
    }
}

# Make the POST request
response = requests.post(url, json=payload)

# Check if the request was successful
if response.status_code == 200:
    data = response.json()

    items_list = {
        "type": "FeatureCollection",
        "features": []
    }

    # Process the results with pystac
    for item in data.get('features', []):
        stac_item = pystac.Item.from_dict(item)
        print(f"Fetched Item ID: {stac_item.id}, Date: {stac_item.datetime}")

        # Filter out assets with 'jp2' in their href
        filtered_assets = {k: v for k, v in stac_item.assets.items() if 'jp2' not in v.href}
        stac_item.assets = filtered_assets

        items_list["features"].append(stac_item.to_dict())  # Append STAC item to the features list

    # Write items to items.json
    items_json_path = os.path.join(items_directory, 'items.json')
    with open(items_json_path, 'w') as f:

        # # Write readible list of features-
        # json.dump(items_list, f, indent=2)

        # Write each feature on a new line (pgstac wants that)
        for feature in items_list["features"]:
            json.dump(feature, f)
            f.write('\n')

    print(f"Items saved to {items_json_path}")

else:
    print(f"Request failed with status code {response.status_code}: {response.text}")
