"""Error injection module for introducing controlled spelling errors."""

import random
from typing import List, Tuple


class ErrorInjector:
    """Inject spelling errors into text at controlled rates."""

    def __init__(self, seed: int = 42):
        """
        Initialize the error injector.

        Args:
            seed: Random seed for reproducible error injection
        """
        self.seed = seed
        random.seed(seed)

    def inject_errors(self, text: str, error_rate: float) -> Tuple[str, int]:
        """
        Inject spelling errors into text at the specified rate.

        Args:
            text: Original text
            error_rate: Fraction of words to corrupt (0.0 to 1.0)

        Returns:
            Tuple of (corrupted_text, num_errors_injected)
        """
        words = text.split()
        total_words = len(words)
        num_errors = max(1, int(total_words * error_rate))

        # Randomly select words to corrupt
        if num_errors >= total_words:
            error_indices = list(range(total_words))
        else:
            error_indices = random.sample(range(total_words), num_errors)

        # Apply errors
        for idx in error_indices:
            words[idx] = self._corrupt_word(words[idx])

        return " ".join(words), len(error_indices)

    def _corrupt_word(self, word: str) -> str:
        """
        Apply a random error to a single word.

        Args:
            word: Original word

        Returns:
            Corrupted word
        """
        # Don't corrupt very short words or punctuation
        if len(word) < 3:
            return word

        # Remove punctuation for corruption
        has_punct = False
        punct = ""
        if word[-1] in ".,!?;:":
            has_punct = True
            punct = word[-1]
            word = word[:-1]

        if len(word) < 3:
            return word + punct if has_punct else word

        error_type = random.choice([
            "character_swap",
            "character_deletion",
            "character_insertion",
            "character_replacement"
        ])

        if error_type == "character_swap":
            corrupted = self._swap_characters(word)
        elif error_type == "character_deletion":
            corrupted = self._delete_character(word)
        elif error_type == "character_insertion":
            corrupted = self._insert_character(word)
        else:  # character_replacement
            corrupted = self._replace_character(word)

        return corrupted + punct if has_punct else corrupted

    def _swap_characters(self, word: str) -> str:
        """Swap two adjacent characters."""
        if len(word) < 2:
            return word
        pos = random.randint(0, len(word) - 2)
        word_list = list(word)
        word_list[pos], word_list[pos + 1] = word_list[pos + 1], word_list[pos]
        return "".join(word_list)

    def _delete_character(self, word: str) -> str:
        """Delete a random character."""
        if len(word) < 2:
            return word
        pos = random.randint(0, len(word) - 1)
        return word[:pos] + word[pos + 1:]

    def _insert_character(self, word: str) -> str:
        """Insert a random character."""
        pos = random.randint(0, len(word))
        char = random.choice("abcdefghijklmnopqrstuvwxyz")
        return word[:pos] + char + word[pos:]

    def _replace_character(self, word: str) -> str:
        """Replace a random character with another."""
        pos = random.randint(0, len(word) - 1)
        char = random.choice("abcdefghijklmnopqrstuvwxyz")
        return word[:pos] + char + word[pos + 1:]


def calculate_actual_error_rate(original: str, corrupted: str) -> float:
    """
    Calculate the actual error rate between two texts.

    Args:
        original: Original text
        corrupted: Corrupted text

    Returns:
        Fraction of words that differ
    """
    orig_words = original.split()
    corr_words = corrupted.split()

    if len(orig_words) != len(corr_words):
        # Word count changed (shouldn't happen but handle gracefully)
        return min(len(orig_words), len(corr_words)) / max(len(orig_words), len(corr_words))

    errors = sum(1 for o, c in zip(orig_words, corr_words) if o != c)
    return errors / len(orig_words) if orig_words else 0.0
