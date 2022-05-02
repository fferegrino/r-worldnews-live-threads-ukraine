import click

from from_jupyter.convert import convert_to_md


@click.group()
def cli():
    pass

@cli.command()
@click.argument('file')
@click.option('--no-code', '-nc', is_flag=True, show_default=True, default=False,)
@click.option('--resources/--no-resources', '-s', is_flag=True, show_default=True, default=True,)
def md(file, no_code, resources):
    convert_to_md(file, remove_code=no_code, save_resources=resources)

if __name__ == '__main__':
    cli()