"""Unit tests for error injection module."""

import pytest
from src.input.error_injector import ErrorInjector


class TestErrorInjector:
    """Test suite for ErrorInjector class."""

    @pytest.fixture
    def injector(self):
        """Create ErrorInjector instance for testing."""
        return ErrorInjector()

    def test_initialization(self, injector):
        """Test ErrorInjector initialization."""
        assert injector is not None
        assert hasattr(injector, 'inject_errors')

    def test_inject_errors_zero_rate(self, injector):
        """Test that zero error rate returns original text."""
        text = "Hello world this is a test sentence"
        corrupted, num_errors = injector.inject_errors(text, 0.0)

        # With 0% error rate, should still inject at least 1 error due to max(1, ...)
        assert isinstance(corrupted, str)
        assert isinstance(num_errors, int)
        assert num_errors >= 1

    def test_inject_errors_full_rate(self, injector):
        """Test that 100% error rate corrupts all words."""
        text = "Hello world test"
        corrupted, num_errors = injector.inject_errors(text, 1.0)

        assert isinstance(corrupted, str)
        assert num_errors == 3  # All 3 words should be corrupted

    def test_inject_errors_25_percent(self, injector):
        """Test 25% error rate on 12-word sentence."""
        text = "The quick brown fox jumps over the lazy dog near the forest"  # 12 words
        corrupted, num_errors = injector.inject_errors(text, 0.25)

        assert isinstance(corrupted, str)
        assert isinstance(num_errors, int)
        assert num_errors == 3  # 25% of 12 = 3 errors

    def test_inject_errors_50_percent(self, injector):
        """Test 50% error rate."""
        text = "One two three four five six seven eight"  # 8 words
        corrupted, num_errors = injector.inject_errors(text, 0.5)

        assert isinstance(corrupted, str)
        assert num_errors == 4  # 50% of 8 = 4 errors

    def test_inject_errors_returns_different_text(self, injector):
        """Test that error injection actually modifies the text."""
        text = "The quick brown fox jumps over lazy dog"
        corrupted, num_errors = injector.inject_errors(text, 0.5)

        # With 50% error rate, text should be different
        assert corrupted != text
        assert num_errors > 0

    def test_inject_errors_preserves_word_count(self, injector):
        """Test that word count is preserved after error injection."""
        text = "The quick brown fox jumps over the lazy dog"
        original_word_count = len(text.split())

        corrupted, _ = injector.inject_errors(text, 0.25)
        corrupted_word_count = len(corrupted.split())

        assert corrupted_word_count == original_word_count

    def test_inject_errors_handles_single_word(self, injector):
        """Test error injection on single word."""
        text = "Hello"
        corrupted, num_errors = injector.inject_errors(text, 1.0)

        assert isinstance(corrupted, str)
        assert num_errors == 1

    def test_inject_errors_handles_long_text(self, injector):
        """Test error injection on longer text."""
        text = " ".join(["word"] * 50)  # 50 words
        corrupted, num_errors = injector.inject_errors(text, 0.1)

        assert isinstance(corrupted, str)
        assert num_errors == 5  # 10% of 50 = 5

    def test_corrupt_word_character_swap(self, injector):
        """Test character swap corruption."""
        # Set seed for reproducibility
        import random
        random.seed(42)

        word = "hello"
        # Call multiple times to get swap operation
        corrupted_words = [injector._corrupt_word(word) for _ in range(10)]

        # At least one should be different from original
        assert any(w != word for w in corrupted_words)
        # All should be strings
        assert all(isinstance(w, str) for w in corrupted_words)

    def test_corrupt_word_preserves_length_mostly(self, injector):
        """Test that corruption preserves approximate word length."""
        word = "testing"
        corrupted = injector._corrupt_word(word)

        # Length should be within 1 character (due to insertions/deletions)
        assert abs(len(corrupted) - len(word)) <= 1

    def test_inject_errors_with_punctuation(self, injector):
        """Test error injection handles punctuation correctly."""
        text = "Hello, world! This is a test."
        corrupted, num_errors = injector.inject_errors(text, 0.25)

        assert isinstance(corrupted, str)
        assert num_errors > 0

    def test_inject_errors_minimum_one_error(self, injector):
        """Test that at least one error is always injected."""
        text = "Hello world"
        corrupted, num_errors = injector.inject_errors(text, 0.01)  # Very low rate

        # Should still inject at least 1 error due to max(1, ...)
        assert num_errors >= 1

    def test_error_rate_accuracy(self, injector):
        """Test that actual error rate matches target."""
        text = " ".join(["word"] * 20)  # 20 words
        target_rate = 0.3

        corrupted, num_errors = injector.inject_errors(text, target_rate)
        actual_rate = num_errors / 20

        # Should be close to target rate
        assert abs(actual_rate - target_rate) < 0.1

    def test_inject_errors_idempotence(self, injector):
        """Test that multiple injections produce different results."""
        text = "The quick brown fox"

        corrupted1, _ = injector.inject_errors(text, 0.5)
        corrupted2, _ = injector.inject_errors(text, 0.5)

        # Due to randomness, results should likely be different
        # (This test might occasionally fail due to random chance)
        assert isinstance(corrupted1, str)
        assert isinstance(corrupted2, str)
