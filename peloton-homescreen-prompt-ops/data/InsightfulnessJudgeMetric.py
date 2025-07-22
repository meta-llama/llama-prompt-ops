import json
import re
import time
from typing import Any, Dict, Optional, Union

from llama_prompt_ops.core.metrics import MetricBase
try:
    import dspy

    DSPY_AVAILABLE = True
except ImportError:
    DSPY_AVAILABLE = False

# Define DSPy signature for insightfulness evaluation
class InsightfulnessJudgeSignature(dspy.Signature):
    """
    Signature for evaluating the insightfulness of fitness insights.

    Evaluates how insightful the explanations are based on the user's goal and workout history.
    Scored from 0-10, where 0 is not insightful and 10 is highly insightful.
    """
    # Input fields
    user_goal = dspy.InputField(desc="The user's fitness goal")
    workout_history = dspy.InputField(desc="The user's workout history")
    o4_mini_response = dspy.InputField(desc='''
        You will be given the o4-mini response with the given JSON format:
            {
            "class_types": ["<value 1>", "<value 2>", ...] # comma-separated list of values from the CLASS_TYPES enum.
            "durations": ["<value 1>", "<value 2>", ...] # comma-separated list of durations from the DURATIONS enum
            "explanation": "<short, deep, personalized explanation>"
            }
        ''')
    model_response = dspy.InputField(desc='''
        You will be given the model response with the given JSON format:
            {
            "class_types": ["<value 1>", "<value 2>", ...] # comma-separated list of values from the CLASS_TYPES enum.
            "durations": ["<value 1>", "<value 2>", ...] # comma-separated list of durations from the DURATIONS enum
            "explanation": "<short, deep, personalized explanation>"
            }
        ''')

    # Output fields
    insightfulness_scores = dspy.OutputField(
        desc= '''
        Determine if the model response insight is more or less insightful than the o4-mini response insight. Consider the following criteria:
            - Does the explanation have specific references to the user's activities (e.g., "Tuesday's 30-min climb ride") or notable patterns (e.g., "3 straight short HIIT sessions")?
            - Does it provide a concise rationale explaining why today's recommendation supports overload, recovery balance, or skill variety for their goal?
            - Is the explanation deep and nuanced rather than surface level?
            - Does it demonstrate expert knowledge of fitness principles and how they apply to this specific user?
            - Does it make connections between the user's history, goals, and the recommended workout that aren't immediately obvious?
        Rate both insights on a scale of 1-10 with the following criteria:
            - 1-2: Generic observations with no specific references to user's activities
            - 3-4: Basic references to user's activities but shallow analysis
            - 5-6: Clear references to specific workouts with basic rationale
            - 7-8: Detailed analysis of patterns with solid rationale for recommendations
            - 9-10: Exceptional insights that reveal non-obvious connections between history, goals, and recommendations
        Return the score for the model response insight and the o4-mini response insight in the following JSON format:
            {
                "model_response_insight_score": <score>,
                "model_response_insight_reasoning": "<brief rationale of your evaluation>",
                "o4_mini_response_insight_score": <score>,
                "o4_mini_response_insight_reasoning": "<brief rationale of your evaluation>"
            }
        '''
    )

