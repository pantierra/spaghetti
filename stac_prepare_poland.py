import json
import pystac

def process_poland():
    with open("poland-data.json") as poland:
        lines = poland.readlines()
        edited_lines = []
        for idx, line in enumerate(lines):
            # if idx >= 1:
            #     break
            item = json.loads(line)
            assets = item["assets"]
            for asset_name, asset in assets.items():
                s3_href = asset["alternate"]["s3"]["href"]
                s3_auth_ref = asset["alternate"]["s3"]["auth:refs"]
                asset["href"] = s3_href
                asset["auth:refs"] = s3_auth_ref
                asset.pop("alternate:name")
                asset.pop("alternate")
            item["assets"] = assets
            item["stac_extensions"].remove("https://stac-extensions.github.io/alternate-assets/v1.2.0/schema.json")
            item["properties"]["auth:schemes"].pop("oidc")
            edited_lines.append(item)
            # print(item["properties"])
        with open("poland-edited.json", "w") as poland_edited:
            for line in edited_lines:
                json.dump(line, poland_edited)
                poland_edited.write('\n')
            # with open("single-modified.json", "w") as single:
            #     single.write(json.dumps(item, indent=2))
            # remove "https://stac-extensions.github.io/alternate-assets/v1.2.0/schema.json", from stac_extensions

def process_collection():
    with open("collection.json") as collection_file:
        collection = json.loads(collection_file.read())
        assets = collection["item_assets"]
        for asset_name, asset in assets.items():
            s3_auth_ref = asset["alternate"]["s3"]["auth:refs"]
            asset["auth:refs"] = s3_auth_ref
            asset.pop("alternate:name")
            asset.pop("alternate")
        collection["auth:schemes"].pop("oidc")
        collection["stac_extensions"].remove("https://stac-extensions.github.io/alternate-assets/v1.2.0/schema.json")
        with open("collection-edited.json", "w") as collection_edited:
            json.dump(collection, collection_edited, indent=2)

if __name__ == "__main__":
    #process_poland()
    process_collection()