import json
from typing import Any, Dict, List

from llama_prompt_ops.core.datasets import DatasetAdapter


class PelotonHomescreenDatasetAdapter(DatasetAdapter):
    """Adapter for Peloton Homescreen dataset"""

    def __init__(self, dataset_path: str, **kwargs):
        """
        Initialize the AutoQADatasetAdapter.

        Args:
            dataset_path: Path to the dataset file
            **kwargs: Additional arguments passed to the parent class
        """
        super().__init__(dataset_path, 'json')

    """
    Transform dataset-specific format into standardized format.

    The standardized format is a list of dictionaries, where each dictionary
    represents a single example and has the following structure:
    {
        "inputs": {
            "field1": value1,
            "field2": value2,
            ...
        },
        "outputs": {
            "field1": value1,
            "field2": value2,
            ...
        },
        "metadata": {  # Optional
            "field1": value1,
            "field2": value2,
            ...
        }
    }

    Returns:
        List of standardized examples
    """
    def adapt(self) -> List[Dict[str, Any]]:
        """Transform customer service data into standardized format."""
        try:
            with open(self.dataset_path, "r") as f:
                data = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Error loading dataset: {e}")
            return []

        standardized_data = []
        for item in data:
            try:
                # Get expected values with safe defaults
                expected = item.get("expected", "")
                # Parse the expected JSON string and handle errors
                try:
                    if expected:
                        expected = json.loads(expected)
                    else:
                        expected = {}
                except json.JSONDecodeError as e:
                    print(f"Error parsing expected JSON: {e}")
                    expected = {}

                # Create answer dictionary with safe gets for all fields
                answer = {
                    "class_types": expected.get("class_types", []),
                    "durations": expected.get("durations", []),
                    "explanation": expected.get("explanation", ""),
                }

                example = {
                    "inputs": {
                        "goal": item.get("goal", ""),
                        "history_text": item.get("history_text", ""),
                        "formatted_time": "07/18/2025 03:02 PM",
                        "question": f"example_id: {item.get('example_id', '')}"},
                    "outputs": {"answer": answer},
                }

                standardized_data.append(example)
            except Exception as e:
                print(f"Error processing item: {e}")
                continue

        return standardized_data
