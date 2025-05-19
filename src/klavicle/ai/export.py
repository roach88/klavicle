"""Export and import utilities for AI analysis."""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from rich.console import Console

# Constants
DEFAULT_EXPORT_DIR = "exports"


def export_data_for_ai_analysis(
    data_type: str, 
    data: Any, 
    export_dir: Optional[str] = None,
    file_name: Optional[str] = None
) -> str:
    """
    Export data for offline AI analysis.
    
    Args:
        data_type: Type of data ("campaigns", "flows", "lists", etc.)
        data: Data to export (usually a list of objects)
        export_dir: Directory to export to (defaults to ./exports)
        file_name: Custom file name (defaults to data_type_timestamp.json)
        
    Returns:
        Path to the exported file
    """
    # Setup export directory
    export_path = Path(export_dir or DEFAULT_EXPORT_DIR)
    os.makedirs(export_path, exist_ok=True)
    
    # Create file name if not provided
    if not file_name:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"{data_type}_data_{timestamp}.json"
    
    # Ensure file has .json extension
    if not file_name.endswith(".json"):
        file_name += ".json"
        
    # Full path to export file
    file_path = export_path / file_name
    
    # Export data
    export_data = {
        "data_type": data_type,
        "timestamp": datetime.now().isoformat(),
        "data": data
    }
    
    with open(file_path, "w") as f:
        json.dump(export_data, f, indent=2)
        
    return str(file_path)


def import_data_for_ai_analysis(file_path: str) -> Dict[str, Any]:
    """
    Import data for AI analysis from a file.
    
    Args:
        file_path: Path to the data file
        
    Returns:
        Dictionary with data_type and data fields
    """
    with open(file_path, "r") as f:
        data = json.load(f)
        
    # Validate that it's a proper export
    if not all(key in data for key in ["data_type", "data"]):
        raise ValueError(
            "Invalid data format. File must contain 'data_type' and 'data' fields."
        )
        
    return data


def export_ai_analysis_results(
    results: Dict[str, Any],
    data_type: str,
    export_dir: Optional[str] = None,
    file_name: Optional[str] = None
) -> str:
    """
    Export AI analysis results to a file.
    
    Args:
        results: AI analysis results
        data_type: Type of data that was analyzed
        export_dir: Directory to export to (defaults to ./exports)
        file_name: Custom file name (defaults to data_type_analysis_timestamp.json)
        
    Returns:
        Path to the exported file
    """
    # Setup export directory
    export_path = Path(export_dir or DEFAULT_EXPORT_DIR)
    os.makedirs(export_path, exist_ok=True)
    
    # Create file name if not provided
    if not file_name:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"{data_type}_analysis_{timestamp}.json"
    
    # Ensure file has .json extension
    if not file_name.endswith(".json"):
        file_name += ".json"
        
    # Full path to export file
    file_path = export_path / file_name
    
    # Export data
    export_data = {
        "data_type": data_type,
        "timestamp": datetime.now().isoformat(),
        "analysis": results
    }
    
    with open(file_path, "w") as f:
        json.dump(export_data, f, indent=2)
        
    return str(file_path)


def import_ai_analysis_results(file_path: str) -> Dict[str, Any]:
    """
    Import AI analysis results from a file.
    
    Args:
        file_path: Path to the results file
        
    Returns:
        Dictionary with data_type and analysis fields
    """
    with open(file_path, "r") as f:
        data = json.load(f)
        
    # Validate that it's a proper export
    if not all(key in data for key in ["data_type", "analysis"]):
        raise ValueError(
            "Invalid data format. File must contain 'data_type' and 'analysis' fields."
        )
        
    return data