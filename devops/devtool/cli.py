"""CLI entry point for DevTool."""

import sys
from pathlib import Path
from typing import Optional

import typer

from .command_runner import CommandRunner
from .commands.docker import DockerCommand
from .commands.generic import GenericCommand
from .commands.setup import SetupCommand
from .commands.start import StartCommand
from .commands.stop import StopCommand
from .commands.test import TestCommand
from .config import DevToolConfig

app = typer.Typer(
    name="devtool",
    help="Development tool for project management",
    add_completion=False,
    no_args_is_help=False,  # We handle this ourselves
)


def get_command_handler(command_name: str, config: dict, runner: CommandRunner):
    """
    Get appropriate command handler for a command.

    Args:
        command_name: Name of the command
        config: Command configuration
        runner: Command runner instance

    Returns:
        Command handler instance
    """
    handlers = {
        "setup": SetupCommand,
        "start": StartCommand,
        "stop": StopCommand,
        "test": TestCommand,
        "d": DockerCommand,
    }

    handler_class = handlers.get(command_name, GenericCommand)
    return handler_class(config, runner)


@app.command()
def help():
    """Show help message."""
    # Custom help that doesn't show Options section
    config = DevToolConfig()
    commands = config.get_commands()
    
    print("Usage: devtool [COMMAND]")
    print()
    print("Development tool for project management")
    print()
    print("Commands:")
    print("-" * 60)
    
    # Show built-in commands
    print("  help            Show help message.")
    print("  version         Show DevTool version.")
    print("  list-commands   List all available commands.")
    
    # Show configured commands
    for cmd_name, cmd_config in commands.items():
        description = cmd_config.get("description", "No description")
        platforms = cmd_config.get("platforms", [])
        platform_str = f" [{', '.join(platforms)}]" if platforms else ""
        
        # Check if available on current platform
        if config.is_command_available(cmd_name):
            status = "[OK]"
        else:
            status = "[SKIP] (not available on this platform)"
        
        print(f"  {status:6} {cmd_name:15} - {description}{platform_str}")


@app.command()
def version():
    """Show DevTool version."""
    config = DevToolConfig()
    metadata = config.get_metadata()
    print(f"{metadata['name']} version {metadata['version']}")


@app.command()
def list_commands():
    """List all available commands."""
    config = DevToolConfig()
    commands = config.get_commands()

    if not commands:
        print("No commands configured. Create a devtool.toml file in your project root.")
        return

    print("Available commands:")
    print("-" * 60)

    for cmd_name, cmd_config in commands.items():
        description = cmd_config.get("description", "No description")
        platforms = cmd_config.get("platforms", [])
        platform_str = f" [{', '.join(platforms)}]" if platforms else ""

        # Check if available on current platform
        if config.is_command_available(cmd_name):
            status = "[OK]"
        else:
            status = "[SKIP] (not available on this platform)"

        print(f"  {status:6} {cmd_name:15} - {description}{platform_str}")


def create_command_function(command_name: str, command_config: dict):
    """
    Create a Typer command function dynamically.

    Args:
        command_name: Name of the command
        command_config: Command configuration

    Returns:
        Typer command function
    """
    # Special handling for 'd' command with subcommands
    if command_name == "d":
        def command_func(subcommand: Optional[str] = typer.Argument(None)):
            config = DevToolConfig()
            runner = CommandRunner()
            handler = get_command_handler(command_name, command_config, runner)
            exit_code = handler.execute(subcommand=subcommand)
            sys.exit(exit_code)
        
        command_func.__name__ = "d"
        command_func.__doc__ = "Docker Compose commands (up, down, re, logs)"
        return command_func

    def command_func():
        config = DevToolConfig()
        runner = CommandRunner()

        # Check if command is available on this platform
        if not config.is_command_available(command_name):
            print(f"Error: Command '{command_name}' is not available on this platform.")
            sys.exit(1)

        handler = get_command_handler(command_name, command_config, runner)
        exit_code = handler.execute()
        sys.exit(exit_code)

    # Set function metadata
    command_func.__name__ = command_name
    description = command_config.get("description", f"Execute {command_name} command")
    command_func.__doc__ = description

    return command_func


def register_commands():
    """Register all commands from configuration."""
    config = DevToolConfig()
    commands = config.get_commands()

    # Register 'd' command first (special handling - always available)
    d_config = commands.get("d", {
        "description": "Docker Compose commands (up, down, re, logs)",
        "command": "docker-compose",
        "platforms": ["windows", "unix"],
    })
    cmd_func = create_command_function("d", d_config)
    app.command(name="d")(cmd_func)

    for command_name, command_config in commands.items():
        # Skip 'd' as it's already registered
        if command_name == "d":
            continue
        # Create and register command
        cmd_func = create_command_function(command_name, command_config)
        app.command(name=command_name)(cmd_func)


# Register commands from config
register_commands()


def main():
    """Main entry point."""
    # Check if a command was provided (not just options)
    args = sys.argv[1:] if len(sys.argv) > 1 else []
    
    # Check if first argument is a command (not starting with -)
    if args and not args[0].startswith("-"):
        # Command provided, execute normally
        app()
    else:
        # No command provided, show custom help (without Options section)
        help()


if __name__ == "__main__":
    main()

