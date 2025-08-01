# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TDXLib is a Python SDK for interacting with the TeamDynamix Web API. It provides three main integration classes:

- `TDXTicketIntegration` - For working with tickets, tasks, and ticket-related objects
- `TDXAssetIntegration` - For working with assets, product types, models, and vendors  
- `TDXReportIntegration` - For working with reports

The library uses configuration files (`tdxlib.ini`) or environment variables for authentication and settings.

## Development Commands

### Setup
```bash
# Install dependencies
pip install -r requirements.txt

# For development dependencies
pip install sphinx  # for documentation
pip install gspread oauth2client  # for Google Sheets integration examples
```

### Testing
```bash
# Run all unit tests (from ./testing directory)
python -m unittest discover testing

# Run specific test module
python -m unittest testing.test_tdx_integration
python -m unittest testing.test_tdx_ticket_integration  
python -m unittest testing.test_tdx_asset_integration
```

### Documentation  
```bash
# Build documentation locally
cd docs
make html
```

### Building & Publishing
```bash
# Install build tools
pip install --upgrade build wheel twine

# Build package
python -m build

# Upload to PyPI (maintainers only)
twine upload dist/*
```

## Architecture

### Core Structure
- `tdxlib/tdx_integration.py` - Base integration class with authentication and universal TDX objects
- `tdxlib/tdx_ticket_integration.py` - Ticket-specific functionality
- `tdxlib/tdx_asset_integration.py` - Asset-specific functionality  
- `tdxlib/tdx_report_integration.py` - Report-specific functionality
- `tdxlib/tdx_config.py` - Configuration management
- `tdxlib/tdx_constants.py` - Constants and default configuration
- `tdxlib/tdx_utils.py` - Utility functions
- `tdxlib/tdx_api_exceptions.py` - Custom exception classes

### Key Design Patterns
- Configuration can be provided via INI files, Python dictionaries, or environment variables
- Caching is used extensively to reduce API calls for repetitive operations
- All datetime objects are handled with timezone awareness
- Authentication uses JWT tokens with automatic refresh

### Testing Configuration
Tests require a `testing_vars.json` file (ignored by git) based on the sample files in `testing/`. Tests include sandbox protection to prevent accidental production modifications.

## Version Management
Version is maintained in both `tdxlib/__init__.py` and `setup.py` and must be updated for releases.