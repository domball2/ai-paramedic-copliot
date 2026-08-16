import json
import math
import os

import ollama

from safety_gate import evaluate


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

MODEL = "paramedic-ai"
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

    if magnitude_a == 0 or magnitude_b == 0:
        return 0

    return dot / (
        magnitude_a * magnitude_b
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

        score = cosine_similarity(
            query_embedding,
            item["embedding"]
        )

        if score < MIN_SIMILARITY:
            continue

        source = item.get(
            "source",
            "UNKNOWN"
        )

        metadata = documents.get(
            source,
            {}
        )

        result = {

            "score": round(
                score,
                4
            ),

            "source": source,

            "title": metadata.get(
                "title",
                source
            ),

            "category": metadata.get(
                "category",
                "uncategorized"
            ),

            "jurisdiction": metadata.get(
                "jurisdiction",
                "UNKNOWN"
            ),

            "document_type": metadata.get(
                "document_type",
                "UNKNOWN"
            ),

            "effective_date": metadata.get(
                "effective_date",
                "UNKNOWN"
            ),

            "status": metadata.get(
                "status",
                "UNKNOWN"
            ),

            "text": item.get(
                "text",
                ""
            )
        }

        result["safety"] = evaluate(
            result
        )

        results.append(result)

    results.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    return results[:TOP_K]


def answer(question):

    results = search(question)

    if not results:

        print("")
        print(
            "No sufficiently relevant "
            "reference was found."
        )
        print("")
        return

    for result in results:

        safety = result["safety"]

        if not safety["protocol_ready"]:

            print("")
            print(
                "========================================"
            )
            print(
                "             SOURCE WARNING"
            )
            print(
                "========================================"
            )

            print(
                "This source is NOT verified as "
                "a current operational protocol."
            )

            print(
                "Status:",
                result["status"]
            )

            print(
                "Jurisdiction:",
                result["jurisdiction"]
            )

            print(
                "Effective date:",
                result["effective_date"]
            )

            for warning in safety["warnings"]:

                print(
                    "-",
                    warning
                )

            print(
                "Use current local protocols "
                "and medical direction for patient care."
            )

    context = []

    for number, result in enumerate(
        results,
        start=1
    ):

        context.append(
            f"""
SOURCE {number}
Title: {result['title']}
File: {result['source']}
Category: {result['category']}
Status: {result['status']}
Jurisdiction: {result['jurisdiction']}
Effective date: {result['effective_date']}

TEXT:
{result['text']}
"""
        )

    prompt = f"""
You are Paramedic AI, an EMS education
and decision-support assistant.

Answer using the retrieved references.

Rules:

- Do not invent information.
- Do not invent medication doses.
- Do not present training material as
  current operational protocol.
- Do not assume a jurisdiction.
- If source status is unknown, say so.
- If jurisdiction is unknown, say so.
- If the source is not verified as current,
  clearly qualify the answer.
- Current local EMS protocols and medical
  direction take precedence for patient care.
- Keep the answer concise.

USER QUESTION:

{question}

RETRIEVED REFERENCES:

{chr(10).join(context)}
"""

    response = ollama.chat(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content":
                    "You are a careful EMS "
                    "education assistant."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    print("")
    print(
        response["message"]["content"]
    )

    print("")
    print(
        "References:"
    )

    for result in results:

        print(
            f"- {result['title']} "
            f"[{result['status']}]"
        )

    print("")


def main():

    print("")
    print(
        "========================================"
    )
    print(
        "       PARAMEDIC AI — SAFE CHAT"
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
            "You: "
        ).strip()

        if not question:
            continue

        if question.lower() == "/exit":
            break

        try:
            answer(question)

        except Exception as error:

            print("")
            print(
                "ERROR:",
                error
            )
            print("")


if __name__ == "__main__":
    main()