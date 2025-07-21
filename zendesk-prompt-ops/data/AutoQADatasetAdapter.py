import json
from typing import Any, Dict, List

from llama_prompt_ops.core.datasets import DatasetAdapter


class AutoQADatasetAdapter(DatasetAdapter):
    """Adapter for zendesk auto qa results"""

    def __init__(self, dataset_path: str, **kwargs):
        """
        Initialize the AutoQADatasetAdapter.

        Args:
            dataset_path: Path to the dataset file
            **kwargs: Additional arguments passed to the parent class
        """
        super().__init__(dataset_path, 'json')

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
                expected = item.get("expected", {})

                # Create answer dictionary with safe gets for all fields
                answer = {
                    "Greeting": expected.get("Greeting", ""),
                    "Closing": expected.get("Closing"),
                    "Comprehension": expected.get("Comprehension"),
                    "Empathy": expected.get("Empathy"),
                    "Solution": expected.get("Solution"),
                    "Tone": expected.get("Tone"),
                }

                example = {
                    "inputs": {"question": item.get("input", {"dialog": ""}).get("dialog", "")},
                    "outputs": {"answer": answer},
                }
                standardized_data.append(example)
            except Exception as e:
                print(f"Error processing item: {e}")
                continue

        return standardized_data
