import json
import os
from datetime import datetime

import ollama


BASE = r"C:\OllamaAI"

DOCUMENT_DIR = os.path.join(
    BASE,
    "documents"
)

RAG_DIR = os.path.join(
    BASE,
    "rag"
)

VECTOR_FILE = os.path.join(
    RAG_DIR,
    "vector_store.json"
)

SOURCE_FILE = os.path.join(
    BASE,
    "knowledge",
    "source_info.json"
)

EMBED_MODEL = "nomic-embed-text"

CHUNK_SIZE = 1200
CHUNK_OVERLAP = 200


def ensure_directories():

    os.makedirs(
        DOCUMENT_DIR,
        exist_ok=True
    )

    os.makedirs(
        RAG_DIR,
        exist_ok=True
    )

    os.makedirs(
        os.path.dirname(SOURCE_FILE),
        exist_ok=True
    )


def load_vectors():

    if not os.path.exists(VECTOR_FILE):

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
            indent=2,
            ensure_ascii=False
        )


def load_sources():

    if not os.path.exists(SOURCE_FILE):

        return {}

    with open(
        SOURCE_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


def save_sources(sources):

    with open(
        SOURCE_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            sources,
            f,
            indent=2,
            ensure_ascii=False
        )


def split_text(text):

    text = text.strip()

    chunks = []

    start = 0

    while start < len(text):

        end = start + CHUNK_SIZE

        chunk = text[start:end].strip()

        if chunk:

            chunks.append(chunk)

        start += (
            CHUNK_SIZE -
            CHUNK_OVERLAP
        )

    return chunks


def embed_text(text):

    response = ollama.embed(

        model=EMBED_MODEL,

        input=text
    )

    return response["embeddings"][0]


def ingest_file(
    filename,
    vectors,
    sources
):

    path = os.path.join(
        DOCUMENT_DIR,
        filename
    )

    print("")
    print("Reading:", filename)

    with open(
        path,
        "r",
        encoding="utf-8",
        errors="ignore"
    ) as f:

        text = f.read()

    if not text.strip():

        print("Skipped: empty file")
        return

    chunks = split_text(text)

    print(
        "Chunks:",
        len(chunks)
    )

    source_id = filename

    sources[source_id] = {

        "title": os.path.splitext(
            filename
        )[0],

        "source": filename,

        "jurisdiction": "UNSPECIFIED",

        "document_type": "TRAINING",

        "effective_date": "UNKNOWN",

        "status": "TRAINING",

        "ingested": datetime.now().isoformat()

    }

    # Remove previous chunks from this source

    vectors[:] = [

        vector
        for vector in vectors
        if vector.get("source")
        != source_id

    ]

    for index, chunk in enumerate(chunks):

        print(
            f"Embedding {index + 1}"
            f"/{len(chunks)}..."
        )

        embedding = embed_text(
            chunk
        )

        vectors.append({

            "source": source_id,

            "chunk": index,

            "text": chunk,

            "embedding": embedding

        })

    print(
        "Finished:",
        filename
    )


def main():

    ensure_directories()

    vectors = load_vectors()

    sources = load_sources()

    files = [

        filename
        for filename
        in os.listdir(DOCUMENT_DIR)

        if filename.lower().endswith(
            ".txt"
        )
    ]

    if not files:

        print("")
        print(
            "No .txt files found in:"
        )
        print(DOCUMENT_DIR)
        print("")
        return

    print("")
    print("========================================")
    print("       PARAMEDIC AI DOCUMENT INGESTOR")
    print("========================================")
    print("")
    print(
        "Documents found:",
        len(files)
    )
    print("")

    for filename in files:

        ingest_file(
            filename,
            vectors,
            sources
        )

    save_vectors(
        vectors
    )

    save_sources(
        sources
    )

    print("")
    print("========================================")
    print("INGESTION COMPLETE")
    print("========================================")
    print("")
    print(
        "Vector records:",
        len(vectors)
    )
    print(
        "Sources:",
        len(sources)
    )
    print("")


if __name__ == "__main__":

    main()