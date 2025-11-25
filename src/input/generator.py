"""Test case generation module."""

from dataclasses import dataclass
from typing import List
from pathlib import Path
import json

from .error_injector import ErrorInjector, calculate_actual_error_rate


@dataclass
class TestCase:
    """Represents a single test case."""
    id: int
    original: str
    corrupted: str
    target_error_rate: float
    actual_error_rate: float
    word_count: int
    num_errors: int


class TestCaseGenerator:
    """Generate test cases with controlled error rates."""

    def __init__(self, base_sentences_file: str, seed: int = 42):
        """
        Initialize generator.

        Args:
            base_sentences_file: Path to file containing base sentences
            seed: Random seed for reproducibility
        """
        self.base_sentences_file = Path(base_sentences_file)
        self.base_sentences = self._load_base_sentences()
        self.error_injector = ErrorInjector(seed=seed)

    def _load_base_sentences(self) -> List[str]:
        """Load base sentences from file."""
        sentences = []
        with open(self.base_sentences_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if line and not line.startswith('#'):
                    # Remove word count annotation if present
                    if '(' in line and 'words)' in line:
                        line = line[:line.rindex('(')].strip()
                    sentences.append(line)
        return sentences

    def generate_test_cases(self, error_rates: List[float]) -> List[TestCase]:
        """
        Generate test cases for all combinations of sentences and error rates.

        Args:
            error_rates: List of target error rates (0.0 to 1.0)

        Returns:
            List of test cases
        """
        test_cases = []
        test_id = 1

        for sentence in self.base_sentences:
            for error_rate in error_rates:
                # Generate corrupted version
                corrupted, num_errors = self.error_injector.inject_errors(
                    sentence, error_rate
                )

                # Calculate actual error rate
                actual_rate = calculate_actual_error_rate(sentence, corrupted)

                # Count words
                word_count = len(sentence.split())

                test_case = TestCase(
                    id=test_id,
                    original=sentence,
                    corrupted=corrupted,
                    target_error_rate=error_rate,
                    actual_error_rate=actual_rate,
                    word_count=word_count,
                    num_errors=num_errors
                )

                test_cases.append(test_case)
                test_id += 1

        return test_cases

    def save_test_cases(self, test_cases: List[TestCase], output_file: str):
        """Save test cases to JSON file."""
        data = [
            {
                "id": tc.id,
                "original": tc.original,
                "corrupted": tc.corrupted,
                "target_error_rate": tc.target_error_rate,
                "actual_error_rate": tc.actual_error_rate,
                "word_count": tc.word_count,
                "num_errors": tc.num_errors
            }
            for tc in test_cases
        ]

        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    @staticmethod
    def load_test_cases(input_file: str) -> List[TestCase]:
        """Load test cases from JSON file."""
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return [
            TestCase(
                id=item["id"],
                original=item["original"],
                corrupted=item["corrupted"],
                target_error_rate=item["target_error_rate"],
                actual_error_rate=item["actual_error_rate"],
                word_count=item["word_count"],
                num_errors=item["num_errors"]
            )
            for item in data
        ]
