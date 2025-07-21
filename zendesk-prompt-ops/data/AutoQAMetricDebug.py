import json
import re
import sys
from typing import Any, Dict, Optional, Union
import pprint

from llama_prompt_ops.core.metrics import MetricBase


class AutoQAMetric(MetricBase):
    """Zendesk AutoQA metric that evaluates customer service responses across multiple dimensions."""
    def __init__(self, weights: Optional[Dict[str, float]] = None, **kwargs):
        """
        Initialize the AutoQA metric.

        Args:
            weights: Optional dictionary of weights for each metric dimension
            **kwargs: Additional arguments passed to the parent class
        """
        # Initialize the parent class
        super().__init__()

        self.weights = weights or {
            "Greeting": 0.1,
            "Closing": 0.1,
            "Comprehension": 0.2,
            "Empathy": 0.1,
            "Grammar": 0.1,
            "Readability": 0.1,
            "Solution": 0.2,
            "Tone": 0.1,
        }

        # Define mapping between gold data keys and prediction data keys
        self.key_mapping = {
            "Greeting": "greeting",
            "Closing": "closing",
            "Comprehension": "issue_understanding",
            "Empathy": "empathy",
            "Grammar": "grammar",
            "Readability": "readability",
            "Solution": "solution_offered",
            "Tone": "tone"
        }

        # Tone scoring dictionary from postprocess_results.py
        self.TONE_SCORE_CATEGORY_DICT = {
            "joyful": (2.9, "pos-cheerful"),
            "fun": (2.3, "pos-cheerful"),
            "excited": (1.4, "pos-cheerful"),
            "friendly": (2.2, "pos-cheerful"),
            "encouraging": (2.4, "pos-supportive"),
            "supportive": (1.2, "pos-supportive"),
            "empathetic": (1.7, "pos-supportive"),
            "appreciative": (2.6, "pos-supportive"),
            "optimistic": (1.3, "pos-supportive"),
            "reassuring": (1.7, "pos-supportive"),
            "accessible": (1.1, "pos-supportive"),
            "professional": (1.5, "pos-professional"),
            "diplomatic": (1, "pos-professional"),
            "confident": (2.2, "pos-professional"),
            "polite": (1, "pos-professional"),
            "formal": (0.8, "pos-professional"),
            "calm": (1.5, "pos-calm"),
            "patient": (2, "pos-calm"),
            "apologetic": (-0.1, "neutral-sorry"),
            "regretful": (-0.1, "neutral-sorry"),
            "concerned": (0, "neutral-sorry"),
            "angry": (-3.9, "negative"),
            "sad": (-2.1, "negative"),
            "frustrated": (-3.9, "negative"),
            "accusatory": (-5, "negative"),
            "worried": (0, "neutral-sorry"),
            "curious": (1.3, "pos-inquisitive"),
            "surprised": (0.9, "pos-inquisitive"),
            "helpful": (1.8, "pos-supportive"),
            "informal": (0.8, "pos-cheerful"),
            "informative": (1.5, "pos-supportive"),
        }

    def _extract_json_block(self, text: str) -> Optional[Union[dict, list]]:
        """
        Return the first JSON object/array in `text`, or None if not parsable.
        Very tolerant: strips ``` fences and grabs the first {...} or [...] block.
        Also handles raw JSON without code fences.
        """
        if not text:
            return None
        text = text.strip()

        # First try to find JSON within ```json fences
        json_block_match = re.search(r"```(?:json)?\s*(.*?)```", text, flags=re.I | re.S)
        if json_block_match:
            # Extract the content within the code fences
            extracted_text = json_block_match.group(1).strip()
        else:
            # If no code fences found, use the entire text
            extracted_text = text

        # Find the first JSON object or array in the extracted text
        start = min(
            (pos for pos in [extracted_text.find("{"), extracted_text.find("[")] if pos != -1), default=-1
        )
        end = max(extracted_text.rfind("}"), extracted_text.rfind("]"))

        if start == -1 or end == -1:
            return None

        json_text = extracted_text[start : end + 1]

        # Remove trailing commas before closing braces/brackets to fix invalid JSON
        json_text = re.sub(r",(\s*[}\]])", r"\1", json_text)

        try:
            parsed_json = json.loads(json_text)
            # Handle nested structure where data is under "properties" key
            if isinstance(parsed_json, dict) and "properties" in parsed_json:
                return parsed_json["properties"]
            return parsed_json
        except json.JSONDecodeError:
            # Try to find another JSON block if the first attempt failed
            try:
                # Look for any valid JSON-like structure in the text
                potential_json_match = re.search(r'(\{.*\}|\[.*\])', extracted_text, re.DOTALL)
                if potential_json_match:
                    json_text = potential_json_match.group(1)
                    # Remove trailing commas before closing braces/brackets
                    json_text = re.sub(r",(\s*[}\]])", r"\1", json_text)
                    parsed_json = json.loads(json_text)
                    if isinstance(parsed_json, dict) and "properties" in parsed_json:
                        return parsed_json["properties"]
                    return parsed_json
            except (json.JSONDecodeError, AttributeError):
                pass
            return None

    def _compare_metric(self, gold: Any, pred: Any, gold_key: str, pred_key: str, model_transform) -> int:
        model_val = pred[pred_key]
        expected_val = gold[gold_key]

        try:
            transformed_model_val = model_transform(model_val)
        except Exception:
            print("Error transforming model value: ", model_val)
            return 0

        if (
            transformed_model_val is not None
            and expected_val is not None
            and transformed_model_val == expected_val
        ):
            return 1
        else:
            return 0


    def __call__(self, gold: Dict, pred: Any, trace: bool = False, **kwargs):
        """
        Evaluate the prediction against the ground truth.

        Args:
            gold: Ground truth data
            pred: Prediction data (can be a string or parsed JSON)
            trace: If True, return detailed scores for each metric
            **kwargs: Additional arguments (unused)

        Returns:
            If trace is True, returns a dictionary with scores for each metric.
            Otherwise, returns the total weighted score.
        """
        print("\n" + "="*80)
        print("DEBUG: AutoQAMetric.__call__ called")
        print(f"DEBUG: gold type: {type(gold)}")
        pred = pred.answer
        print(f"DEBUG: pred type: {type(pred)}")
        print(f"DEBUG: pred: {pred}")

        # Parse prediction if it's a string
        if isinstance(pred, str):
            print(f"DEBUG: pred is a string, length: {len(pred)}")
            print(f"DEBUG: First 200 chars of pred: {pred[:200]}")
            try:
                extracted_pred = self._extract_json_block(pred)
                if extracted_pred:
                    print(f"DEBUG: Successfully extracted JSON from pred")
                    print(f"DEBUG: Extracted pred keys: {list(extracted_pred.keys()) if isinstance(extracted_pred, dict) else 'Not a dict'}")
                    pred = extracted_pred
                else:
                    print(f"DEBUG: Failed to extract JSON from pred")
                    print(f"DEBUG: Full pred content: {pred}")
                    return 0.0
            except json.JSONDecodeError as e:
                print(f"DEBUG: JSON decode error: {e}")
                return 0.0
            except Exception as e:
                print(f"DEBUG: Unexpected error in JSON extraction: {e}")
                return 0.0

        # Extract gold data
        gold_data = gold.get("answer", gold)
        print(f"DEBUG: gold_data keys: {list(gold_data.keys()) if isinstance(gold_data, dict) else 'Not a dict'}")

        if isinstance(pred, dict):
            print(f"DEBUG: pred keys: {list(pred.keys())}")
        else:
            print(f"DEBUG: pred is not a dict, it's a {type(pred)}")
            return 0.0

        # Initialize scores dictionary
        scores = {}

        # Calculate individual scores for each metric using the key mapping
        print("\nDEBUG: Calculating scores for each metric:")
        for gold_key, pred_key in self.key_mapping.items():
            print(f"\nDEBUG: Processing {gold_key} -> {pred_key}")

            # Skip if the gold data doesn't have this key
            if gold_key not in gold_data:
                print(f"DEBUG: {gold_key} not in gold_data, skipping")
                continue

            # For Tone, use the special tone mapping function
            if gold_key == "Tone":
                transform_func = self._map_tone_to_manual
                print(f"DEBUG: Using tone mapping function")
            else:
                transform_func = self._map_results_to_manual
                print(f"DEBUG: Using standard mapping function")

            # Calculate the score for this metric
            try:
                if pred_key in pred:
                    print(f"DEBUG: {pred_key} found in pred")
                    print(f"DEBUG: gold_data[{gold_key}] = {gold_data[gold_key]}")
                    print(f"DEBUG: pred[{pred_key}] = {pred[pred_key]}")

                    score = self._compare_metric(
                        gold_data, pred, gold_key, pred_key, transform_func
                    )
                    print(f"DEBUG: Score for {gold_key}: {score}")
                    scores[gold_key.lower() + "_score"] = score
                else:
                    print(f"DEBUG: {pred_key} NOT found in pred")
                    scores[gold_key.lower() + "_score"] = 0
            except (KeyError, TypeError) as e:
                print(f"DEBUG: Error calculating score for {gold_key}: {e}")
                scores[gold_key.lower() + "_score"] = 0

        # Calculate weighted score
        total_score = 0.0
        print("\nDEBUG: Calculating weighted score:")
        for gold_key in self.weights:
            score_key = gold_key.lower() + "_score"
            if score_key in scores:
                weighted_score = scores[score_key] * self.weights[gold_key]
                print(f"DEBUG: {gold_key}: {scores[score_key]} * {self.weights[gold_key]} = {weighted_score}")
                total_score += weighted_score
            else:
                print(f"DEBUG: {score_key} not in scores")

        # Add total score to the scores dictionary
        scores["total_score"] = total_score
        print(f"\nDEBUG: Final scores: {scores}")
        print("="*80 + "\n")

        if trace:
            return scores

        return total_score

    def _map_results_to_manual(self, result) -> Optional[float]:
        """Map yes/no results to 1.0/0.0."""
        print(f"DEBUG: _map_results_to_manual called with result: {result} (type: {type(result)})")

        if isinstance(result, dict) and "Agent1" in result:
            print(f"DEBUG: Found Agent1 in result dict, extracting value: {result['Agent1']}")
            result = result["Agent1"]

        if result == "yes":
            print("DEBUG: Mapped 'yes' to 1.0")
            return 1.0
        if result == "no":
            print("DEBUG: Mapped 'no' to 0.0")
            return 0.0

        print(f"DEBUG: Could not map result '{result}', returning None")
        return None

    def _tone_score(self, tone_list: list, start_bias: float = 0.0) -> Optional[float]:
        """
        Scores tone based on tone_list.
        If no valid tones are present, returns None.
        """
        print(f"DEBUG: _tone_score called with tone_list: {tone_list}")

        if not tone_list:
            print("DEBUG: Empty tone list, returning None")
            return None

        score = start_bias
        zero_valid_tones = True

        for tone in tone_list:
            tone_lowercase = tone.strip().lower()
            tone_score = self.TONE_SCORE_CATEGORY_DICT.get(tone_lowercase, None)
            if tone_score:
                print(f"DEBUG: Found tone '{tone_lowercase}' with score {tone_score[0]}")
                score += tone_score[0]
                zero_valid_tones = False
            else:
                print(f"DEBUG: Tone '{tone_lowercase}' not found in dictionary")

        if zero_valid_tones:
            print("DEBUG: No valid tones found, returning None")
            return None
        else:
            final_score = None
            if score < -1.5:
                final_score = 0.0
            elif score < -0.5:
                final_score = 1.0
            elif score < 0.5:
                final_score = 2.0
            elif score < 1.5:
                final_score = 3.0
            else:
                final_score = 4.0

            print(f"DEBUG: Final tone score: {final_score} (raw score: {score})")
            return final_score

    def _map_tone_to_manual(self, result) -> Optional[float]:
        """Map tone results to manual scoring."""
        print(f"DEBUG: _map_tone_to_manual called with result: {result} (type: {type(result)})")

        if isinstance(result, dict) and "Agent1" in result:
            print(f"DEBUG: Found Agent1 in result dict, extracting value: {result['Agent1']}")
            tone_list = result["Agent1"]
        elif isinstance(result, list):
            print(f"DEBUG: Result is already a list of length {len(result)}")
            tone_list = result
        else:
            print(f"DEBUG: Result is not a dict with Agent1 or a list, returning None")
            return None

        return self._tone_score(tone_list)
