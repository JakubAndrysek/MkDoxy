from pathlib import Path

import click

from mkdoxy.migration import update_new_config


@click.group()
def cli():
    pass


@click.command()
@click.argument("yaml_file", type=click.Path(exists=True))
@click.option("--no-backup", is_flag=True, help="Do not backup old config to mkdocs.old.yaml")
def migrate(yaml_file, no_backup):
    """
    Migrate mkdoxy config to new version
    @details
    @param yaml_file: Path to mkdocs.yaml file
    @param no_backup: Do not backup old config to mkdocs.old.yaml
    """
    backup_file_name = "mkdocs.old.yaml"
    update_new_config(Path(yaml_file), not no_backup, backup_file_name)
    click.echo("Migration completed successfully")
    if not no_backup:
        click.echo(f"Old config was not backed up as '{backup_file_name}'")


# @click.command()
# def version():
#     package_version = importlib.metadata.version('mkdoxy')
#     click.echo(f"Version: {package_version}")


cli.add_command(migrate)
# cli.add_command(version)

if __name__ == "__main__":
    cli()
