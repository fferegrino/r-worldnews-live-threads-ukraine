import base64
import logging
import random
import string
from pathlib import Path

import imgkit
import jupytext
from nbformat.notebooknode import from_dict

logger = logging.getLogger("from-jupyter")


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
    parent_dir = Path("exported", file.stem)
    parent_dir.mkdir(exist_ok=True, parents=True)

    with open(file) as w:
        notebook = jupytext.read(w)

        # if jupytext_meta := notebook["metadata"].get("jupytext"):
        #     execute = (jupytext_meta["text_representation"]["extension"] != "ipynb") and save_resources

        # if execute:
        #     ep = ExecutePreprocessor(timeout=600, kernel_name="python3")
        #     notebook, metadata = ep.preprocess(notebook, {"metadata": {"path": "."}})

    if save_resources:
        new_cells = save_cell_resources(parent_dir, notebook)
        notebook["cells"] = new_cells

    if remove_code:
        notebook["cells"] = [cell for cell in notebook["cells"] if cell["cell_type"] != "code"]

    jupytext.write(notebook, f"{file.stem}-exported.md")


def save_cell_resources(save_dir, notebook):
    new_cells = []
    for cell in notebook["cells"]:
        new_cells.append(cell)
        if outputs := cell.get("outputs", []):
            if data := outputs[0].get("data", {}):
                metadata = cell.get("metadata")
                if "image/png" in data:
                    new_cell = process_image_cell(data, metadata, save_dir)
                    new_cells.append(new_cell)
                elif "text/html" in data:
                    image_name = metadata["file"]
                    options = {"zoom": 2, "quality": 100}
                    with open("from_jupyter/dataframe.html") as r:
                        template = r.read()
                        imgkit.from_string(
                            template.replace("{{DATAFRAME}}", data["text/html"]),
                            save_dir / image_name,
                            options=options,
                        )
    return new_cells


def process_image_cell(data, metadata, parent_dir):
    image_name = metadata["file"]
    print(image_name)
    description = metadata.get("description", image_name)
    image_path = parent_dir / image_name
    with open(image_path, "wb") as fh:
        fh.write(base64.decodebytes(bytes(data["image/png"], "utf-8")))
    new_cell = make_markdown_cell(f"![{description}]({str(image_path)})")
    return new_cell
