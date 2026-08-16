import json
import os
import tkinter as tk
from tkinter import ttk, messagebox


BASE = r"C:\OllamaAI"

METADATA_FILE = os.path.join(
    BASE,
    "knowledge",
    "metadata.json"
)

DOCUMENT_DIR = os.path.join(
    BASE,
    "documents"
)


def load_metadata():

    if not os.path.exists(METADATA_FILE):
        return {"documents": {}}

    with open(
        METADATA_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


class LibraryApp:

    def __init__(self, root):

        self.root = root

        self.root.title(
            "Paramedic AI — Document Library"
        )

        self.root.geometry(
            "1000x600"
        )

        self.root.configure(
            bg="#101820"
        )

        self.build_ui()
        self.refresh()

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
            text="Document Library",
            font=("Segoe UI", 11),
            fg="#45d483",
            bg="#17232d"
        ).pack(
            side="right",
            padx=20
        )

        frame = tk.Frame(
            self.root,
            bg="#101820"
        )

        frame.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=20
        )

        columns = (
            "source",
            "category",
            "status",
            "jurisdiction",
            "effective"
        )

        self.tree = ttk.Treeview(
            frame,
            columns=columns,
            show="headings"
        )

        self.tree.heading(
            "source",
            text="Source"
        )

        self.tree.heading(
            "category",
            text="Category"
        )

        self.tree.heading(
            "status",
            text="Status"
        )

        self.tree.heading(
            "jurisdiction",
            text="Jurisdiction"
        )

        self.tree.heading(
            "effective",
            text="Effective Date"
        )

        self.tree.column(
            "source",
            width=300
        )

        self.tree.column(
            "category",
            width=130
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
            width=140
        )

        self.tree.pack(
            fill="both",
            expand=True
        )

        buttons = tk.Frame(
            self.root,
            bg="#101820"
        )

        buttons.pack(
            fill="x",
            padx=20,
            pady=(0, 20)
        )

        tk.Button(
            buttons,
            text="Refresh",
            command=self.refresh,
            bg="#1976d2",
            fg="white",
            padx=20,
            pady=8
        ).pack(
            side="left"
        )

        tk.Button(
            buttons,
            text="View Details",
            command=self.view_details,
            bg="#455a64",
            fg="white",
            padx=20,
            pady=8
        ).pack(
            side="left",
            padx=10
        )

    def refresh(self):

        for item in self.tree.get_children():

            self.tree.delete(item)

        data = load_metadata()

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

    def view_details(self):

        selection = self.tree.selection()

        if not selection:

            messagebox.showinfo(
                "Document Library",
                "Select a document first."
            )

            return

        values = self.tree.item(
            selection[0],
            "values"
        )

        source = values[0]

        data = load_metadata()

        metadata = data.get(
            "documents",
            {}
        ).get(
            source,
            {}
        )

        details = json.dumps(
            metadata,
            indent=4
        )

        messagebox.showinfo(
            "Reference Details",
            details
        )


def main():

    root = tk.Tk()

    LibraryApp(
        root
    )

    root.mainloop()


if __name__ == "__main__":
    main()