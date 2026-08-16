HIGH_RISK_TERMS = [
    "dose",
    "dosage",
    "mg",
    "mcg",
    "ml",
    "medication",
    "drug",
    "epinephrine",
    "epi",
    "naloxone",
    "amiodarone",
    "ketamine",
    "intubation",
    "cricothyrotomy",
    "defibrillation",
    "cardioversion",
    "protocol",
    "medical direction",
    "contraindication"
]


def assess_question(question):

    text = question.lower()

    matches = []

    for term in HIGH_RISK_TERMS:

        if term in text:
            matches.append(term)

    if matches:

        return {
            "risk": "HIGH",
            "requires_source": True,
            "matches": matches
        }

    return {
        "risk": "NORMAL",
        "requires_source": False,
        "matches": []
    }


def main():

    print("")
    print("PARAMEDIC AI SAFETY GATE")
    print("Type /exit to quit.")
    print("")

    while True:

        question = input(
            "Question: "
        ).strip()

        if question.lower() == "/exit":
            break

        result = assess_question(
            question
        )

        print("")
        print(
            "Risk:",
            result["risk"]
        )

        print(
            "Requires verified source:",
            result["requires_source"]
        )

        if result["matches"]:

            print(
                "Matched terms:",
                ", ".join(
                    result["matches"]
                )
            )

        print("")


if __name__ == "__main__":

    main()