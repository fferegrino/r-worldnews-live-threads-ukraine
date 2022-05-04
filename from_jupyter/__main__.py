from pathlib import Path

import click

from from_jupyter.convert import convert_to_md
from from_jupyter.gistify import gistify


@click.group()
def cli():
    pass

@cli.command()
@click.argument('file')
@click.option('--no-code', '-nc', is_flag=True, show_default=True, default=False,)
@click.option('--resources/--no-resources', '-s', is_flag=True, show_default=True, default=True,)
def md(file, no_code, resources):
    convert_to_md(file, remove_code=no_code, save_resources=resources)


@cli.command()
@click.argument("file")
@click.argument("personal-token", envvar="GITHUB_PERSONAL_TOKEN")
def gist(file, personal_token):
    gistify(Path(file), personal_token)


if __name__ == "__main__":
    cli()
