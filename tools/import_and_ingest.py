import os
import sys

sys.path.insert(
    0,
    r"C:\OllamaAI\tools"
)

from import_document import (
    create_import_record,
    save_staging_record
)

from ingest_approved import (
    split_text,
    load_vectors,
    save_vectors
)

import ollama


EMBED_MODEL = "nomic-embed-text"


def embed_record(record):

    text = record.get(
        "text",
        ""
    )

    chunks = split_text(
        text
    )

    vectors = load_vectors()

    source = record[
        "source_file"
    ]

    vectors = [
        vector
        for vector in vectors
        if vector.get("source")
        != source
    ]

    for index, chunk in enumerate(
        chunks,
        start=1
    ):

        print(
            f"Embedding "
            f"{index}/{len(chunks)}..."
        )

        response = ollama.embed(
            model=EMBED_MODEL,
            input=chunk
        )

        embedding = response[
            "embeddings"
        ][0]

        vectors.append({

            "source":
                source,

            "title":
                record["title"],

            "path":
                source,

            "text":
                chunk,

            "embedding":
                embedding
        })

    save_vectors(
        vectors
    )

    return len(chunks)


def main():

    print("")
    print(
        "========================================"
    )
    print(
        "       PARAMEDIC AI DOCUMENT IMPORT"
    )
    print(
        "========================================"
    )
    print("")

    path = input(
        "Document path: "
    ).strip().strip('"')

    title = input(
        "Title: "
    ).strip()

    jurisdiction = input(
        "Jurisdiction: "
    ).strip()

    document_type = input(
        "Document type: "
    ).strip()

    effective_date = input(
        "Effective date: "
    ).strip()

    status = input(
        "Status: "
    ).strip()

    result = create_import_record(
        path,
        title,
        jurisdiction,
        document_type,
        effective_date,
        status
    )

    if not result["success"]:

        print("")
        print(
            "IMPORT REJECTED"
        )

        for error in result[
            "validation"
        ]["errors"]:

            print(
                f"- {error}"
            )

        return

    record = result[
        "record"
    ]

    print("")
    print(
        "Document validated."
    )

    print("")
    print(
        "Title:",
        record["title"]
    )

    print(
        "Jurisdiction:",
        record["jurisdiction"]
    )

    print(
        "Type:",
        record["document_type"]
    )

    print(
        "Effective date:",
        record["effective_date"]
    )

    print(
        "Status:",
        record["status"]
    )

    print("")

    confirm = input(
        "Approve and add to RAG? "
        "[y/N]: "
    ).strip().lower()

    if confirm != "y":

        print("")
        print(
            "Document remains unapproved."
        )

        save_staging_record(
            record
        )

        return

    record["approved"] = True

    save_staging_record(
        record
    )

    print("")
    print(
        "Document approved."
    )

    print("")

    chunks = embed_record(
        record
    )

    print("")
    print(
        "========================================"
    )

    print(
        "IMPORT COMPLETE"
    )

    print(
        f"Chunks embedded: {chunks}"
    )

    print(
        "Document is now searchable in RAG."
    )

    print(
        "========================================"
    )


if __name__ == "__main__":

    main()