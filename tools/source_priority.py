import json
import os


BASE = r"C:\OllamaAI"

HIERARCHY_FILE = os.path.join(
    BASE,
    "knowledge",
    "source_hierarchy.json"
)


def load_hierarchy():

    with open(
        HIERARCHY_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


def get_priority(metadata):

    hierarchy = load_hierarchy()

    category = metadata.get(
        "category",
        "uncategorized"
    ).lower()

    source = hierarchy.get(
        category,
        hierarchy["uncategorized"]
    )

    return {
        "category": category,
        "priority": source["priority"],
        "trust_level": source["trust_level"],
        "description": source["description"]
    }


def main():

    examples = [

        {
            "category": "protocols"
        },

        {
            "category": "training"
        },

        {
            "category": "uncategorized"
        }
    ]

    for example in examples:

        result = get_priority(
            example
        )

        print("")
        print(
            result
        )


if __name__ == "__main__":
    main()