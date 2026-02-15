pet = {
    "type": "object",
    "required": ["name", "type"],
    "properties": {
        "id": {
            "type": "integer"
        },
        "name": {
            "type": "string"
        },
        "type": {
            "type": "string",
            "enum": ["cat", "dog", "fish"]
        },
        "status": {
            "type": "string",
            "enum": ["available", "sold", "pending"]
        },
    }
}

order = {
    "type": "object",
    "required": ["id", "pet_id", "quantity", "status"],
    "properties": {
        "id": {"type": "integer"},
        "pet_id": {"type": "integer"},
        "quantity": {"type": "integer"},
        "status": {"type": "string", "enum": ["placed", "approved", "delivered"]}
    }
}
