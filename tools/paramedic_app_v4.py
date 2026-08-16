import json
import os
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext

import ollama


BASE = r"C:\OllamaAI"

SESSION_DIR = os.path.join(
    BASE,
    "sessions"
)

MODEL = "paramedic-ai:latest"


def ensure_sessions():

    os.makedirs(
        SESSION_DIR,
        exist_ok=True
    )


def session_path(name):

    safe = "".join(
        character
        for character in name
        if character.isalnum()
        or character in "_-"
    )

    return os.path.join(
        SESSION_DIR,
        safe + ".json"
    )


def save_session(
    name,
    messages
):

    ensure_sessions()

    path = session_path(
        name
    )

    data = {
        "session": name,
        "messages": messages
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


def load_session(name):

    path = session_path(
        name
    )

    if not os.path.exists(path):

        return []

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


class SessionApp:

    def __init__(self, root):

        self.root = root

        self.root.title(
            "Paramedic AI — Sessions"
        )

        self.root.geometry(
            "950x700"
        )

        self.messages = []

        self.session_name = (
            "default"
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
            font=(
                "Segoe UI",
                20,
                "bold"
            ),
            fg="white",
            bg="#17232d"
        ).pack(
            side="left",
            padx=20,
            pady=15
        )

        self.session_label = tk.Label(
            header,
            text="Session: default",
            fg="#45d483",
            bg="#17232d"
        )

        self.session_label.pack(
            side="right",
            padx=20
        )

        self.chat = scrolledtext.ScrolledText(
            self.root,
            wrap=tk.WORD,
            font=(
                "Segoe UI",
                11
            ),
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

        bottom = tk.Frame(
            self.root,
            bg="#101820"
        )

        bottom.pack(
            fill="x",
            padx=15,
            pady=(0, 15)
        )

        self.entry = tk.Entry(
            bottom,
            font=(
                "Segoe UI",
                12
            ),
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
            padx=20,
            pady=8
        ).pack(
            side="left",
            padx=5
        )

        tk.Button(
            bottom,
            text="Save",
            command=self.save,
            bg="#2e7d32",
            fg="white",
            padx=20,
            pady=8
        ).pack(
            side="left",
            padx=5
        )

        tk.Button(
            bottom,
            text="Load",
            command=self.load,
            bg="#455a64",
            fg="white",
            padx=20,
            pady=8
        ).pack(
            side="left",
            padx=5
        )

    def send(self, event=None):

        question = (
            self.entry.get()
            .strip()
        )

        if not question:
            return

        self.entry.delete(
            0,
            tk.END
        )

        self.messages.append({
            "role": "user",
            "content": question
        })

        self.chat.insert(
            tk.END,
            f"You:\n{question}\n\n"
        )

        self.chat.insert(
            tk.END,
            "Paramedic AI:\n"
            "Thinking...\n\n"
        )

        threading.Thread(
            target=self.ask_ai,
            args=(question,),
            daemon=True
        ).start()

    def ask_ai(self, question):

        try:

            response = ollama.chat(
                model=MODEL,
                messages=self.messages
            )

            answer = response[
                "message"
            ][
                "content"
            ]

            self.messages.append({
                "role": "assistant",
                "content": answer
            })

            self.root.after(
                0,
                self.display,
                answer
            )

        except Exception as error:

            self.root.after(
                0,
                self.display,
                f"ERROR:\n{error}"
            )

    def display(self, answer):

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

    def save(self):

        save_session(
            self.session_name,
            self.messages
        )

        messagebox.showinfo(
            "Session",
            "Session saved."
        )

    def load(self):

        messages = load_session(
            self.session_name
        )

        if not messages:

            messagebox.showinfo(
                "Session",
                "No saved session found."
            )

            return

        self.messages = messages

        self.chat.delete(
            "1.0",
            tk.END
        )

        for message in messages:

            role = message[
                "role"
            ]

            content = message[
                "content"
            ]

            label = (
                "You"
                if role == "user"
                else "Paramedic AI"
            )

            self.chat.insert(
                tk.END,
                f"{label}:\n"
                f"{content}\n\n"
            )

        self.chat.see(
            tk.END
        )


def main():

    ensure_sessions()

    root = tk.Tk()

    SessionApp(root)

    root.mainloop()


if __name__ == "__main__":

    main()