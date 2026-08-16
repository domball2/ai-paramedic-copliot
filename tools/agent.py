import json
import math
import os
from datetime import datetime

import ollama


# ============================================================
# CONFIGURATION
# ============================================================

BASE = r"C:\OllamaAI"

DATABASE = os.path.join(
    BASE, "rag", "vector_store.json"
)

SOURCE_INFO = os.path.join(
    BASE, "knowledge", "source_info.json"
)

MEMORY_FILE = os.path.join(
    BASE, "memory", "memory.json"
)

SESSION_DIR = os.path.join(
    BASE, "sessions"
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
# RAG SEARCH
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
# MEMORY TOOL
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
            "Invalid category. "
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
# SESSION MANAGEMENT
# ============================================================

def ensure_sessions():

    os.makedirs(
        SESSION_DIR,
        exist_ok=True
    )


def new_session():

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    return f"session_{timestamp}"


def session_path(session_name):

    safe_name = "".join(
        character
        for character in session_name
        if character.isalnum()
        or character in "_-"
    )

    return os.path.join(
        SESSION_DIR,
        safe_name + ".json"
    )


def save_session(
    session_name,
    messages
):

    ensure_sessions()

    path = session_path(
        session_name
    )

    serializable_messages = []

    for message in messages:

        if hasattr(message, "model_dump"):

            message = message.model_dump()

        elif hasattr(message, "dict"):

            message = message.dict()

        serializable_messages.append(message)

    data = {
        "session": session_name,
        "updated": datetime.now().isoformat(),
        "messages": serializable_messages
    }

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

    return path


def load_session(session_name):

    path = session_path(
        session_name
    )

    if not os.path.exists(path):

        return None

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as f:

        data = json.load(f)

    return data.get(
        "messages",
        []
    )


def list_sessions():

    ensure_sessions()

    files = []

    for filename in os.listdir(
        SESSION_DIR
    ):

        if filename.endswith(".json"):

            files.append(
                filename[:-5]
            )

    return sorted(
        files,
        reverse=True
    )
def save_session(
    session_name,
    messages
):

    ensure_sessions()

    path = session_path(
        session_name
    )

    serializable_messages = []

    for message in messages:

        if hasattr(message, "model_dump"):

            message = message.model_dump()

        elif hasattr(message, "dict"):

            message = message.dict()

        serializable_messages.append(message)

    data = {
        "session": session_name,
        "updated": datetime.now().isoformat(),
        "messages": serializable_messages
    }

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

    return path


def load_session(session_name):

    path = session_path(
        session_name
    )

    if not os.path.exists(path):

        return None

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as f:

        data = json.load(f)

    return data.get(
        "messages",
        []
    )


def list_sessions():

    ensure_sessions()

    files = []

    for filename in os.listdir(
        SESSION_DIR
    ):

        if filename.endswith(".json"):

            files.append(
                filename[:-5]
            )

    return sorted(
        files,
        reverse=True
    )
    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    return f"session_{timestamp}"




def load_session(
    session_name
):

    path = session_path(
        session_name
    )

    if not os.path.exists(path):

        return None

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as f:

        data = json.load(f)

    return data.get(
        "messages",
        []
    )


def list_sessions():

    ensure_sessions()

    files = []

    for filename in os.listdir(
        SESSION_DIR
    ):

        if filename.endswith(".json"):

            files.append(
                filename[:-5]
            )

    return sorted(
        files,
        reverse=True
    )


# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are Paramedic AI.

You are an EMS educational and decision-support assistant.

You have three tools:

search_ems_knowledge
calculate
remember

IMPORTANT:

- Do not invent EMS protocols.
- Do not fabricate sources.
- Do not fabricate medication doses.
- Pay attention to jurisdiction and effective date.
- Clearly identify TEST ONLY or TRAINING documents.
- User memory is not medical evidence.
- Do not permanently remember patient information automatically.
- Current applicable local EMS protocols and medical direction take
  precedence for real patient care.
- This system is for education and decision support.
"""


# ============================================================
# INITIAL MESSAGES
# ============================================================

def initial_messages():

    memory = load_memory()

    return [

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
# MAIN
# ============================================================

def main():

    ensure_sessions()

    session_name = new_session()

    messages = initial_messages()

    print("")
    print("========================================")
    print("          PARAMEDIC AI")
    print("========================================")
    print("")
    print("Session:", session_name)
    print("Qwen3 4B: ONLINE")
    print("EMS RAG: ENABLED")
    print("Memory: ENABLED")
    print("Tools: ENABLED")
    print("")
    print("Commands:")
    print("  /new")
    print("  /save")
    print("  /sessions")
    print("  /load SESSION")
    print("  /memory")
    print("  /clear")
    print("  /exit")
    print("")

    while True:

        user_input = input(
            "You: "
        ).strip()

        if not user_input:
            continue

        # ----------------------------------------------------
        # EXIT
        # ----------------------------------------------------

        if user_input.lower() == "/exit":

            save_session(
                session_name,
                messages
            )

            print("")
            print(
                "Session saved:",
                session_name
            )

            print("Goodbye.")

            break

        # ----------------------------------------------------
        # NEW SESSION
        # ----------------------------------------------------

        if user_input.lower() == "/new":

            save_session(
                session_name,
                messages
            )

            session_name = new_session()

            messages = initial_messages()

            print("")
            print(
                "New session:",
                session_name
            )
            print("")

            continue

        # ----------------------------------------------------
        # SAVE
        # ----------------------------------------------------

        if user_input.lower() == "/save":

            save_session(
                session_name,
                messages
            )

            print(
                "Saved:",
                session_name
            )

            continue

        # ----------------------------------------------------
        # LIST SESSIONS
        # ----------------------------------------------------

        if user_input.lower() == "/sessions":

            sessions = list_sessions()

            print("")

            if not sessions:

                print("No saved sessions.")

            else:

                for session in sessions:

                    print(
                        " ",
                        session
                    )

            print("")

            continue

        # ----------------------------------------------------
        # LOAD SESSION
        # ----------------------------------------------------

        if user_input.lower().startswith(
            "/load "
        ):

            requested = user_input[6:].strip()

            loaded = load_session(
                requested
            )

            if loaded is None:

                print(
                    "Session not found."
                )

            else:

                session_name = requested

                messages = loaded

                print(
                    "Loaded:",
                    session_name
                )

            print("")

            continue

        # ----------------------------------------------------
        # MEMORY
        # ----------------------------------------------------

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

        # ----------------------------------------------------
        # CLEAR
        # ----------------------------------------------------

        if user_input.lower() == "/clear":

            messages = initial_messages()

            print(
                "Current conversation cleared."
            )

            print(
                "Persistent memory was not deleted."
            )

            print("")

            continue

        # ----------------------------------------------------
        # NORMAL USER MESSAGE
        # ----------------------------------------------------

        messages.append({

            "role": "user",

            "content": user_input

        })

        # ----------------------------------------------------
        # AI / TOOL LOOP
        # ----------------------------------------------------

        while True:

            response = ollama.chat(

                model=MODEL,

                messages=messages,

                tools=TOOLS

            )

            assistant_message = (
                response["message"]
            )

            messages.append(
                assistant_message
            )

            tool_calls = (
                assistant_message.get(
                    "tool_calls",
                    []
                )
            )

            # Final response

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

            # Execute tools

            for tool_call in tool_calls:

                function_name = (
                    tool_call["function"]["name"]
                )

                arguments = (
                    tool_call["function"]
                    ["arguments"]
                )

                print(
                    f"[Tool: {function_name}]"
                )

                function = FUNCTIONS.get(
                    function_name
                )

                if function is None:

                    result = (
                        "ERROR: Unknown tool."
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

                # Refresh memory

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