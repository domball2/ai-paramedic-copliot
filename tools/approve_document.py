import json
import os


BASE = r"C:\OllamaAI"

STAGING_DIR = os.path.join(
    BASE,
    "staging"
)


def list_staged():

    if not os.path.exists(
        STAGING_DIR
    ):

        return []

    return sorted(
        filename
        for filename in os.listdir(
            STAGING_DIR
        )
        if filename.endswith(".json")
    )


def load_record(filename):

    path = os.path.join(
        STAGING_DIR,
        filename
    )

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


def save_record(
    filename,
    record
):

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


def main():

    print("")
    print(
        "PARAMEDIC AI "
        "DOCUMENT APPROVAL"
    )
    print("")

    files = list_staged()

    if not files:

        print(
            "No staged documents."
        )

        return

    for index, filename in enumerate(
        files,
        start=1
    ):

        print(
            f"{index}. {filename}"
        )

    print("")

    choice = input(
        "Select document number: "
    ).strip()

    try:

        index = int(choice) - 1

        filename = files[index]

    except (
        ValueError,
        IndexError
    ):

        print(
            "Invalid selection."
        )

        return

    record = load_record(
        filename
    )

    print("")
    print(
        "TITLE:",
        record.get("title")
    )

    print(
        "JURISDICTION:",
        record.get(
            "jurisdiction"
        )
    )

    print(
        "TYPE:",
        record.get(
            "document_type"
        )
    )

    print(
        "EFFECTIVE DATE:",
        record.get(
            "effective_date"
        )
    )

    print(
        "STATUS:",
        record.get(
            "status"
        )
    )

    print("")
    print(
        "Current approval:",
        record.get(
            "approved",
            False
        )
    )

    print("")

    confirm = input(
        "Approve this document? "
        "[y/N]: "
    ).strip().lower()

    if confirm != "y":

        print("")
        print(
            "Document remains STAGED."
        )

        return

    record["approved"] = True

    save_record(
        filename,
        record
    )

    print("")
    print(
        "DOCUMENT APPROVED"
    )

    print(
        "It is still NOT embedded."
    )

    print(
        "Next stage: ingestion."
    )


if __name__ == "__main__":

    main()