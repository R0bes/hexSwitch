"""Main application entry point for HexSwitch."""

import argparse
import logging
import sys

from hexswitch import __version__

logger = logging.getLogger(__name__)


def main() -> int:
    """Main entry point for HexSwitch CLI.

    Returns:
        Exit code (0 for success, non-zero for errors).
    """
    parser = argparse.ArgumentParser(
        description="HexSwitch - Hexagonal runtime switchboard for config-driven microservices"
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"HexSwitch {__version__}",
    )
    parser.add_argument(
        "--config",
        type=str,
        help="Path to configuration file (not implemented yet)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )

    args = parser.parse_args()

    # Set up logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Print version and description
    logger.info(f"HexSwitch {__version__}")
    logger.info("Hexagonal runtime switchboard for config-driven microservices")

    # Handle config parameter (not implemented yet)
    if args.config:
        logger.warning(f"Config file specified: {args.config}")
        logger.warning("Configuration loading is not implemented yet.")

    logger.info("HexSwitch runtime is not implemented yet. This is a placeholder.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

