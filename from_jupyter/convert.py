import jupytext
import imgkit
import base64
from pathlib import Path
from nbformat.notebooknode import from_dict
import random
import string

from nbconvert.preprocessors import ExecutePreprocessor


def make_markdown_cell(content):
    return from_dict(
        {
            "cell_type": "markdown",
            "id": "".join(random.choice(string.ascii_lowercase) for i in range(10)),
            "metadata": {},
            "source": content,
        }
    )


def convert_to_md(file, execute=False, remove_code=False, save_resources=True):
    file = Path(file)
    with open(file) as w:
        notebook = jupytext.read(w)

        if jupytext_meta := notebook["metadata"].get("jupytext"):
            execute = (jupytext_meta["text_representation"]["extension"] != "ipynb") and save_resources

    image_count = 0
    table_count = 0

    if save_resources:
        parent_dir = Path(file.stem)
        parent_dir.mkdir(exist_ok=True)

        new_cells = []
        if execute:
            ep = ExecutePreprocessor(timeout=600, kernel_name="python3")
            notebook, metadata = ep.preprocess(notebook, {"metadata": {"path": "."}})

        for cell in notebook["cells"]:
            new_cells.append(cell)
            if outputs := cell.get("outputs", []):
                if data := outputs[0].get("data", {}):
                    metadata = cell.get("metadata")
                    if "image/png" in data:
                        new_cell = process_image_cell(data, image_count, metadata, parent_dir)
                        new_cells.append(new_cell)
                        image_count += 1
                    elif "text/html" in data:

                        image_name = metadata.get("file", f"table-{table_count}.jpg")
                        options = {"zoom": 2, "quality": 100}
                        with open("from_jupyter/dataframe.html") as r:
                            template = r.read()
                            imgkit.from_string(
                                template.replace("{{DATAFRAME}}", data["text/html"]),
                                parent_dir / image_name,
                                options=options,
                            )
                            table_count += 1
        notebook["cells"] = new_cells

    if remove_code:
        notebook["cells"] = [cell for cell in notebook["cells"] if cell["cell_type"] != "code"]

    jupytext.write(notebook, f"{file.stem}-exported.md")


def process_image_cell(data, image_count, metadata, parent_dir):
    image_name = metadata.get("file", f"image-{image_count}.png")
    print(image_name)
    description = metadata.get("description", image_name)
    image_path = parent_dir / image_name
    with open(image_path, "wb") as fh:
        fh.write(base64.decodebytes(bytes(data["image/png"], "utf-8")))
    new_cell = make_markdown_cell(f"![{description}]({str(image_path)})")
    return new_cell
