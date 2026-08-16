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

    if not os.path.exists(
        METADATA_FILE
    ):

        return {
            "documents": {}
        }

    with open(
        METADATA_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


def save_metadata(data):

    os.makedirs(
        os.path.dirname(
            METADATA_FILE
        ),
        exist_ok=True
    )

    with open(
        METADATA_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            indent=4,
            ensure_ascii=False
        )


def find_documents():

    documents = []

    for root, directories, files in os.walk(
        DOCUMENT_DIR
    ):

        for filename in files:

            if not filename.lower().endswith(
                (".txt", ".pdf")
            ):
                continue

            full_path = os.path.join(
                root,
                filename
            )

            relative_path = os.path.relpath(
                full_path,
                DOCUMENT_DIR
            )

            documents.append(
                relative_path
            )

    return documents


def get_category(relative_path):

    parts = relative_path.split(
        os.sep
    )

    if len(parts) > 1:
        return parts[0]

    return "uncategorized"


def main():

    data = load_metadata()

    documents = data.setdefault(
        "documents",
        {}
    )

    files = find_documents()

    print("")
    print(
        "========================================"
    )
    print(
        "       PARAMEDIC AI METADATA SYNC"
    )
    print(
        "========================================"
    )
    print("")

    print(
        "Documents found:",
        len(files)
    )

    for relative_path in files:

        category = get_category(
            relative_path
        )

        existing = documents.get(
            relative_path,
            {}
        )

        print("")
        print(
            "Document:",
            relative_path
        )

        print(
            "Category:",
            category
        )

        title = existing.get(
            "title",
            os.path.splitext(
                os.path.basename(
                    relative_path
                )
            )[0]
        )

        jurisdiction = existing.get(
            "jurisdiction",
            "UNSPECIFIED"
        )

        document_type = existing.get(
            "document_type",
            category.upper()
        )

        effective_date = existing.get(
            "effective_date",
            "UNKNOWN"
        )

        status = existing.get(
            "status",
            "TRAINING"
        )

        documents[relative_path] = {

            "title":
                title,

            "source":
                relative_path,

            "category":
                category,

            "jurisdiction":
                jurisdiction,

            "document_type":
                document_type,

            "effective_date":
                effective_date,

            "status":
                status
        }

    save_metadata(data)

    print("")
    print(
        "Metadata synchronized."
    )
    print("")


if __name__ == "__main__":

    main()