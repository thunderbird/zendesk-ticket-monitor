"""CLI commands."""

import click
from spike_monitor.config import Config


@click.group()
def main():
    """Spike Monitor CLI."""
    pass


@main.command()
@click.option("--config", required=True)
def validate(config):
    """Validate config."""
    cfg = Config.from_yaml(config)
    click.echo("Config valid!")


@main.command()
@click.option("--config", required=True)
def run_once(config):
    """Run once."""
    cfg = Config.from_yaml(config)
    click.echo("Running...")
