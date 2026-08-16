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


def save_metadata(data):

    os.makedirs(
        os.path.dirname(METADATA_FILE),
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


def ask(prompt, default=None):

    value = input(prompt).strip()

    if not value and default is not None:

        return default

    return value


def main():

    print("")
    print("========================================")
    print("       PARAMEDIC AI REFERENCE INTAKE")
    print("========================================")
    print("")

    source = ask(
        "Source path: "
    )

    if not source:

        print("Source path is required.")
        return

    title = ask(
        "Title: "
    )

    category = ask(
        "Category "
        "[protocols/training/medications/etc.]: "
    )

    jurisdiction = ask(
        "Jurisdiction [UNSPECIFIED]: ",
        "UNSPECIFIED"
    )

    document_type = ask(
        "Document type [REFERENCE]: ",
        "REFERENCE"
    )

    effective_date = ask(
        "Effective date [UNKNOWN]: ",
        "UNKNOWN"
    )

    status = ask(
        "Status "
        "[CURRENT/ARCHIVED/TRAINING/UNKNOWN]: ",
        "UNKNOWN"
    ).upper()

    notes = ask(
        "Notes [none]: ",
        ""
    )

    metadata = load_metadata()

    documents = metadata.setdefault(
        "documents",
        {}
    )

    documents[source] = {

        "title": title,

        "source": source,

        "category": category,

        "jurisdiction": jurisdiction,

        "document_type": document_type,

        "effective_date": effective_date,

        "status": status,

        "notes": notes
    }

    save_metadata(metadata)

    print("")
    print("Reference registered.")
    print("")
    print(
        "IMPORTANT:"
    )
    print(
        "Registering a document does not"
    )
    print(
        "make it a current operational protocol."
    )
    print("")


if __name__ == "__main__":

    main()