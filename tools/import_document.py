import json
import os
from datetime import datetime

from document_reader import read_document
from document_validator import validate_document


BASE = r"C:\OllamaAI"

STAGING_DIR = os.path.join(
    BASE,
    "staging"
)


def ensure_staging():

    os.makedirs(
        STAGING_DIR,
        exist_ok=True
    )


def safe_name(name):

    return "".join(
        character
        for character in name
        if character.isalnum()
        or character in "_-"
    )


def create_import_record(
    path,
    title,
    jurisdiction,
    document_type,
    effective_date,
    status
):

    text = read_document(
        path
    )

    validation = validate_document(
        path,
        text,
        title,
        jurisdiction,
        document_type,
        effective_date,
        status
    )

    if not validation["valid"]:

        return {
            "success": False,
            "validation": validation
        }

    record = {

        "id":
            safe_name(title),

        "title":
            title,

        "source_file":
            os.path.abspath(path),

        "jurisdiction":
            jurisdiction,

        "document_type":
            document_type,

        "effective_date":
            effective_date,

        "status":
            status,

        "imported_at":
            datetime.now().isoformat(),

        "approved":
            False,

        "text":
            text
    }

    return {
        "success": True,
        "record": record,
        "validation": validation
    }


def save_staging_record(record):

    ensure_staging()

    filename = (
        safe_name(
            record["title"]
        )
        + ".json"
    )

    path = os.path.join(
        STAGING_DIR,
        filename
    )

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            record,
            f,
            indent=2,
            ensure_ascii=False
        )

    return path


def main():

    print("")
    print(
        "PARAMEDIC AI DOCUMENT IMPORT"
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

    try:

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

        staging_path = (
            save_staging_record(
                record
            )
        )

        print("")
        print(
            "IMPORT SUCCESSFUL"
        )

        print("")
        print(
            "Status: STAGED"
        )

        print(
            "Approved: False"
        )

        print(
            f"Staging file:\n"
            f"{staging_path}"
        )

        print("")
        print(
            "Document is NOT yet "
            "part of the RAG knowledge base."
        )

    except Exception as error:

        print("")
        print(
            f"ERROR: {error}"
        )


if __name__ == "__main__":

    main()