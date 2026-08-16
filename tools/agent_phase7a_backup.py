import json
import math
import ollama

DATABASE = r"C:\OllamaAI\rag\vector_store.json"
SOURCE_INFO = r"C:\OllamaAI\knowledge\source_info.json"

MODEL = "paramedic-ai"
EMBED_MODEL = "nomic-embed-text"

TOP_K = 3
MIN_SIMILARITY = 0.35


# ============================================================
# TOOL 1: SEARCH EMS KNOWLEDGE
# ============================================================

def search_ems_knowledge(question: str) -> str:
    """
    Search the local EMS knowledge base.

    Use this when the user asks about information that may be
    contained in the local EMS reference library.
    """

    try:
        with open(DATABASE, "r", encoding="utf-8") as f:
            documents = json.load(f)
    except FileNotFoundError:
        return "EMS knowledge database was not found."

    try:
        with open(SOURCE_INFO, "r", encoding="utf-8") as f:
            source_info = json.load(f)
    except FileNotFoundError:
        source_info = {}

    response = ollama.embed(
        model=EMBED_MODEL,
        input=question
    )

    query_embedding = response["embeddings"][0]

    results = []

    for document in documents:

        embedding = document["embedding"]

        dot = sum(
            a * b
            for a, b in zip(query_embedding, embedding)
        )

        magnitude_a = math.sqrt(
            sum(a * a for a in query_embedding)
        )

        magnitude_b = math.sqrt(
            sum(b * b for b in embedding)
        )

        if magnitude_a == 0 or magnitude_b == 0:
            continue

        similarity = (
            dot / (magnitude_a * magnitude_b)
        )

        if similarity < MIN_SIMILARITY:
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
            "similarity": round(
                similarity,
                4
            ),
            "text": document["text"]
        })

    results.sort(
        key=lambda x: x["similarity"],
        reverse=True
    )

    if not results:
        return "No sufficiently relevant EMS references were found."

    return json.dumps(
        results[:TOP_K],
        indent=2
    )


# ============================================================
# TOOL 2: SAFE CALCULATOR
# ============================================================

def calculate(expression: str) -> str:
    """
    Perform basic arithmetic.

    Only numbers and basic arithmetic operators are permitted.
    """

    allowed = "0123456789+-*/(). "

    if any(
        character not in allowed
        for character in expression
    ):
        return "ERROR: Only basic arithmetic is allowed."

    try:

        result = eval(
            expression,
            {
                "__builtins__": {}
            },
            {}
        )

        return str(result)

    except Exception as error:

        return f"ERROR: {error}"


# ============================================================
# TOOL REGISTRY
# ============================================================

available_tools = {
    "search_ems_knowledge": search_ems_knowledge,
    "calculate": calculate
}


# ============================================================
# AI LOOP
# ============================================================

def main():

    print("")
    print("========================================")
    print("       PARAMEDIC AI - PHASE 7")
    print("========================================")
    print("")
    print("AI tool calling: ENABLED")
    print("")
    print("Available tools:")
    print("  search_ems_knowledge")
    print("  calculate")
    print("")
    print("Type 'exit' to quit.")
    print("")

    messages = []

    while True:

        user_input = input("You: ").strip()

        if user_input.lower() == "exit":
            break

        messages.append({
            "role": "user",
            "content": user_input
        })

        while True:

            response = ollama.chat(
                model=MODEL,
                messages=messages,
                tools=[
                    search_ems_knowledge,
                    calculate
                ]
            )

            messages.append(response["message"])

            tool_calls = response["message"].get(
                "tool_calls",
                []
            )

            if not tool_calls:

                print("")
                print(response["message"]["content"])
                print("")
                break

            for tool_call in tool_calls:

                function_name = tool_call["function"]["name"]

                arguments = tool_call["function"]["arguments"]

                print(
                    f"[AI requested tool: "
                    f"{function_name}]"
                )

                if function_name in available_tools:

                    function = available_tools[
                        function_name
                    ]

                    result = function(
                        **arguments
                    )

                else:

                    result = "ERROR: Unknown tool."

                print("[Tool completed]")
                print("")

                messages.append({
                    "role": "tool",
                    "tool_name": function_name,
                    "content": str(result)
                })


if __name__ == "__main__":
    main()