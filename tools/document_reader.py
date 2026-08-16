import os

import PyPDF2
from docx import Document


def read_txt(path):

    with open(
        path,
        "r",
        encoding="utf-8",
        errors="replace"
    ) as f:

        return f.read()


def read_pdf(path):

    text = []

    with open(
        path,
        "rb"
    ) as f:

        reader = PyPDF2.PdfReader(f)

        for page in reader.pages:

            page_text = page.extract_text()

            if page_text:

                text.append(
                    page_text
                )

    return "\n\n".join(text)


def read_docx(path):

    document = Document(path)

    paragraphs = []

    for paragraph in document.paragraphs:

        if paragraph.text.strip():

            paragraphs.append(
                paragraph.text
            )

    return "\n\n".join(
        paragraphs
    )


def read_document(path):

    if not os.path.exists(path):

        raise FileNotFoundError(
            path
        )

    extension = (
        os.path.splitext(path)[1]
        .lower()
    )

    if extension == ".txt":

        return read_txt(path)

    if extension == ".pdf":

        return read_pdf(path)

    if extension == ".docx":

        return read_docx(path)

    raise ValueError(
        f"Unsupported file type: "
        f"{extension}"
    )


def main():

    path = input(
        "Document path: "
    ).strip().strip('"')

    try:

        text = read_document(
            path
        )

        print("")
        print(
            "Successfully extracted "
            f"{len(text)} characters."
        )

        print("")
        print("----- BEGIN TEXT -----")
        print("")
        print(text[:3000])
        print("")
        print("----- END PREVIEW -----")

    except Exception as error:

        print("")
        print(
            f"ERROR: {error}"
        )


if __name__ == "__main__":

    main()