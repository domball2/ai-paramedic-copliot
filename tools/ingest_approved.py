import json
import os

import ollama


BASE = r"C:\OllamaAI"

STAGING_DIR = os.path.join(
    BASE,
    "staging"
)

VECTOR_FILE = os.path.join(
    BASE,
    "rag",
    "vector_store.json"
)

EMBED_MODEL = "nomic-embed-text"


def split_text(text, chunk_size=1200):

    chunks = []

    start = 0

    while start < len(text):

        end = start + chunk_size

        chunk = text[
            start:end
        ].strip()

        if chunk:

            chunks.append(
                chunk
            )

        start = end

    return chunks


def load_vectors():

    if not os.path.exists(
        VECTOR_FILE
    ):

        return []

    with open(
        VECTOR_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


def save_vectors(vectors):

    with open(
        VECTOR_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            vectors,
            f,
            ensure_ascii=False
        )


def main():

    print("")
    print(
        "APPROVED DOCUMENT INGESTION"
    )
    print("")

    files = [
        filename
        for filename in os.listdir(
            STAGING_DIR
        )
        if filename.endswith(".json")
    ]

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

    staging_path = os.path.join(
        STAGING_DIR,
        filename
    )

    with open(
        staging_path,
        "r",
        encoding="utf-8"
    ) as f:

        record = json.load(f)

    if not record.get(
        "approved",
        False
    ):

        print("")
        print(
            "INGESTION BLOCKED"
        )

        print(
            "Document is not approved."
        )

        return

    source = record.get(
        "source_file",
        filename
    )

    title = record.get(
        "title",
        filename
    )

    text = record.get(
        "text",
        ""
    )

    if not text.strip():

        print(
            "INGESTION BLOCKED"
        )

        print(
            "Document contains no text."
        )

        return

    chunks = split_text(
        text
    )

    vectors = load_vectors()

    vectors = [
        vector
        for vector in vectors
        if vector.get("source")
        != source
    ]

    print("")
    print(
        f"Embedding {len(chunks)} "
        f"chunk(s)..."
    )

    for index, chunk in enumerate(
        chunks,
        start=1
    ):

        response = ollama.embed(
            model=EMBED_MODEL,
            input=chunk
        )

        embedding = response[
            "embeddings"
        ][0]

        vectors.append({
            "source": source,
            "title": title,
            "path": source,
            "text": chunk,
            "embedding": embedding
        })

        print(
            f"Embedded "
            f"{index}/{len(chunks)}"
        )

    save_vectors(
        vectors
    )

    print("")
    print(
        "INGESTION COMPLETE"
    )

    print(
        f"Document: {title}"
    )

    print(
        f"Chunks: {len(chunks)}"
    )

    print(
        f"Vector database: "
        f"{VECTOR_FILE}"
    )


if __name__ == "__main__":

    main()