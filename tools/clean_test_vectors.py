import json


VECTOR_FILE = (
    r"C:\OllamaAI\rag\vector_store.json"
)

KEEP_SOURCE = (
    r"C:\OllamaAI\documents\test_ems.txt"
)


def main():

    with open(
        VECTOR_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        vectors = json.load(f)

    original_count = len(vectors)

    vectors = [
        vector
        for vector in vectors
        if vector.get("source")
        == KEEP_SOURCE
        or vector.get("source")
        not in {
            "Chest_Pain_Test.txt",
            "EMS_Test.txt",
            "test_ems.txt",
            r"training\test_ems.txt"
        }
    ]

    removed = (
        original_count
        - len(vectors)
    )

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

    print("")
    print(
        f"Removed vectors: {removed}"
    )

    print(
        f"Remaining vectors: "
        f"{len(vectors)}"
    )


if __name__ == "__main__":

    main()