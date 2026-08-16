import json
import math
import ollama

DATABASE = r"C:\OllamaAI\rag\vector_store.json"
SOURCE_INFO = r"C:\OllamaAI\knowledge\source_info.json"

EMBED_MODEL = "nomic-embed-text"

MIN_SIMILARITY = 0.35
TOP_K = 3


def cosine_similarity(a, b):

    dot = sum(x * y for x, y in zip(a, b))

    magnitude_a = math.sqrt(sum(x * x for x in a))
    magnitude_b = math.sqrt(sum(y * y for y in b))

    if magnitude_a == 0 or magnitude_b == 0:
        return 0

    return dot / (magnitude_a * magnitude_b)


def load_database():

    with open(DATABASE, "r", encoding="utf-8") as f:
        return json.load(f)


def load_source_info():

    try:

        with open(SOURCE_INFO, "r", encoding="utf-8") as f:
            return json.load(f)

    except FileNotFoundError:

        return {}


def search_knowledge(question):

    documents = load_database()
    source_info = load_source_info()

    response = ollama.embed(
        model=EMBED_MODEL,
        input=question
    )

    question_embedding = response["embeddings"][0]

    results = []

    for document in documents:

        score = cosine_similarity(
            question_embedding,
            document["embedding"]
        )

        if score < MIN_SIMILARITY:
            continue

        metadata = source_info.get(
            document["source"],
            {}
        )

        results.append({
            "source": document["source"],
            "title": metadata.get(
                "title",
                document["source"]
            ),
            "jurisdiction": metadata.get(
                "jurisdiction",
                "Unknown"
            ),
            "effective_date": metadata.get(
                "effective_date",
                "Unknown"
            ),
            "status": metadata.get(
                "status",
                "Unknown"
            ),
            "score": score,
            "text": document["text"]
        })

    results.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return results[:TOP_K]


def list_sources():

    source_info = load_source_info()

    if not source_info:
        return []

    return source_info


def calculate(expression):

    allowed = "0123456789+-*/(). "

    if any(character not in allowed for character in expression):
        return {
            "error": "Only basic arithmetic is allowed."
        }

    try:

        result = eval(
            expression,
            {
                "__builtins__": {}
            },
            {}
        )

        return {
            "expression": expression,
            "result": result
        }

    except Exception as error:

        return {
            "error": str(error)
        }


def main():

    print("")
    print("========================================")
    print("          EMS TOOL SYSTEM")
    print("========================================")
    print("")
    print("1 - Search EMS knowledge")
    print("2 - Calculate")
    print("3 - List sources")
    print("4 - Exit")
    print("")

    while True:

        choice = input("Tool: ").strip()

        if choice == "1":

            question = input(
                "Search question: "
            )

            results = search_knowledge(question)

            print("")

            if not results:

                print(
                    "No sufficiently relevant "
                    "sources found."
                )

            else:

                for result in results:

                    print("----------------------------------------")
                    print(
                        f"Source: {result['source']}"
                    )
                    print(
                        f"Title: {result['title']}"
                    )
                    print(
                        f"Jurisdiction: "
                        f"{result['jurisdiction']}"
                    )
                    print(
                        f"Effective date: "
                        f"{result['effective_date']}"
                    )
                    print(
                        f"Status: {result['status']}"
                    )
                    print(
                        f"Similarity: "
                        f"{result['score']:.4f}"
                    )
                    print("")
                    print(result["text"])
                    print("")

        elif choice == "2":

            expression = input(
                "Expression: "
            )

            result = calculate(expression)

            print(result)

        elif choice == "3":

            sources = list_sources()

            if not sources:

                print("No source metadata found.")

            else:

                for filename, metadata in sources.items():

                    print("----------------------------------------")
                    print(f"File: {filename}")

                    for key, value in metadata.items():

                        print(
                            f"{key}: {value}"
                        )

        elif choice == "4":

            break

        else:

            print("Invalid choice.")


if __name__ == "__main__":
    main()