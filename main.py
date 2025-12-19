"""Main entry point for MyFinGPT"""

# Load environment variables first, before importing any other modules
from dotenv import load_dotenv
import os
import argparse

try:
    # Best-effort .env loading; don't crash if file is unreadable
    load_dotenv()
except PermissionError as e:
    print(f"[Warning] Could not load .env file due to permission error: {e}. "
          "Continuing without .env; ensure required environment variables are set.")

# Configure logging before importing other modules
from src.utils.logging_config import setup_logging

# Setup logging
log_dir = os.getenv("LOG_DIR", "./logs")
log_level = os.getenv("LOG_LEVEL", "INFO")
logging_config = setup_logging(log_dir=log_dir, log_level=log_level)

from src.ui.gradio_app import main
from src.utils.llm_config import llm_config
from src.utils.integration_config import integration_config


def parse_arguments():
    """
    Parse command-line arguments for LLM provider and integration control
    
    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description="MyFinGPT - Multi-agent financial analysis system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Use LM Studio as LLM provider
  python main.py --llm-provider lmstudio

  # Disable FMP integration
  python main.py --disable-integrations fmp

  # Use OpenAI and disable Alpha Vantage
  python main.py --llm-provider openai --disable-integrations alpha_vantage

  # Enable only Yahoo Finance
  python main.py --enable-integrations yahoo_finance --disable-integrations fmp,alpha_vantage
        """
    )
    
    # LLM provider selection
    available_providers = llm_config.list_available_providers()
    parser.add_argument(
        "--llm-provider",
        type=str,
        choices=available_providers,
        default=None,
        help=f"LLM provider to use. Available: {', '.join(available_providers)}. "
             f"Can also be set via LITELLM_PROVIDER environment variable."
    )
    
    # Integration control
    parser.add_argument(
        "--enable-integrations",
        type=str,
        default=None,
        help="Comma-separated list of integrations to enable (yahoo_finance, alpha_vantage, fmp). "
             "Overrides config file settings."
    )
    
    parser.add_argument(
        "--disable-integrations",
        type=str,
        default=None,
        help="Comma-separated list of integrations to disable (yahoo_finance, alpha_vantage, fmp). "
             "Overrides config file settings."
    )
    
    # Server configuration
    parser.add_argument(
        "--host",
        type=str,
        default=None,
        help="Host to bind the Gradio server to (default: 0.0.0.0)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=None,
        help="Port to bind the Gradio server to (default: 7860)"
    )
    
    parser.add_argument(
        "--share",
        action="store_true",
        help="Create a public Gradio share link"
    )
    
    return parser.parse_args()


def apply_cli_configuration(args):
    """
    Apply CLI arguments to configuration
    
    Args:
        args: Parsed command-line arguments
    """
    # Set LLM provider via environment variable (will be picked up by llm_config)
    if args.llm_provider:
        os.environ["LITELLM_PROVIDER"] = args.llm_provider
        print(f"[Config] LLM Provider set to: {args.llm_provider}")
    
    # Apply integration enable/disable
    if args.enable_integrations:
        integrations_to_enable = [i.strip() for i in args.enable_integrations.split(",")]
        for integration in integrations_to_enable:
            env_var = f"ENABLE_{integration.upper()}"
            os.environ[env_var] = "true"
            print(f"[Config] Enabled integration: {integration}")
    
    if args.disable_integrations:
        integrations_to_disable = [i.strip() for i in args.disable_integrations.split(",")]
        for integration in integrations_to_disable:
            env_var = f"ENABLE_{integration.upper()}"
            os.environ[env_var] = "false"
            print(f"[Config] Disabled integration: {integration}")
    
    # Print current configuration summary
    print("\n[Config] Current Configuration:")
    print(f"  LLM Provider: {os.getenv('LITELLM_PROVIDER', llm_config.default_provider)}")
    print(f"  Enabled Integrations: {', '.join(integration_config.get_enabled_integrations())}")
    disabled = integration_config.get_disabled_integrations()
    if disabled:
        print(f"  Disabled Integrations: {', '.join(disabled)}")
    print()


if __name__ == "__main__":
    # Parse command-line arguments
    args = parse_arguments()
    
    # Apply CLI configuration
    apply_cli_configuration(args)
    
    # Prepare arguments for Gradio app
    # Note: gradio_app.main() has its own argparse, so we set environment variables
    # and let it parse its own arguments, or we can modify sys.argv
    import sys
    
    # Build sys.argv for gradio_app's argparse
    gradio_argv = [sys.argv[0]]  # Script name
    
    if args.llm_provider:
        gradio_argv.extend(["--provider", args.llm_provider])
    if args.host:
        gradio_argv.extend(["--host", args.host])
    if args.port:
        gradio_argv.extend(["--port", str(args.port)])
    if args.share:
        gradio_argv.append("--share")
    
    # Temporarily replace sys.argv for gradio_app's argparse
    original_argv = sys.argv
    sys.argv = gradio_argv
    
    try:
        # Launch Gradio app (it will parse its own arguments)
        main()
    finally:
        # Restore original sys.argv
        sys.argv = original_argv

