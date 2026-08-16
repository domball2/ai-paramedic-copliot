import json
import math
import os

import ollama

from question_intent import detect_intent
from source_priority import get_priority


BASE = r"C:\OllamaAI"

VECTOR_FILE = os.path.join(
    BASE,
    "rag",
    "vector_store.json"
)

METADATA_FILE = os.path.join(
    BASE,
    "knowledge",
    "metadata.json"
)

EMBED_MODEL = "nomic-embed-text"

TOP_K = 5
MIN_SIMILARITY = 0.30


INTENT_CATEGORIES = {

    "protocol": [
        "protocols",
        "medical_direction"
    ],

    "medication": [
        "medications"
    ],

    "training": [
        "training",
        "airway",
        "cardiology",
        "trauma",
        "pediatrics"
    ],

    "assessment": [
        "training",
        "airway",
        "cardiology",
        "trauma",
        "pediatrics"
    ],

    "general": [
        "training",
        "medications",
        "airway",
        "cardiology",
        "trauma",
        "pediatrics"
    ]
}


def load_json(path, default):

    if not os.path.exists(path):
        return default

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


def cosine_similarity(a, b):

    dot = sum(
        x * y
        for x, y in zip(a, b)
    )

    mag_a = math.sqrt(
        sum(x * x for x in a)
    )

    mag_b = math.sqrt(
        sum(y * y for y in b)
    )

    if mag_a == 0 or mag_b == 0:
        return 0

    return dot / (
        mag_a * mag_b
    )


def calculate_rank(
    similarity,
    authority,
    category_match
):

    relevance = similarity

    authority_score = (
        authority / 1000
    )

    category_bonus = 0.10 if (
        category_match
    ) else 0

    return (
        relevance
        + authority_score
        + category_bonus
    )


def search(question):

    intent = detect_intent(
        question
    )

    allowed_categories = (
        INTENT_CATEGORIES.get(
            intent,
            INTENT_CATEGORIES["general"]
        )
    )

    vectors = load_json(
        VECTOR_FILE,
        []
    )

    metadata_data = load_json(
        METADATA_FILE,
        {"documents": {}}
    )

    documents = metadata_data.get(
        "documents",
        {}
    )

    if not vectors:
        return intent, []

    response = ollama.embed(
        model=EMBED_MODEL,
        input=question
    )

    query_embedding = response[
        "embeddings"
    ][0]

    results = []

    for item in vectors:

        similarity = cosine_similarity(
            query_embedding,
            item["embedding"]
        )

        if similarity < MIN_SIMILARITY:
            continue

        source = item.get(
            "source",
            "UNKNOWN"
        )

        metadata = documents.get(
            source,
            {}
        )

        category = metadata.get(
            "category",
            "uncategorized"
        ).lower()

        priority = get_priority(
            metadata
        )

        category_match = (
            category in allowed_categories
        )

        rank = calculate_rank(
            similarity,
            priority["priority"],
            category_match
        )

        results.append({

            "rank":
                round(
                    rank,
                    4
                ),

            "similarity":
                round(
                    similarity,
                    4
                ),

            "authority":
                priority["priority"],

            "category_match":
                category_match,

            "trust_level":
                priority["trust_level"],

            "intent":
                intent,

            "source":
                source,

            "title":
                metadata.get(
                    "title",
                    source
                ),

            "category":
                category,

            "status":
                metadata.get(
                    "status",
                    "UNKNOWN"
                ),

            "jurisdiction":
                metadata.get(
                    "jurisdiction",
                    "UNKNOWN"
                ),

            "effective_date":
                metadata.get(
                    "effective_date",
                    "UNKNOWN"
                ),

            "text":
                item.get(
                    "text",
                    ""
                )
        })

    results.sort(
        key=lambda item:
            item["rank"],
        reverse=True
    )

    return intent, results[:TOP_K]


def main():

    print("")
    print(
        "========================================"
    )
    print(
        "       INTENT-AWARE RAG SEARCH"
    )
    print(
        "========================================"
    )
    print("")
    print(
        "Type /exit to quit."
    )
    print("")

    while True:

        question = input(
            "Search: "
        ).strip()

        if not question:
            continue

        if question.lower() == "/exit":
            break

        try:

            intent, results = search(
                question
            )

            print("")
            print(
                "Detected intent:",
                intent
            )

            print("")

            if not results:

                print(
                    "No matching sources."
                )

                continue

            for number, result in enumerate(
                results,
                start=1
            ):

                print(
                    f"[{number}] "
                    f"{result['title']}"
                )

                print(
                    f"    Rank: "
                    f"{result['rank']}"
                )

                print(
                    f"    Similarity: "
                    f"{result['similarity']}"
                )

                print(
                    f"    Authority: "
                    f"{result['authority']}"
                )

                print(
                    f"    Category: "
                    f"{result['category']}"
                )

                print(
                    f"    Category match: "
                    f"{result['category_match']}"
                )

                print(
                    f"    Trust: "
                    f"{result['trust_level']}"
                )

                print(
                    f"    Status: "
                    f"{result['status']}"
                )

                print(
                    f"    Source: "
                    f"{result['source']}"
                )

                print("")

        except Exception as error:

            print("")
            print(
                "ERROR:",
                error
            )
            print("")


if __name__ == "__main__":
    main()
