"""
Utility functions for the netbox_oxidized_config_viewer plugin.
"""
import difflib

def generate_unified_diff(text1, text2, from_filename="config_a", to_filename="config_b"):
    """
    Generate a unified diff string between two text inputs.

    Args:
        text1 (str): The first text input
        text2 (str): The second text input
        from_filename (str): The name of the first file
        to_filename (str): The name of the second file

    Returns:
        str: A unified diff string
    """
    diff = difflib.unified_diff(
        text1.splitlines(),
        text2.splitlines(),
        fromfile=from_filename,
        tofile=to_filename,
        lineterm="",
    )
    return "\n".join(diff)