import logging
from pathlib import Path

import jupytext

from from_jupyter.gist_client import GistClient
from from_jupyter.utils import hash_string

logger = logging.getLogger("gistify")


def gistify(file: Path, personal_token: str):
    gist_client = GistClient(personal_token)

    with open(file) as w:
        notebook = jupytext.read(w)

    file_hash = hash_string(file.name)

    for idx, cell in enumerate(notebook["cells"], 1):
        metadata = cell.get("metadata")
        if cell["cell_type"] == "code":
            gist_id = metadata.get("gist_id")
            gist = metadata.get("gist")

            if gist_id or gist:
                name, _, extension = gist.partition(".")
                new_file_name = f"{name}-{file_hash}.{extension}"
                description = f"File {gist} for the file {file.name}"

                if gist_id:
                    gist_id = gist_client.update_gist(gist_id, description, new_file_name, cell["source"])
                elif gist:
                    gist_id = gist_client.publish_gist(description, new_file_name, cell["source"])

                metadata["gist_id"] = gist_id
            else:
                logger.warning(f"Code cell at {idx} does not contain a gist attribute")

    jupytext.write(notebook, file)
