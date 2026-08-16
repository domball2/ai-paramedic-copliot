import json
import math
import os

import ollama

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
    priority
):

    authority_bonus = (
        priority / 1000
    )

    return (
        similarity +
        authority_bonus
    )


def search(question):

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
        return []

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

        priority = get_priority(
            metadata
        )

        final_rank = calculate_rank(
            similarity,
            priority["priority"]
        )

        results.append({

            "similarity":
                round(
                    similarity,
                    4
                ),

            "priority":
                priority["priority"],

            "final_rank":
                round(
                    final_rank,
                    4
                ),

            "trust_level":
                priority["trust_level"],

            "source":
                source,

            "title":
                metadata.get(
                    "title",
                    source
                ),

            "category":
                metadata.get(
                    "category",
                    "uncategorized"
                ),

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
            item["final_rank"],
        reverse=True
    )

    return results[:TOP_K]


def main():

    print("")
    print(
        "========================================"
    )
    print(
        "       AUTHORITY-AWARE RAG SEARCH"
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

            results = search(
                question
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
                    f"    Similarity: "
                    f"{result['similarity']}"
                )

                print(
                    f"    Authority: "
                    f"{result['priority']}"
                )

                print(
                    f"    Final rank: "
                    f"{result['final_rank']}"
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
                    f"    Jurisdiction: "
                    f"{result['jurisdiction']}"
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