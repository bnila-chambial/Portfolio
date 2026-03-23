
import os
import glob
import json
import yaml
import xml.etree.ElementTree as ET

# ----------------------------------------------------
# Load YAML configuration
# ----------------------------------------------------
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

settings = config["xml_processing"]

input_dir = settings["input"]["directory"]
pattern = settings["input"]["file_pattern"]
recursive = settings["input"]["recursive"]

output_dir = settings["output"]["directory"]
os.makedirs(output_dir, exist_ok=True)

# ----------------------------------------------------
# Helper: apply transformations
# ----------------------------------------------------
def apply_transformations(record, rules):
    for rule in rules:
        t = rule["type"]
        target = rule["target"]

        if target not in record:
            continue

        if t == "uppercase":
            record[target] = record[target].upper() if record[target] else None

        elif t == "replace":
            if record[target]:
                record[target] = record[target].replace(
                    rule["from"], rule["to"]
                )

    return record

# ----------------------------------------------------
# Helper: simplified XPath resolver
# ----------------------------------------------------
def get_value(root, path):
    """
    xml.etree doesn't support full XPath, but supports simple paths like:
        book/title
        article/author/name
    """
    element = root.find(path)
    return element.text.strip() if element is not None and element.text else None

# ----------------------------------------------------
# Process each XML file
# ----------------------------------------------------
search_path = os.path.join(input_dir, pattern)
files = glob.glob(search_path, recursive=recursive)

results = []

for xml_file in files:
    tree = ET.parse(xml_file)
    root = tree.getroot()

    data = {}
    for field in settings["extraction"]["fields"]:
        # Remove leading slash if present (since ET does not use absolute paths)
        path = field["xpath"].lstrip("/")
        data[field["name"]] = get_value(root, path)

    # Apply transformations
    if settings["transformations"]["enabled"]:
        data = apply_transformations(data, settings["transformations"]["rules"])

    results.append(data)

# ----------------------------------------------------
# Save output
# ----------------------------------------------------
output_path = os.path.join(output_dir, "output.json")

with open(output_path, "w", encoding="utf-8") as f:
    if settings["output"]["pretty_print"]:
        json.dump(results, f, indent=4, ensure_ascii=False)
    else:
        json.dump(results, f, ensure_ascii=False)

print(f"✅ Processing complete! Output saved to {output_path}")
