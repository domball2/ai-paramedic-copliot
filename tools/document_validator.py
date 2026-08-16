import os


MIN_TEXT_LENGTH = 50


def validate_document(
    path,
    text,
    title,
    jurisdiction,
    document_type,
    effective_date,
    status
):

    errors = []
    warnings = []

    if not os.path.exists(path):

        errors.append(
            "Document file does not exist."
        )

    if not text or not text.strip():

        errors.append(
            "No text was extracted."
        )

    elif len(text.strip()) < MIN_TEXT_LENGTH:

        warnings.append(
            "Document contains very little text."
        )

    if not title.strip():

        errors.append(
            "Title is required."
        )

    if not jurisdiction.strip():

        warnings.append(
            "Jurisdiction is unspecified."
        )

    if not document_type.strip():

        warnings.append(
            "Document type is unspecified."
        )

    if not effective_date.strip():

        warnings.append(
            "Effective date is unspecified."
        )

    if not status.strip():

        warnings.append(
            "Document status is unspecified."
        )

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }


def main():

    print("")
    print("PARAMEDIC AI DOCUMENT VALIDATOR")
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

        from document_reader import read_document

        text = read_document(
            path
        )

        result = validate_document(
            path,
            text,
            title,
            jurisdiction,
            document_type,
            effective_date,
            status
        )

        print("")
        print(
            "VALID:",
            result["valid"]
        )

        if result["errors"]:

            print("")
            print("ERRORS:")

            for error in result["errors"]:

                print(
                    f"- {error}"
                )

        if result["warnings"]:

            print("")
            print("WARNINGS:")

            for warning in result["warnings"]:

                print(
                    f"- {warning}"
                )

    except Exception as error:

        print("")
        print(
            f"ERROR: {error}"
        )


if __name__ == "__main__":

    main()