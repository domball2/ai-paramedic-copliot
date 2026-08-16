import json
import math
import os

import ollama


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

TOP_K = 3

MIN_SIMILARITY = 0.35


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

    magnitude_a = math.sqrt(
        sum(x * x for x in a)
    )

    magnitude_b = math.sqrt(
        sum(y * y for y in b)
    )

    if (
        magnitude_a == 0
        or magnitude_b == 0
    ):

        return 0

    return dot / (
        magnitude_a *
        magnitude_b
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

    document_metadata = (
        metadata_data.get(
            "documents",
            {}
        )
    )

    if not vectors:

        print(
            "No vector records found."
        )

        return

    response = ollama.embed(

        model=EMBED_MODEL,

        input=question
    )

    query_embedding = (
        response["embeddings"][0]
    )

    results = []

    for document in vectors:

        similarity = cosine_similarity(

            query_embedding,

            document["embedding"]

        )

        if similarity < MIN_SIMILARITY:

            continue

        source = document.get(
            "source",
            "UNKNOWN"
        )

        metadata = (
            document_metadata.get(
                source,
                {}
            )
        )

        results.append({

            "similarity":
                round(
                    similarity,
                    4
                ),

            "source":
                source,

            "title":
                metadata.get(
                    "title",
                    source
                ),

            "jurisdiction":
                metadata.get(
                    "jurisdiction",
                    "UNKNOWN"
                ),

            "document_type":
                metadata.get(
                    "document_type",
                    "UNKNOWN"
                ),

            "effective_date":
                metadata.get(
                    "effective_date",
                    "UNKNOWN"
                ),

            "status":
                metadata.get(
                    "status",
                    "UNKNOWN"
                ),

            "text":
                document.get(
                    "text",
                    ""
                )
        })

    results.sort(
        key=lambda item:
            item["similarity"],
        reverse=True
    )

    if not results:

        print(
            "No sufficiently relevant "
            "documents found."
        )

        return

    print("")
    print(
        "========================================"
    )
    print(
        "          RAG SEARCH RESULTS"
    )
    print(
        "========================================"
    )

    for number, result in enumerate(
        results[:TOP_K],
        start=1
    ):

        print("")
        print(
            f"RESULT {number}"
        )

        print(
            "Similarity:",
            result["similarity"]
        )

        print(
            "Title:",
            result["title"]
        )

        print(
            "Source:",
            result["source"]
        )

        print(
            "Jurisdiction:",
            result["jurisdiction"]
        )

        print(
            "Document type:",
            result["document_type"]
        )

        print(
            "Effective date:",
            result["effective_date"]
        )

        print(
            "Status:",
            result["status"]
        )

        print("")
        print(
            "Text:"
        )

        print(
            result["text"]
        )

    print("")


def main():

    print("")
    print(
        "Paramedic AI RAG Search"
    )
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

            search(question)

        except Exception as error:

            print("")
            print(
                "ERROR:",
                error
            )
            print("")


if __name__ == "__main__":

    main()