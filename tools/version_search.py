import json
import os


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


def is_current(metadata):

    status = metadata.get(
        "status",
        "UNKNOWN"
    ).upper()

    return status in [
        "CURRENT",
        "ACTIVE"
    ]


def select_sources(
    category=None,
    jurisdiction=None,
    current_only=False
):

    data = load_metadata()

    documents = data.get(
        "documents",
        {}
    )

    selected = []

    for source, metadata in documents.items():

        source_category = metadata.get(
            "category",
            "uncategorized"
        ).lower()

        source_jurisdiction = metadata.get(
            "jurisdiction",
            "UNKNOWN"
        ).lower()

        if category:

            if source_category != category.lower():
                continue

        if jurisdiction:

            if (
                source_jurisdiction
                != jurisdiction.lower()
            ):
                continue

        if current_only:

            if not is_current(metadata):
                continue

        selected.append({
            "source": source,
            "title": metadata.get(
                "title",
                source
            ),
            "category": source_category,
            "jurisdiction":
                metadata.get(
                    "jurisdiction",
                    "UNKNOWN"
                ),
            "status":
                metadata.get(
                    "status",
                    "UNKNOWN"
                ),
            "effective_date":
                metadata.get(
                    "effective_date",
                    "UNKNOWN"
                )
        })

    return selected


def main():

    print("")
    print("=" * 70)
    print("           VERSION-AWARE SOURCE SEARCH")
    print("=" * 70)
    print("")

    print("All references:")
    print("-" * 70)

    results = select_sources()

    for item in results:

        print(
            f"{item['status']:10} "
            f"{item['category']:15} "
            f"{item['source']}"
        )

    print("")
    print("Current/active references:")
    print("-" * 70)

    results = select_sources(
        current_only=True
    )

    if not results:

        print(
            "No CURRENT or ACTIVE references."
        )

    else:

        for item in results:

            print(
                f"{item['status']:10} "
                f"{item['category']:15} "
                f"{item['source']}"
            )

    print("")


if __name__ == "__main__":
    main()
