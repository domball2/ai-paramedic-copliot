import json
import os


BASE = r"C:\OllamaAI"

DOCUMENT_DIR = os.path.join(
    BASE,
    "documents"
)

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

    print("")
    print("========================================")
    print("       REFERENCE VALIDATION")
    print("========================================")
    print("")

    if not documents:

        print("No registered references.")
        return

    valid = 0
    missing = 0

    for source, metadata in documents.items():

        path = os.path.join(
            DOCUMENT_DIR,
            source
        )

        exists = os.path.isfile(path)

        print(
            f"{'OK' if exists else 'MISSING'}  "
            f"{source}"
        )

        if exists:
            valid += 1
        else:
            missing += 1

    print("")
    print(
        f"Valid: {valid}"
    )

    print(
        f"Missing: {missing}"
    )

    print("")


if __name__ == "__main__":
    main()