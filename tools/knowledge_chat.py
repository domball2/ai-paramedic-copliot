import json
import math
import os

import ollama


BASE = r"C:\OllamaAI"

VECTOR_FILE = os.path.join(
    BASE, "rag", "vector_store.json"
)

METADATA_FILE = os.path.join(
    BASE, "knowledge", "metadata.json"
)

MODEL = "paramedic-ai"
EMBED_MODEL = "nomic-embed-text"

TOP_K = 3
MIN_SIMILARITY = 0.45


def load_json(path, default):

    if not os.path.exists(path):
        return default

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


def similarity(a, b):

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

    return dot / (mag_a * mag_b)


def search(question):

    vectors = load_json(
        VECTOR_FILE,
        []
    )

    metadata = load_json(
        METADATA_FILE,
        {"documents": {}}
    )

    documents = metadata.get(
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

        score = similarity(
            query_embedding,
            item["embedding"]
        )

        if score < MIN_SIMILARITY:
            continue

        source = item.get(
            "source",
            "UNKNOWN"
        )

        info = documents.get(
            source,
            {}
        )

        results.append({

            "score": round(
                score,
                4
            ),

            "source": source,

            "title": info.get(
                "title",
                source
            ),

            "jurisdiction": info.get(
                "jurisdiction",
                "UNKNOWN"
            ),

            "document_type": info.get(
                "document_type",
                "UNKNOWN"
            ),

            "effective_date": info.get(
                "effective_date",
                "UNKNOWN"
            ),

            "status": info.get(
                "status",
                "UNKNOWN"
            ),

            "text": item.get(
                "text",
                ""
            )
        })

    results.sort(
        key=lambda x: x["score"],
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

    context_parts = []

    for number, result in enumerate(
        results,
        start=1
    ):

        context_parts.append(

            f"""
SOURCE {number}
Title: {result['title']}
File: {result['source']}
Jurisdiction: {result['jurisdiction']}
Document type: {result['document_type']}
Effective date: {result['effective_date']}
Status: {result['status']}

TEXT:
{result['text']}
"""
        )

    context = "\n".join(
        context_parts
    )

    prompt = f"""
You are Paramedic AI, an EMS education
and decision-support assistant.

Answer the user's question using the
retrieved reference material below.

IMPORTANT:

1. Do not invent protocol information.
2. Do not invent medication doses.
3. Do not treat TRAINING material as
   current protocol.
4. If jurisdiction is UNKNOWN or
   UNSPECIFIED, say so.
5. If effective date is UNKNOWN,
   say so when relevant.
6. If the sources are insufficient,
   say that clearly.
7. For real patient care, current
   local EMS protocols and medical
   direction take precedence.
8. Keep the answer concise.

RETRIEVED REFERENCES:

{context}

USER QUESTION:

{question}
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
        "References used:"
    )

    seen_sources = set()

    for result in results:

        source = result["source"]

        if source in seen_sources:
            continue

        seen_sources.add(
            source
        )

        print(
            f"- {result['title']} "
            f"({result['status']})"
        )


def main():

    print("")
    print(
        "========================================"
    )
    print(
        "       PARAMEDIC AI KNOWLEDGE CHAT"
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