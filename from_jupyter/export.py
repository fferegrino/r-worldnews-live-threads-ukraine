import base64
import logging
import pkgutil
from pathlib import Path

import imgkit
import jupytext

logger = logging.getLogger("export")


def export_images(parent_dir: Path, file: Path):

    image_output_folder = Path(parent_dir, file.stem)
    image_output_folder.mkdir(exist_ok=True)

    with open(file) as w:
        notebook = jupytext.read(w)

    for idx, cell in enumerate(notebook["cells"], 1):
        if (cell["cell_type"] == "code") and (outputs := cell.get("outputs", [])):
            image_outputs = [output for output in outputs if ("data" in output) and "image/png" in output["data"]]
            if len(image_outputs) > 0:
                image_name = cell.get("metadata", {}).get("image")
                with open(image_output_folder / image_name, "wb") as fh:
                    fh.write(base64.decodebytes(bytes(image_outputs[0]["data"]["image/png"], "utf-8")))


def export_dataframes(parent_dir: Path, file: Path):
    template = pkgutil.get_data(__name__, "dataframe.html").decode("utf-8")

    image_output_folder = Path(parent_dir, file.stem)
    image_output_folder.mkdir(exist_ok=True)

    with open(file) as w:
        notebook = jupytext.read(w)

    for idx, cell in enumerate(notebook["cells"], 1):
        dataframe_name = cell.get("metadata", {}).get("dataframe")
        if (cell["cell_type"] == "code") and dataframe_name and (outputs := cell.get("outputs", [])):
            image_outputs = [output for output in outputs if ("data" in output) and "text/html" in output["data"]]
            if len(image_outputs) > 0:
                options = {"zoom": 2, "quality": 100, "quiet": ""}
                imgkit.from_string(
                    template.replace("{{DATAFRAME}}", image_outputs[0]["data"]["text/html"]),
                    image_output_folder / dataframe_name,
                    options=options,
                )
