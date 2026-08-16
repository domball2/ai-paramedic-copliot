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


# ============================================================
# DIRECTORIES
# ============================================================

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


# ============================================================
# DATABASE
# ============================================================

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
            indent=2,
            ensure_ascii=False
        )


def load_sources():

    if not os.path.exists(
        SOURCE_FILE
    ):

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


# ============================================================
# TEXT EXTRACTION
# ============================================================

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

    for page_number, page in enumerate(
        reader.pages,
        start=1
    ):

        try:

            text = page.extract_text()

        except Exception:

            text = ""

        if text:

            pages.append(
                f"\n[PAGE {page_number}]\n"
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


# ============================================================
# CHUNKING
# ============================================================

def split_text(text):

    text = text.strip()

    chunks = []

    start = 0

    while start < len(text):

        end = start + CHUNK_SIZE

        chunk = text[start:end].strip()

        if chunk:

            chunks.append(
                chunk
            )

        start += (
            CHUNK_SIZE -
            CHUNK_OVERLAP
        )

    return chunks


# ============================================================
# EMBEDDINGS
# ============================================================

def embed_text(text):

    response = ollama.embed(

        model=EMBED_MODEL,

        input=text

    )

    return response["embeddings"][0]


# ============================================================
# INGEST DOCUMENT
# ============================================================

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
    print(
        "Reading:",
        filename
    )

    text = read_document(
        path
    )

    if not text.strip():

        print(
            "Skipped: no extractable text."
        )

        return

    chunks = split_text(
        text
    )

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

        "jurisdiction":
            "UNSPECIFIED",

        "document_type":
            "TRAINING",

        "effective_date":
            "UNKNOWN",

        "status":
            "TRAINING",

        "ingested":
            datetime.now().isoformat()

    }

    # Remove previous version
    # of this document.

    vectors[:] = [

        vector

        for vector in vectors

        if vector.get("source")
        != source_id

    ]

    for index, chunk in enumerate(
        chunks
    ):

        print(
            f"Embedding "
            f"{index + 1}"
            f"/{len(chunks)}..."
        )

        embedding = embed_text(
            chunk
        )

        vectors.append({

            "source":
                source_id,

            "chunk":
                index,

            "text":
                chunk,

            "embedding":
                embedding

        })

    print(
        "Finished:",
        filename
    )


# ============================================================
# MAIN
# ============================================================

def main():

    ensure_directories()

    vectors = load_vectors()

    sources = load_sources()

    files = [

        filename

        for filename
        in os.listdir(
            DOCUMENT_DIR
        )

        if filename.lower().endswith(
            (".txt", ".pdf")
        )

    ]

    if not files:

        print("")
        print(
            "No .txt or .pdf files found."
        )
        print(
            DOCUMENT_DIR
        )
        print("")

        return

    print("")
    print(
        "========================================"
    )
    print(
        "       PARAMEDIC AI DOCUMENT INGESTOR"
    )
    print(
        "========================================"
    )
    print("")

    print(
        "Documents found:",
        len(files)
    )

    print("")

    for filename in files:

        try:

            ingest_file(
                filename,
                vectors,
                sources
            )

        except Exception as error:

            print("")
            print(
                "ERROR:",
                filename
            )

            print(
                error
            )

            print(
                "Document skipped."
            )

    save_vectors(
        vectors
    )

    save_sources(
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