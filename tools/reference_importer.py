import json
import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox


BASE = r"C:\OllamaAI"

DOCUMENT_DIR = os.path.join(
    BASE,
    "documents"
)

METADATA_FILE = os.path.join(
    BASE,
    "knowledge",
    "metadata.json"
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


def save_metadata(data):

    os.makedirs(
        os.path.dirname(METADATA_FILE),
        exist_ok=True
    )

    with open(
        METADATA_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            indent=4,
            ensure_ascii=False
        )


class Importer:

    def __init__(self, root):

        self.root = root

        self.root.title(
            "Paramedic AI — Import Reference"
        )

        self.root.geometry(
            "600x650"
        )

        self.root.configure(
            bg="#101820"
        )

        self.build_ui()

    def build_ui(self):

        tk.Label(
            self.root,
            text="IMPORT REFERENCE",
            font=("Segoe UI", 20, "bold"),
            fg="white",
            bg="#101820"
        ).pack(
            pady=20
        )

        tk.Button(
            self.root,
            text="Select Document",
            command=self.select_file,
            bg="#1976d2",
            fg="white",
            padx=25,
            pady=10
        ).pack(
            pady=10
        )

        self.file_label = tk.Label(
            self.root,
            text="No document selected",
            fg="#45d483",
            bg="#101820",
            wraplength=500
        )

        self.file_label.pack(
            pady=10
        )

        self.fields = {}

        field_names = [
            ("title", "Title"),
            ("category", "Category"),
            ("jurisdiction", "Jurisdiction"),
            ("document_type", "Document Type"),
            ("effective_date", "Effective Date"),
            ("status", "Status"),
            ("notes", "Notes")
        ]

        for key, label in field_names:

            tk.Label(
                self.root,
                text=label,
                fg="white",
                bg="#101820"
            ).pack(
                anchor="w",
                padx=50
            )

            entry = tk.Entry(
                self.root,
                width=60,
                bg="#1b2833",
                fg="white",
                insertbackground="white"
            )

            entry.pack(
                padx=50,
                pady=(0, 10)
            )

            self.fields[key] = entry

        self.fields["status"].insert(
            0,
            "UNKNOWN"
        )

        tk.Button(
            self.root,
            text="IMPORT",
            command=self.import_file,
            bg="#2e7d32",
            fg="white",
            font=("Segoe UI", 11, "bold"),
            padx=35,
            pady=10
        ).pack(
            pady=20
        )

        self.selected_file = None

    def select_file(self):

        path = filedialog.askopenfilename(
            title="Select Reference"
        )

        if not path:
            return

        self.selected_file = path

        self.file_label.config(
            text=path
        )

        filename = os.path.basename(
            path
        )

        if not self.fields["title"].get():

            self.fields["title"].insert(
                0,
                os.path.splitext(
                    filename
                )[0]
            )

    def import_file(self):

        if not self.selected_file:

            messagebox.showerror(
                "Import",
                "Select a document first."
            )

            return

        category = self.fields[
            "category"
        ].get().strip()

        status = self.fields[
            "status"
        ].get().strip().upper()

        if not category:

            messagebox.showerror(
                "Import",
                "Category is required."
            )

            return

        if not status:

            status = "UNKNOWN"

        filename = os.path.basename(
            self.selected_file
        )

        destination = os.path.join(
            DOCUMENT_DIR,
            filename
        )

        os.makedirs(
            DOCUMENT_DIR,
            exist_ok=True
        )

        if os.path.exists(destination):

            messagebox.showerror(
                "Import",
                "A document with this "
                "filename already exists."
            )

            return

        shutil.copy2(
            self.selected_file,
            destination
        )

        metadata = load_metadata()

        documents = metadata.setdefault(
            "documents",
            {}
        )

        documents[filename] = {

            "title":
                self.fields[
                    "title"
                ].get().strip(),

            "source":
                filename,

            "category":
                category,

            "jurisdiction":
                self.fields[
                    "jurisdiction"
                ].get().strip()
                or "UNSPECIFIED",

            "document_type":
                self.fields[
                    "document_type"
                ].get().strip()
                or "REFERENCE",

            "effective_date":
                self.fields[
                    "effective_date"
                ].get().strip()
                or "UNKNOWN",

            "status":
                status,

            "notes":
                self.fields[
                    "notes"
                ].get().strip()
        }

        save_metadata(
            metadata
        )

        messagebox.showinfo(
            "Import Complete",
            "Reference imported successfully.\n\n"
            "It is registered in the library.\n\n"
            "It has NOT been embedded yet."
        )

        self.root.destroy()


def main():

    root = tk.Tk()

    Importer(root)

    root.mainloop()


if __name__ == "__main__":

    main()