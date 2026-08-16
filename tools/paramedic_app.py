import tkinter as tk
from tkinter import scrolledtext
import threading
import ollama


MODEL = "paramedic-ai:latest"


class ParamedicAIApp:

    def __init__(self, root):

        self.root = root

        self.root.title(
            "Paramedic AI"
        )

        self.root.geometry(
            "900x650"
        )

        self.root.configure(
            bg="#101820"
        )

        self.build_ui()

    def build_ui(self):

        # Header

        header = tk.Frame(
            self.root,
            bg="#17232d",
            height=70
        )

        header.pack(
            fill="x"
        )

        title = tk.Label(
            header,
            text="PARAMEDIC AI",
            font=(
                "Segoe UI",
                20,
                "bold"
            ),
            fg="#ffffff",
            bg="#17232d"
        )

        title.pack(
            side="left",
            padx=20,
            pady=15
        )

        status = tk.Label(
            header,
            text="● Ollama",
            font=(
                "Segoe UI",
                10
            ),
            fg="#45d483",
            bg="#17232d"
        )

        status.pack(
            side="right",
            padx=20
        )

        # Chat area

        self.chat = scrolledtext.ScrolledText(
            self.root,
            wrap=tk.WORD,
            font=(
                "Segoe UI",
                11
            ),
            bg="#0d141a",
            fg="#ffffff",
            insertbackground="#ffffff",
            padx=15,
            pady=15
        )

        self.chat.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=(15, 10)
        )

        self.chat.insert(
            tk.END,
            "Paramedic AI\n"
            "Ready.\n\n"
        )

        # Bottom area

        bottom = tk.Frame(
            self.root,
            bg="#101820"
        )

        bottom.pack(
            fill="x",
            padx=15,
            pady=15
        )

        self.entry = tk.Entry(
            bottom,
            font=(
                "Segoe UI",
                12
            ),
            bg="#1b2833",
            fg="#ffffff",
            insertbackground="#ffffff"
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

        send_button = tk.Button(
            bottom,
            text="Send",
            command=self.send_message,
            bg="#1976d2",
            fg="#ffffff",
            activebackground="#1565c0",
            activeforeground="#ffffff",
            font=(
                "Segoe UI",
                11,
                "bold"
            ),
            padx=25,
            pady=8
        )

        send_button.pack(
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

        self.chat.see(
            tk.END
        )

        self.chat.insert(
            tk.END,
            "Paramedic AI:\nThinking...\n\n"
        )

        self.chat.see(
            tk.END
        )

        thread = threading.Thread(
            target=self.get_response,
            args=(question,),
            daemon=True
        )

        thread.start()

    def get_response(self, question):

        try:

            response = ollama.chat(
                model=MODEL,
                messages=[
                    {
                        "role": "system",
                        "content":
                            """
You are Paramedic AI.

You are an EMS education and
decision-support assistant.

Give concise, clear explanations.

Do not invent protocols,
medication doses, or clinical facts.

Do not present general training
material as a current local protocol.

Current local EMS protocols,
medical direction, and applicable
clinical authorities take precedence.

When information is uncertain,
clearly say so.
"""
                    },
                    {
                        "role": "user",
                        "content": question
                    }
                ]
            )

            answer = response[
                "message"
            ][
                "content"
            ]

        except Exception as error:

            answer = (
                "Connection error:\n\n"
                + str(error)
            )

        self.root.after(
            0,
            self.display_response,
            answer
        )

    def display_response(self, answer):

        # Remove "Thinking..." text

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

            start = (
                f"1.0+{position}c"
            )

            end = (
                f"1.0+"
                f"{position + len(marker)}c"
            )

            self.chat.delete(
                start,
                end
            )

        self.chat.insert(
            tk.END,
            f"Paramedic AI:\n"
            f"{answer}\n\n"
        )

        self.chat.see(
            tk.END
        )


def main():

    root = tk.Tk()

    app = ParamedicAIApp(
        root
    )

    root.mainloop()


if __name__ == "__main__":

    main()