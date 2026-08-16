import json
import os


BASE = r"C:\OllamaAI"

METADATA_FILE = os.path.join(
    BASE,
    "knowledge",
    "metadata.json"
)

DOCUMENT_DIR = os.path.join(
    BASE,
    "documents"
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

    print("")
    print("=" * 90)
    print("                 PARAMEDIC AI REFERENCE DASHBOARD")
    print("=" * 90)
    print("")

    if not documents:

        print("No references registered.")
        return

    print(
        f"{'SOURCE':35} "
        f"{'CATEGORY':15} "
        f"{'STATUS':12} "
        f"{'JURISDICTION':20}"
    )

    print("-" * 90)

    for source, metadata in documents.items():

        path = os.path.join(
            DOCUMENT_DIR,
            source
        )

        exists = os.path.isfile(path)

        marker = "OK" if exists else "MISSING"

        category = metadata.get(
            "category",
            "UNKNOWN"
        )

        status = metadata.get(
            "status",
            "UNKNOWN"
        )

        jurisdiction = metadata.get(
            "jurisdiction",
            "UNKNOWN"
        )

        print(
            f"{marker:7} "
            f"{source[:35]:35} "
            f"{category[:15]:15} "
            f"{status[:12]:12} "
            f"{jurisdiction[:20]:20}"
        )

    print("")
    print("=" * 90)
    print(
        f"Total references: {len(documents)}"
    )
    print("=" * 90)
    print("")


if __name__ == "__main__":
    main()