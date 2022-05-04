import base64
import logging
from pathlib import Path

import jupytext

from from_jupyter.gist_client import GistClient
from from_jupyter.utils import hash_string

logger = logging.getLogger("gistify")


def export_images(file: Path):
    with open(file) as w:
        notebook = jupytext.read(w)

    for idx, cell in enumerate(notebook["cells"], 1):
        if cell["cell_type"] == "code":
            if outputs := cell.get("outputs", []):
                file = cell.get("metadata", {}).get("file")
                if data := outputs[0].get("data", {}):
                    if "image/png" in data:
                        if file:
                            with open(file, "wb") as fh:
                                fh.write(base64.decodebytes(bytes(data["image/png"], "utf-8")))
