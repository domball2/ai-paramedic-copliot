import tkinter as tk
from tkinter import scrolledtext
import threading

import ollama

from intent_search import search
from safety_gate import assess_question


MODEL = "paramedic-ai:latest"


SYSTEM_PROMPT = """
You are Paramedic AI.

You are an EMS education and
decision-support assistant.

Be concise and clear.

Do not invent:
- protocols
- medication doses
- contraindications
- clinical facts

Do not present training material
as a current local protocol.

When a question requires current
protocol information, the user must
verify the answer against the applicable
local EMS protocol and medical direction.

If verified source information is
unavailable, say so clearly.
"""


class SafetyApp:

    def __init__(self, root):

        self.root = root

        root.title(
            "Paramedic AI — Safety Test"
        )

        root.geometry(
            "900x650"
        )

        self.chat = scrolledtext.ScrolledText(
            root,
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
            expand=True,
            padx=15,
            pady=15
        )

        self.chat.insert(
            tk.END,
            "Paramedic AI\n"
            "Safety gate enabled.\n\n"
        )

        bottom = tk.Frame(
            root,
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
            self.send
        )

        tk.Button(
            bottom,
            text="Send",
            command=self.send,
            bg="#1976d2",
            fg="white",
            padx=25,
            pady=8
        ).pack(
            side="right",
            padx=(10, 0)
        )

    def send(self, event=None):

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
            "Checking safety...\n\n"
        )

        threading.Thread(
            target=self.process,
            args=(question,),
            daemon=True
        ).start()

    def process(self, question):

        try:

            safety = assess_question(
                question
            )

            intent, results = search(
                question
            )

            context = ""

            for result in results:

                context += f"""
SOURCE: {result['title']}
CATEGORY: {result['category']}
STATUS: {result['status']}
JURISDICTION: {result['jurisdiction']}
EFFECTIVE DATE: {result['effective_date']}

TEXT:
{result['text']}

"""

            if not context:

                context = (
                    "No verified reference "
                    "was retrieved."
                )

            if safety["risk"] == "HIGH":

                warning = """
This question was classified as
HIGH RISK.

Use only verified, applicable clinical
references for operational decisions.

Do not treat this response as a
replacement for local EMS protocol,
medical direction, or clinical judgment.
"""

            else:

                warning = ""

            prompt = f"""
{SYSTEM_PROMPT}

{safety}

{warning}

Detected intent:
{intent}

Retrieved references:
{context}

User question:
{question}
"""

            response = ollama.chat(
                model=MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": SYSTEM_PROMPT
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
                self.show,
                safety,
                answer
            )

        except Exception as error:

            self.root.after(
                0,
                self.show_error,
                error
            )

    def show(
        self,
        safety,
        answer
    ):

        self.chat.insert(
            tk.END,
            f"Risk level: "
            f"{safety['risk']}\n\n"
        )

        if safety["risk"] == "HIGH":

            self.chat.insert(
                tk.END,
                "⚠ HIGH-RISK QUESTION\n"
                "Verify applicable local "
                "protocol/medical direction.\n\n"
            )

        self.chat.insert(
            tk.END,
            f"{answer}\n\n"
        )

        self.chat.see(
            tk.END
        )

    def show_error(self, error):

        self.chat.insert(
            tk.END,
            f"ERROR:\n{error}\n\n"
        )


def main():

    root = tk.Tk()

    SafetyApp(root)

    root.mainloop()


if __name__ == "__main__":
    main()