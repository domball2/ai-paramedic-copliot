import json
import os
from datetime import datetime

import ollama
from pypdf import PdfReader


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


def load_json(path, default):

    if not os.path.exists(path):
        return default

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


def save_json(path, data):

    os.makedirs(
        os.path.dirname(path),
        exist_ok=True
    )

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            indent=2,
            ensure_ascii=False
        )


def read_txt(path):

    with open(
        path,
        "r",
        encoding="utf-8",
        errors="ignore"
    ) as f:

        return f.read()


def read_pdf(path):

    reader = PdfReader(path)

    pages = []

    for number, page in enumerate(
        reader.pages,
        start=1
    ):

        text = page.extract_text()

        if text:

            pages.append(
                f"\n[PAGE {number}]\n"
                + text
            )

    return "\n".join(pages)


def read_document(path):

    extension = os.path.splitext(
        path
    )[1].lower()

    if extension == ".txt":
        return read_txt(path)

    if extension == ".pdf":
        return read_pdf(path)

    return ""


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


def find_documents():

    found = []

    for root, directories, files in os.walk(
        DOCUMENT_DIR
    ):

        for filename in files:

            if filename.lower().endswith(
                (".txt", ".pdf")
            ):

                full_path = os.path.join(
                    root,
                    filename
                )

                relative_path = os.path.relpath(
                    full_path,
                    DOCUMENT_DIR
                )

                found.append(
                    (
                        full_path,
                        relative_path
                    )
                )

    return found


def category_from_path(relative_path):

    parts = relative_path.split(
        os.sep
    )

    if len(parts) > 1:

        return parts[0]

    return "uncategorized"


def ingest_document(
    full_path,
    relative_path,
    vectors,
    sources
):

    print("")
    print(
        "Reading:",
        relative_path
    )

    text = read_document(
        full_path
    )

    if not text.strip():

        print(
            "Skipped: no text."
        )

        return

    chunks = split_text(text)

    print(
        "Chunks:",
        len(chunks)
    )

    source_id = relative_path

    category = category_from_path(
        relative_path
    )

    vectors[:] = [

        item

        for item in vectors

        if item.get("source")
        != source_id

    ]

    for index, chunk in enumerate(
        chunks
    ):

        print(
            f"Embedding "
            f"{index + 1}/"
            f"{len(chunks)}..."
        )

        embedding = embed_text(
            chunk
        )

        vectors.append({

            "source":
                source_id,

            "chunk":
                index,

            "category":
                category,

            "text":
                chunk,

            "embedding":
                embedding
        })

    sources[source_id] = {

        "title":
            os.path.splitext(
                os.path.basename(
                    relative_path
                )
            )[0],

        "source":
            source_id,

        "category":
            category,

        "ingested":
            datetime.now().isoformat()
    }

    print(
        "Finished:",
        relative_path
    )


def main():

    os.makedirs(
        DOCUMENT_DIR,
        exist_ok=True
    )

    vectors = load_json(
        VECTOR_FILE,
        []
    )

    sources = load_json(
        SOURCE_FILE,
        {}
    )

    documents = find_documents()

    print("")
    print(
        "========================================"
    )
    print(
        "     PARAMEDIC AI RECURSIVE INGESTOR"
    )
    print(
        "========================================"
    )
    print("")

    print(
        "Documents found:",
        len(documents)
    )

    if not documents:

        print(
            "No .txt or .pdf files found."
        )

        return

    for full_path, relative_path in documents:

        try:

            ingest_document(
                full_path,
                relative_path,
                vectors,
                sources
            )

        except Exception as error:

            print("")
            print(
                "ERROR:",
                relative_path
            )

            print(error)

    save_json(
        VECTOR_FILE,
        vectors
    )

    save_json(
        SOURCE_FILE,
        sources
    )

    print("")
    print(
        "========================================"
    )
    print(
        "INGESTION COMPLETE"
    )
    print(
        "========================================"
    )

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