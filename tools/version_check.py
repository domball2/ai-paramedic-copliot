import json
import os
from collections import defaultdict


BASE = r"C:\OllamaAI"

METADATA_FILE = os.path.join(
    BASE,
    "knowledge",
    "metadata.json"
)


def load_metadata():

    if not os.path.exists(METADATA_FILE):
        return {"documents": {}}

    with open(
        METADATA_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


def main():

    data = load_metadata()

    documents = data.get(
        "documents",
        {}
    )

    groups = defaultdict(list)

    for source, metadata in documents.items():

        category = metadata.get(
            "category",
            "uncategorized"
        )

        jurisdiction = metadata.get(
            "jurisdiction",
            "UNKNOWN"
        )

        key = (
            category.lower(),
            jurisdiction.lower()
        )

        groups[key].append(
            (source, metadata)
        )

    print("")
    print("=" * 80)
    print("             REFERENCE VERSION CHECK")
    print("=" * 80)
    print("")

    for key, references in groups.items():

        category, jurisdiction = key

        print(
            f"{category} / {jurisdiction}"
        )

        current_count = 0

        for source, metadata in references:

            status = metadata.get(
                "status",
                "UNKNOWN"
            ).upper()

            effective = metadata.get(
                "effective_date",
                "UNKNOWN"
            )

            print(
                f"  {status:10} "
                f"{effective:15} "
                f"{source}"
            )

            if status in [
                "CURRENT",
                "ACTIVE"
            ]:

                current_count += 1

        if current_count > 1:

            print("")
            print(
                "  WARNING: Multiple CURRENT "
                "versions detected."
            )

        print("")


if __name__ == "__main__":
    main()