class InsightfulnessJudgeMetric(MetricBase):
    """
        Metric for evalutating the insightfulness of a model response fitenss insight compared to an o4-mini response insight.
        The metric returns a ratio between the model response insightfulness score and the o4-mini response insightfulness score.
    """

    def __init__(
        self,
        judge_model: str = "openrouter/openai/o3",
        judge_api_key: str = "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",
        temperature: float = 1.0,
        max_tokens: int = 5000,
        max_retries: int = 1,
        **kwargs,
    ):
        """
        Initialize the metric

        Args:
            judge_model: Model to use for LLM judging
            judge_api_key: API key for LLM judging
            temperature: Temperature for LLM generation (lower = more consistent)
            max_tokens: Maximum number of tokens for LLM generation
            max_retries: Maximum number of retry attempts for failed API calls
        """

        if not DSPY_AVAILABLE:
            raise ImportError("DSPy is required for LLM-based metrics. Install with: pip install dspy")

        self.judge_model = judge_model
        self.temperature = temperature
        self.max_retries = max_retries

        # Initialize DSPy model for judging
        self.model = dspy.LM(
            model=judge_model,
            api_key=judge_api_key,
            temperature=temperature,
            max_tokens=max_tokens  # Simple metric needs fewer tokens
        )

        # Create judge predictor
        self.judge_predictor = dspy.Predict(InsightfulnessJudgeSignature)

        print(f"Initialized InsightfulnessJudgeMetric with model: {judge_model}")

    def __call__(self, gold: Any, pred: Any, trace: bool = False, **kwargs) -> Union[Dict[str, float], float]:
        """
        Evaluate the insightfulness of a model response fitenss insight compared to an o4-mini response insight.

        Args:
            gold: Ground truth example (dict or string)
            pred: Model prediction (dict or string)
            trace: Whether to enable tracing for debugging
            **kwargs: Additional arguments

        Returns:
            Either a dictionary containing metric scores (if trace=True) or a single float score
        """

        scores = self._get_insightfulness_scores_with_retry(gold, pred)
        if isinstance(scores, dict):
            scores = scores['answer'] if 'answer' in scores else scores
            ratio_score = scores["model_response_insight_score"] / scores["o4_mini_response_insight_score"]
            ratio_score = min(ratio_score, 1.0)
            if trace:
                scores["ratio_score"] = ratio_score
                return scores
            else:
                return ratio_score
        else:
            if trace:
                print(f"Failed to parse insightfulness score from: {scores}")
            return scores



    def _get_insightfulness_scores_with_retry(self, ground_truth: Any, prediction: Any) -> Union[Dict[str, float], float]:
        """Get similarity score with retry logic for robustness."""
        # Define expected keys for different objects
        response_keys = ['answer', 'class_types', 'durations', 'explanation']
        score_keys = ['answer', 'model_response_insight_score', 'model_response_insight_reasoning',
                     'o4_mini_response_insight_score', 'o4_mini_response_insight_reasoning']

        for attempt in range(self.max_retries):
            try:
                print(f"o4-mini response: {ground_truth.answer} with type: {type(ground_truth.answer)}")
                o4_extracted_json = self._handle_json(ground_truth.answer, expected_keys=response_keys)
                print(f"o4_extracted_json: {o4_extracted_json} with type: {type(o4_extracted_json)}")
                if not o4_extracted_json:
                    print("Failed to extract JSON from o4-mini response")
                    return 5.0  # Default to middle score

                print(f"model response: {prediction.answer} with type: {type(prediction.answer)}")
                model_extracted_json = self._handle_json(prediction.answer, expected_keys=response_keys)
                print(f"model_extracted_json: {model_extracted_json} with type: {type(model_extracted_json)}")
                if not model_extracted_json:
                    print("Failed to extract JSON from model response")
                    return 5.0  # Default to middle score

                with dspy.context(lm=self.model):
                    result = self.judge_predictor(
                        user_goal=ground_truth.goal,
                        workout_history=ground_truth.history_text,
                        o4_mini_response=o4_extracted_json,
                        model_response=model_extracted_json,
                    )
                print(f"result of self.judge_predictor: {result}")

                # Use expected_keys parameter to ensure all required keys are present
                # and wrap in 'answer' key if needed
                scores = self._handle_json(result.insightfulness_scores, score_keys)
                print(f"scores: {scores}")

                if not scores:
                    print(f"Failed to parse insightfulness score from: {result.insightfulness_scores}")
                    return 5.0  # Return properly formatted default

                # If scores is a dict but doesn't have the expected structure, wrap it in an answer key
                if isinstance(scores, dict):
                    return scores
                else:
                    print("Parsed scores are not in the expected format. Defaulting to middle score.")
                    return 5.0  # Return properly formatted default
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    print(f"All {self.max_retries} attempts failed")
                    return 5.0  # Default to middle score on complete failure

        return 5.0  # Ensure a return value on all code paths


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

    def _handle_json(self, json_obj: Any, expected_keys: list = None) -> Union[dict, list]:
        """
        Handle JSON objects of any type, ensuring they have the expected keys.

        Args:
            json_obj: Any object that needs to be converted to a dict/list
            expected_keys: List of keys that should be present in the resulting dict

        Returns:
            A dictionary or list with all expected keys
        """
        result = {}

        # Handle different input types
        if isinstance(json_obj, str):
            try:
                extracted_pred = self._extract_json_block(json_obj)
                if extracted_pred:
                    result = extracted_pred
                else:
                    print(f"Failed to extract JSON from pred: {json_obj[:100]}...")
            except Exception as e:
                print(f"Error extracting JSON: {e}")
        elif isinstance(json_obj, dict):
            result = json_obj
        elif isinstance(json_obj, list):
            return json_obj  # Lists are returned as-is
        elif hasattr(json_obj, "__dict__"):
            # Handle objects with __dict__ attribute
            result = json_obj.__dict__
        elif hasattr(json_obj, "to_dict"):
            # Handle objects with to_dict method
            result = json_obj.to_dict()

        ret_dict = {}
        # Ensure the result has all expected keys if provided
        result = result['answer'] if 'answer' in result else result
        for key in expected_keys:
            if str.lower(key) == 'answer':
                continue
            if key not in result:
                ret_dict[key] = None  # Add missing keys with None value
            else:
                ret_dict[key] = result[key]

        if 'answer' in expected_keys:
            return {'answer': ret_dict}

        return ret_dict
