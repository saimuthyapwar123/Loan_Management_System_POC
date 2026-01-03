from bson import ObjectId

def convert_objectid_to_str(doc: dict):
    """Recursively convert ObjectId fields to strings."""
    if isinstance(doc, dict):
        return {k: convert_objectid_to_str(v) for k, v in doc.items()}
    elif isinstance(doc, list):
        return [convert_objectid_to_str(i) for i in doc]
    elif isinstance(doc, ObjectId):
        return str(doc)
    else:
        return doc
