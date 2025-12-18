"""Logging configuration for MyFinGPT"""

import os
import sys
from pathlib import Path
from loguru import logger
from datetime import datetime


def setup_logging(log_dir: str = "./logs", log_level: str = None):
    """
    Configure loguru logger with file and console handlers
    
    Args:
        log_dir: Directory to store log files (default: ./logs)
        log_level: Log level (DEBUG, INFO, WARNING, ERROR). If None, reads from LOG_LEVEL env var or defaults to INFO
    """
    # Remove default handler
    logger.remove()
    
    # Determine log level
    if log_level is None:
        log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    
    # Create logs directory if it doesn't exist
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)
    
    # Log file names with date
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    # Main log file (all logs)
    main_log_file = log_path / f"myfingpt_{date_str}.log"
    
    # Error log file (errors only)
    error_log_file = log_path / f"myfingpt_errors_{date_str}.log"
    
    # Component-specific log files
    component_logs = {
        "workflow": log_path / f"workflow_{date_str}.log",
        "agents": log_path / f"agents_{date_str}.log",
        "mcp": log_path / f"mcp_{date_str}.log",
        "vectordb": log_path / f"vectordb_{date_str}.log",
        "ui": log_path / f"ui_{date_str}.log",
    }
    
    # Format strings
    detailed_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )
    
    simple_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<level>{message}</level>"
    )
    
    # Console handler (colorized, simple format)
    logger.add(
        sys.stderr,
        format=simple_format,
        level=log_level,
        colorize=True,
        backtrace=True,
        diagnose=True
    )
    
    # Main log file (all logs, detailed format)
    logger.add(
        str(main_log_file),
        format=detailed_format,
        level=log_level,
        rotation="100 MB",  # Rotate when file reaches 100MB
        retention="30 days",  # Keep logs for 30 days
        compression="zip",  # Compress old logs
        backtrace=True,
        diagnose=True,
        encoding="utf-8"
    )
    
    # Error log file (errors and warnings only)
    logger.add(
        str(error_log_file),
        format=detailed_format,
        level="WARNING",  # Only warnings and errors
        rotation="50 MB",
        retention="90 days",  # Keep error logs longer
        compression="zip",
        backtrace=True,
        diagnose=True,
        encoding="utf-8"
    )
    
    # Component-specific log files with filtering
    # Workflow logs
    logger.add(
        str(component_logs["workflow"]),
        format=detailed_format,
        level=log_level,
        filter=lambda record: "[WORKFLOW]" in record["message"] or "[GRAPH]" in record["message"],
        rotation="50 MB",
        retention="30 days",
        compression="zip",
        encoding="utf-8"
    )
    
    # Agent logs
    logger.add(
        str(component_logs["agents"]),
        format=detailed_format,
        level=log_level,
        filter=lambda record: any(
            agent in record["message"] 
            for agent in ["Research Agent", "Analyst Agent", "Reporting Agent", "Base Agent"]
        ),
        rotation="50 MB",
        retention="30 days",
        compression="zip",
        encoding="utf-8"
    )
    
    # MCP client logs
    logger.add(
        str(component_logs["mcp"]),
        format=detailed_format,
        level=log_level,
        filter=lambda record: "[MCP:" in record["message"],
        rotation="50 MB",
        retention="30 days",
        compression="zip",
        encoding="utf-8"
    )
    
    # Vector DB logs
    logger.add(
        str(component_logs["vectordb"]),
        format=detailed_format,
        level=log_level,
        filter=lambda record: "[VectorDB]" in record["message"],
        rotation="50 MB",
        retention="30 days",
        compression="zip",
        encoding="utf-8"
    )
    
    # UI logs
    logger.add(
        str(component_logs["ui"]),
        format=detailed_format,
        level=log_level,
        filter=lambda record: "[UI]" in record["message"],
        rotation="50 MB",
        retention="30 days",
        compression="zip",
        encoding="utf-8"
    )
    
    logger.info(f"Logging configured | Level: {log_level} | Log directory: {log_path.absolute()}")
    logger.info(f"Log files: main={main_log_file.name}, errors={error_log_file.name}")
    logger.info(f"Component logs: {', '.join(f.name for f in component_logs.values())}")
    
    return {
        "log_dir": str(log_path.absolute()),
        "main_log": str(main_log_file.absolute()),
        "error_log": str(error_log_file.absolute()),
        "component_logs": {k: str(v.absolute()) for k, v in component_logs.items()}
    }

