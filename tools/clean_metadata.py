import json
import os


METADATA_FILE = (
    r"C:\OllamaAI\knowledge\metadata.json"
)


def main():

    if not os.path.exists(
        METADATA_FILE
    ):

        print(
            "Metadata file not found."
        )

        return

    with open(
        METADATA_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        data = json.load(f)

    documents = data.get(
        "documents",
        {}
    )

    cleaned = {}

    for source, info in documents.items():

        title = info.get(
            "title",
            ""
        )

        if (
            "test_ems" in source.lower()
            or "ems training test"
            in title.lower()
        ):

            continue

        cleaned[source] = info

    cleaned[
        r"C:\OllamaAI\documents\test_ems.txt"
    ] = {

        "title":
            "EMS Training Test",

        "source":
            r"C:\OllamaAI\documents\test_ems.txt",

        "jurisdiction":
            "TEST",

        "document_type":
            "TRAINING",

        "effective_date":
            "2026-08-15",

        "status":
            "TRAINING"
    }

    output = {
        "documents": cleaned
    }

    with open(
        METADATA_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            output,
            f,
            indent=4,
            ensure_ascii=False
        )

    print("")
    print(
        "Metadata cleanup complete."
    )

    print(
        "Documents:",
        len(cleaned)
    )


if __name__ == "__main__":

    main()