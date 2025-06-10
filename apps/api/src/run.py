#!/usr/bin/env python3
"""
Run the FastAPI application.

This script starts the FastAPI application using Uvicorn.
"""

import uvicorn
from pathlib import Path
import os

def main():
    """Run the FastAPI application."""
    # Ensure the data directory exists
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # Set up logging
    log_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "()": "uvicorn.logging.DefaultFormatter",
                "fmt": "%(levelprefix)s %(asctime)s - %(name)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            }
        },
        "handlers": {
            "default": {
                "formatter": "default",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stderr",
            }
        },
        "loggers": {
            "api": {"handlers": ["default"], "level": "INFO"},
            "database": {"handlers": ["default"], "level": "INFO"},
            "uvicorn": {"handlers": ["default"], "level": "INFO"},
            "uvicorn.error": {"level": "ERROR"},
            "uvicorn.access": {
                "handlers": ["default"],
                "level": "INFO",
                "propagate": False,
            },
        },
    }
    
    # Run the application
    uvicorn.run(
        "api.main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("RELOAD", "true").lower() == "true",
        log_config=log_config,
    )

if __name__ == "__main__":
    main()
