import json
import os


BASE = r"C:\OllamaAI"

RULES_FILE = os.path.join(
    BASE,
    "knowledge",
    "category_rules.json"
)


def load_rules():

    with open(
        RULES_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


def check_source(metadata):

    rules = load_rules()

    category = metadata.get(
        "category",
        "uncategorized"
    ).lower()

    rule = rules.get(
        category,
        rules["uncategorized"]
    )

    warnings = []

    if (
        rule.get(
            "requires_current_status"
        )
        and metadata.get(
            "status",
            "UNKNOWN"
        ).upper()
        not in [
            "CURRENT",
            "ACTIVE"
        ]
    ):

        warnings.append(
            "Source is not identified "
            "as current or active."
        )

    if (
        rule.get(
            "requires_jurisdiction"
        )
        and metadata.get(
            "jurisdiction",
            "UNKNOWN"
        ).upper()
        == "UNKNOWN"
    ):

        warnings.append(
            "Jurisdiction is unknown."
        )

    if (
        rule.get(
            "requires_effective_date"
        )
        and metadata.get(
            "effective_date",
            "UNKNOWN"
        ).upper()
        == "UNKNOWN"
    ):

        warnings.append(
            "Effective date is unknown."
        )

    return {
        "category": category,
        "description": rule.get(
            "description",
            ""
        ),
        "safe_for_protocol_use":
            len(warnings) == 0,
        "warnings": warnings
    }


def main():

    test_source = {

        "category": "training",

        "status": "TRAINING",

        "jurisdiction":
            "UNSPECIFIED",

        "effective_date":
            "UNKNOWN"
    }

    result = check_source(
        test_source
    )

    print("")
    print(
        "Source safety check:"
    )

    print(
        json.dumps(
            result,
            indent=4
        )
    )

    print("")


if __name__ == "__main__":

    main()