import json
import os
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext

import ollama

from intent_search import search


BASE = r"C:\OllamaAI"

METADATA_FILE = os.path.join(
    BASE,
    "knowledge",
    "metadata.json"
)

MODEL = "paramedic-ai:latest"


class ParamedicApp:

    def __init__(self, root):

        self.root = root

        self.root.title(
            "Paramedic AI"
        )

        self.root.geometry(
            "1200x750"
        )

        self.root.configure(
            bg="#101820"
        )

        self.build_ui()

    def build_ui(self):

        header = tk.Frame(
            self.root,
            bg="#17232d"
        )

        header.pack(
            fill="x"
        )

        tk.Label(
            header,
            text="PARAMEDIC AI",
            font=("Segoe UI", 20, "bold"),
            fg="white",
            bg="#17232d"
        ).pack(
            side="left",
            padx=20,
            pady=15
        )

        tk.Label(
            header,
            text="EMS Education & Decision Support",
            font=("Segoe UI", 10),
            fg="#45d483",
            bg="#17232d"
        ).pack(
            side="right",
            padx=20
        )

        self.notebook = ttk.Notebook(
            self.root
        )

        self.notebook.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

        self.chat_tab = tk.Frame(
            self.notebook,
            bg="#101820"
        )

        self.library_tab = tk.Frame(
            self.notebook,
            bg="#101820"
        )

        self.notebook.add(
            self.chat_tab,
            text="  Chat  "
        )

        self.notebook.add(
            self.library_tab,
            text="  References  "
        )

        self.build_chat()

        self.build_library()

    # -------------------------
    # CHAT
    # -------------------------

    def build_chat(self):

        main = tk.Frame(
            self.chat_tab,
            bg="#101820"
        )

        main.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=15
        )

        left = tk.Frame(
            main,
            bg="#101820"
        )

        left.pack(
            side="left",
            fill="both",
            expand=True
        )

        right = tk.Frame(
            main,
            bg="#17232d",
            width=330
        )

        right.pack(
            side="right",
            fill="y",
            padx=(15, 0)
        )

        right.pack_propagate(
            False
        )

        self.chat = scrolledtext.ScrolledText(
            left,
            wrap=tk.WORD,
            font=("Segoe UI", 11),
            bg="#0d141a",
            fg="white",
            insertbackground="white",
            padx=15,
            pady=15
        )

        self.chat.pack(
            fill="both",
            expand=True
        )

        self.chat.insert(
            tk.END,
            "Paramedic AI\n"
            "Ready.\n\n"
        )

        tk.Label(
            right,
            text="REFERENCES",
            font=("Segoe UI", 12, "bold"),
            fg="white",
            bg="#17232d"
        ).pack(
            anchor="w",
            padx=15,
            pady=15
        )

        self.references = scrolledtext.ScrolledText(
            right,
            wrap=tk.WORD,
            font=("Segoe UI", 9),
            bg="#0d141a",
            fg="#d8e2ea",
            padx=10,
            pady=10
        )

        self.references.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=(0, 15)
        )

        bottom = tk.Frame(
            self.chat_tab,
            bg="#101820"
        )

        bottom.pack(
            fill="x",
            padx=15,
            pady=(0, 15)
        )

        self.entry = tk.Entry(
            bottom,
            font=("Segoe UI", 12),
            bg="#1b2833",
            fg="white",
            insertbackground="white"
        )

        self.entry.pack(
            side="left",
            fill="x",
            expand=True,
            ipady=10
        )

        self.entry.bind(
            "<Return>",
            self.send_message
        )

        tk.Button(
            bottom,
            text="Send",
            command=self.send_message,
            bg="#1976d2",
            fg="white",
            font=("Segoe UI", 11, "bold"),
            padx=25,
            pady=8
        ).pack(
            side="right",
            padx=(10, 0)
        )

    def send_message(self, event=None):

        question = self.entry.get().strip()

        if not question:
            return

        self.entry.delete(
            0,
            tk.END
        )

        self.chat.insert(
            tk.END,
            f"You:\n{question}\n\n"
        )

        self.chat.insert(
            tk.END,
            "Paramedic AI:\n"
            "Thinking...\n\n"
        )

        self.chat.see(
            tk.END
        )

        self.references.delete(
            "1.0",
            tk.END
        )

        thread = threading.Thread(
            target=self.process_question,
            args=(question,),
            daemon=True
        )

        thread.start()

    def process_question(self, question):

        try:

            intent, results = search(
                question
            )

            context = []

            for result in results:

                context.append(
                    f"""
SOURCE:
{result['title']}

CATEGORY:
{result['category']}

STATUS:
{result['status']}

JURISDICTION:
{result['jurisdiction']}

EFFECTIVE DATE:
{result['effective_date']}

TEXT:
{result['text']}
"""
                )

            context_text = (
                "\n".join(context)
                if context
                else
                "No relevant references found."
            )

            prompt = f"""
You are Paramedic AI.

Intent:
{intent}

Answer the user's question using
the retrieved references.

Rules:

- Be concise.
- Do not invent information.
- Do not invent medication doses.
- Do not present training material
  as current operational protocol.
- Do not assume jurisdiction.
- State uncertainty clearly.

Question:
{question}

References:
{context_text}
"""

            response = ollama.chat(
                model=MODEL,
                messages=[
                    {
                        "role": "system",
                        "content":
                            "You are a careful "
                            "EMS education "
                            "assistant."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            answer = response[
                "message"
            ][
                "content"
            ]

            self.root.after(
                0,
                self.show_answer,
                answer,
                intent,
                results
            )

        except Exception as error:

            self.root.after(
                0,
                self.show_error,
                str(error)
            )

    def show_answer(
        self,
        answer,
        intent,
        results
    ):

        current = self.chat.get(
            "1.0",
            tk.END
        )

        marker = (
            "Paramedic AI:\n"
            "Thinking...\n\n"
        )

        position = current.rfind(
            marker
        )

        if position != -1:

            self.chat.delete(
                f"1.0+{position}c",
                f"1.0+"
                f"{position + len(marker)}c"
            )

        self.chat.insert(
            tk.END,
            f"Paramedic AI:\n"
            f"{answer}\n\n"
        )

        self.chat.see(
            tk.END
        )

        self.references.delete(
            "1.0",
            tk.END
        )

        self.references.insert(
            tk.END,
            f"Intent: {intent}\n\n"
        )

        for number, result in enumerate(
            results,
            start=1
        ):

            self.references.insert(
                tk.END,
                f"[{number}] "
                f"{result['title']}\n"
            )

            self.references.insert(
                tk.END,
                f"Category: "
                f"{result['category']}\n"
            )

            self.references.insert(
                tk.END,
                f"Status: "
                f"{result['status']}\n"
            )

            self.references.insert(
                tk.END,
                f"Jurisdiction: "
                f"{result['jurisdiction']}\n"
            )

            self.references.insert(
                tk.END,
                f"Effective: "
                f"{result['effective_date']}\n\n"
            )

    def show_error(self, error):

        self.chat.insert(
            tk.END,
            f"ERROR:\n{error}\n\n"
        )

    # -------------------------
    # LIBRARY
    # -------------------------

    def build_library(self):

        top = tk.Frame(
            self.library_tab,
            bg="#101820"
        )

        top.pack(
            fill="x",
            padx=15,
            pady=15
        )

        tk.Button(
            top,
            text="Refresh",
            command=self.refresh_library,
            bg="#1976d2",
            fg="white",
            padx=20,
            pady=8
        ).pack(
            side="left"
        )

        columns = (
            "source",
            "category",
            "status",
            "jurisdiction",
            "effective"
        )

        self.tree = ttk.Treeview(
            self.library_tab,
            columns=columns,
            show="headings"
        )

        headings = {
            "source": "Source",
            "category": "Category",
            "status": "Status",
            "jurisdiction": "Jurisdiction",
            "effective": "Effective Date"
        }

        for column, heading in headings.items():

            self.tree.heading(
                column,
                text=heading
            )

        self.tree.column(
            "source",
            width=350
        )

        self.tree.column(
            "category",
            width=150
        )

        self.tree.column(
            "status",
            width=120
        )

        self.tree.column(
            "jurisdiction",
            width=180
        )

        self.tree.column(
            "effective",
            width=150
        )

        self.tree.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=(0, 15)
        )

        self.refresh_library()

    def refresh_library(self):

        for item in self.tree.get_children():

            self.tree.delete(item)

        if not os.path.exists(
            METADATA_FILE
        ):

            return

        with open(
            METADATA_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            data = json.load(f)

        documents = data.get(
            "documents",
            {}
        )

        for source, metadata in documents.items():

            self.tree.insert(
                "",
                "end",
                values=(
                    source,
                    metadata.get(
                        "category",
                        "UNKNOWN"
                    ),
                    metadata.get(
                        "status",
                        "UNKNOWN"
                    ),
                    metadata.get(
                        "jurisdiction",
                        "UNKNOWN"
                    ),
                    metadata.get(
                        "effective_date",
                        "UNKNOWN"
                    )
                )
            )


def main():

    root = tk.Tk()

    ParamedicApp(
        root
    )

    root.mainloop()


if __name__ == "__main__":

    main()