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


def main():

    data = load_metadata()

    documents = data.setdefault(
        "documents",
        {}
    )

    files = [

        filename

        for filename
        in os.listdir(
            DOCUMENT_DIR
        )

        if filename.lower().endswith(
            (".txt", ".pdf")
        )
    ]

    if not files:

        print(
            "No documents found."
        )

        return

    print("")
    print(
        "========================================"
    )
    print(
        "       PARAMEDIC AI METADATA"
    )
    print(
        "========================================"
    )
    print("")

    for filename in files:

        print("")
        print(
            "Document:",
            filename
        )

        print(
            "Press ENTER to use the default."
        )

        default_title = os.path.splitext(
            filename
        )[0]

        title = input(
            f"Title [{default_title}]: "
        ).strip()

        if not title:
            title = default_title

        jurisdiction = input(
            "Jurisdiction [UNSPECIFIED]: "
        ).strip()

        if not jurisdiction:
            jurisdiction = "UNSPECIFIED"

        document_type = input(
            "Document type [TRAINING]: "
        ).strip()

        if not document_type:
            document_type = "TRAINING"

        effective_date = input(
            "Effective date [UNKNOWN]: "
        ).strip()

        if not effective_date:
            effective_date = "UNKNOWN"

        status = input(
            "Status [TRAINING]: "
        ).strip()

        if not status:
            status = "TRAINING"

        documents[filename] = {

            "title": title,

            "source": filename,

            "jurisdiction":
                jurisdiction,

            "document_type":
                document_type,

            "effective_date":
                effective_date,

            "status":
                status
        }

        print(
            "Metadata saved."
        )

    save_metadata(data)

    print("")
    print(
        "Metadata file:"
    )

    print(
        METADATA_FILE
    )

    print("")


if __name__ == "__main__":

    main()