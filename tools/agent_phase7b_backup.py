import json
import math
import os
import ollama


# ============================================================
# CONFIGURATION
# ============================================================

BASE = r"C:\OllamaAI"

DATABASE = os.path.join(
    BASE,
    "rag",
    "vector_store.json"
)

SOURCE_INFO = os.path.join(
    BASE,
    "knowledge",
    "source_info.json"
)

MEMORY_FILE = os.path.join(
    BASE,
    "memory",
    "memory.json"
)

MODEL = "paramedic-ai"
EMBED_MODEL = "nomic-embed-text"

TOP_K = 3
MIN_SIMILARITY = 0.35


# ============================================================
# MEMORY
# ============================================================

def load_memory():

    try:

        with open(
            MEMORY_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            return json.load(f)

    except:

        return {
            "user": {
                "name": "",
                "preferences": [],
                "learning_goals": [],
                "projects": []
            },
            "assistant": {
                "notes": []
            }
        }


def save_memory(memory):

    os.makedirs(
        os.path.dirname(MEMORY_FILE),
        exist_ok=True
    )

    with open(
        MEMORY_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            memory,
            f,
            indent=4
        )


def memory_text(memory):

    return json.dumps(
        memory,
        indent=2
    )


# ============================================================
# EMS KNOWLEDGE SEARCH
# ============================================================

def search_ems_knowledge(question: str) -> str:

    try:

        with open(
            DATABASE,
            "r",
            encoding="utf-8"
        ) as f:

            documents = json.load(f)

    except FileNotFoundError:

        return "EMS knowledge database not found."

    try:

        with open(
            SOURCE_INFO,
            "r",
            encoding="utf-8"
        ) as f:

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
            for a, b in zip(
                query_embedding,
                embedding
            )
        )

        magnitude_a = math.sqrt(
            sum(
                a * a
                for a in query_embedding
            )
        )

        magnitude_b = math.sqrt(
            sum(
                b * b
                for b in embedding
            )
        )

        if magnitude_a == 0 or magnitude_b == 0:
            continue

        similarity = (
            dot /
            (magnitude_a * magnitude_b)
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

            "document_type": metadata.get(
                "document_type",
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

        return (
            "No sufficiently relevant EMS "
            "references were found."
        )

    return json.dumps(
        results[:TOP_K],
        indent=2
    )


# ============================================================
# CALCULATOR
# ============================================================

def calculate(expression: str) -> str:

    allowed = "0123456789+-*/(). "

    if any(
        character not in allowed
        for character in expression
    ):

        return (
            "ERROR: Only basic arithmetic "
            "is allowed."
        )

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
# MEMORY TOOLS
# ============================================================

def remember(
    category: str,
    information: str
) -> str:

    memory = load_memory()

    categories = {
        "preference": "preferences",
        "goal": "learning_goals",
        "project": "projects"
    }

    if category not in categories:

        return (
            "Invalid memory category. "
            "Use preference, goal, or project."
        )

    information = information.strip()

    if not information:

        return "Memory cannot be empty."

    target = categories[category]

    if information not in memory["user"][target]:

        memory["user"][target].append(
            information
        )

        save_memory(memory)

    return (
        f"Saved to {target}: "
        f"{information}"
    )


# ============================================================
# TOOL REGISTRY
# ============================================================

TOOLS = [
    search_ems_knowledge,
    calculate,
    remember
]

FUNCTIONS = {

    "search_ems_knowledge":
        search_ems_knowledge,

    "calculate":
        calculate,

    "remember":
        remember
}


# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are Paramedic AI.

You are an EMS educational and decision-support assistant.

Your available tools are:

1. search_ems_knowledge
   Search the user's local EMS reference library.

2. calculate
   Perform basic arithmetic.

3. remember
   Save an explicit user preference, learning goal, or project.

IMPORTANT SAFETY RULES:

- Do not invent EMS protocols.
- Do not fabricate sources.
- Do not fabricate medication doses.
- Do not claim a source is current unless its metadata supports that.
- Pay attention to jurisdiction and effective date.
- Clearly identify TEST ONLY or TRAINING documents.
- Do not treat user memory as medical evidence.
- Do not permanently store patient information.
- Do not use memory to infer medical facts about a patient.
- For real patient care, current applicable local protocols,
  medical direction, and qualified clinicians take precedence.
- This system is for education and decision support.

Use tools when they improve the answer.

If the user explicitly asks you to remember something,
you may use the remember tool.

Do not remember patient scenarios automatically.
"""


# ============================================================
# MAIN AGENT
# ============================================================

def main():

    memory = load_memory()

    messages = [

        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },

        {
            "role": "system",
            "content":
                "Current user memory:\n"
                + memory_text(memory)
        }

    ]

    print("")
    print("========================================")
    print("          PARAMEDIC AI")
    print("========================================")
    print("")
    print("Qwen3 4B: ONLINE")
    print("EMS RAG: ENABLED")
    print("Memory: ENABLED")
    print("Tools: ENABLED")
    print("")
    print("Commands:")
    print("  /memory")
    print("  /clear")
    print("  /exit")
    print("")
    print("========================================")
    print("")

    while True:

        user_input = input("You: ").strip()

        if not user_input:
            continue

        # --------------------------------------------
        # EXIT
        # --------------------------------------------

        if user_input.lower() == "/exit":

            print("Goodbye.")
            break

        # --------------------------------------------
        # MEMORY VIEW
        # --------------------------------------------

        if user_input.lower() == "/memory":

            memory = load_memory()

            print("")
            print(
                json.dumps(
                    memory,
                    indent=4
                )
            )
            print("")

            continue

        # --------------------------------------------
        # CLEAR CONVERSATION
        # --------------------------------------------

        if user_input.lower() == "/clear":

            memory = load_memory()

            messages = [

                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },

                {
                    "role": "system",
                    "content":
                        "Current user memory:\n"
                        + memory_text(memory)
                }

            ]

            print("Conversation cleared.")
            print("")

            continue

        # --------------------------------------------
        # USER MESSAGE
        # --------------------------------------------

        messages.append({

            "role": "user",
            "content": user_input

        })

        # --------------------------------------------
        # TOOL LOOP
        # --------------------------------------------

        while True:

            response = ollama.chat(

                model=MODEL,

                messages=messages,

                tools=TOOLS
            )

            assistant_message = response["message"]

            messages.append(
                assistant_message
            )

            tool_calls = assistant_message.get(
                "tool_calls",
                []
            )

            # No tool call = final answer

            if not tool_calls:

                print("")
                print(
                    assistant_message.get(
                        "content",
                        ""
                    )
                )
                print("")

                break

            # ----------------------------------------
            # EXECUTE REQUESTED TOOLS
            # ----------------------------------------

            for tool_call in tool_calls:

                function_name = (
                    tool_call["function"]["name"]
                )

                arguments = (
                    tool_call["function"]["arguments"]
                )

                print(
                    f"[Tool: {function_name}]"
                )

                function = FUNCTIONS.get(
                    function_name
                )

                if function is None:

                    result = (
                        "ERROR: Tool does not exist."
                    )

                else:

                    try:

                        result = function(
                            **arguments
                        )

                    except Exception as error:

                        result = (
                            f"ERROR: {error}"
                        )

                messages.append({

                    "role": "tool",

                    "tool_name":
                        function_name,

                    "content":
                        str(result)

                })

                # Refresh memory after a remember call

                if function_name == "remember":

                    memory = load_memory()

                    messages[1] = {

                        "role": "system",

                        "content":
                            "Current user memory:\n"
                            + memory_text(memory)

                    }


if __name__ == "__main__":

    main()