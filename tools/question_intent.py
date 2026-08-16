def detect_intent(question):

    text = question.lower().strip()

    protocol_words = [
        "protocol",
        "protocols",
        "standing order",
        "standing orders",
        "local guideline",
        "local guidelines",
        "what can i do",
        "what should i administer",
        "may i administer"
    ]

    medication_words = [
        "medication",
        "medications",
        "drug",
        "dose",
        "dosage",
        "contraindication",
        "indication",
        "side effect"
    ]

    training_words = [
        "teach me",
        "explain",
        "learn",
        "study",
        "practice",
        "quiz",
        "training",
        "what is",
        "why does",
        "how does"
    ]

    assessment_words = [
        "assessment",
        "patient assessment",
        "primary assessment",
        "secondary assessment",
        "scene safety",
        "differential"
    ]

    if any(
        word in text
        for word in protocol_words
    ):
        return "protocol"

    if any(
        word in text
        for word in medication_words
    ):
        return "medication"

    if any(
        word in text
        for word in assessment_words
    ):
        return "assessment"

    if any(
        word in text
        for word in training_words
    ):
        return "training"

    return "general"


def main():

    print("")
    print(
        "Paramedic AI Intent Detector"
    )
    print(
        "Type /exit to quit."
    )
    print("")

    while True:

        question = input(
            "Question: "
        ).strip()

        if not question:
            continue

        if question.lower() == "/exit":
            break

        intent = detect_intent(
            question
        )

        print(
            "Intent:",
            intent
        )

        print("")


if __name__ == "__main__":
    main()