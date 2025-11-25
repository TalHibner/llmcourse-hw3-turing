"""Unit tests for test case generation module."""

import pytest
import tempfile
import json
from pathlib import Path
from src.input.generator import TestCaseGenerator, TestCase


class TestTestCaseGenerator:
    """Test suite for TestCaseGenerator class."""

    @pytest.fixture
    def temp_sentences_file(self):
        """Create temporary sentences file for testing."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("The quick brown fox jumps over the lazy dog while running fast.\n")
            f.write("Scientists have discovered new species living in deep ocean trenches.\n")
            f.write("Technology advances rapidly changing how we communicate every single day.\n")
            temp_path = f.name

        yield temp_path

        # Cleanup
        Path(temp_path).unlink(missing_ok=True)

    @pytest.fixture
    def generator(self, temp_sentences_file):
        """Create TestCaseGenerator instance for testing."""
        return TestCaseGenerator(temp_sentences_file)

    def test_initialization(self, generator, temp_sentences_file):
        """Test TestCaseGenerator initialization."""
        assert generator is not None
        assert generator.base_sentences_file == temp_sentences_file
        assert len(generator.base_sentences) == 3

    def test_load_base_sentences(self, generator):
        """Test loading base sentences from file."""
        sentences = generator.base_sentences

        assert len(sentences) == 3
        assert all(isinstance(s, str) for s in sentences)
        assert all(len(s) > 0 for s in sentences)

    def test_load_nonexistent_file(self):
        """Test that loading nonexistent file raises error."""
        with pytest.raises(FileNotFoundError):
            TestCaseGenerator("nonexistent_file.txt")

    def test_generate_test_cases_single_rate(self, generator):
        """Test generating test cases with single error rate."""
        error_rates = [0.25]
        test_cases = generator.generate_test_cases(error_rates)

        # Should have 3 sentences × 1 error rate = 3 test cases
        assert len(test_cases) == 3
        assert all(isinstance(tc, TestCase) for tc in test_cases)

    def test_generate_test_cases_multiple_rates(self, generator):
        """Test generating test cases with multiple error rates."""
        error_rates = [0.0, 0.25, 0.5]
        test_cases = generator.generate_test_cases(error_rates)

        # Should have 3 sentences × 3 error rates = 9 test cases
        assert len(test_cases) == 9

    def test_generate_test_cases_five_rates(self, generator):
        """Test standard configuration with 5 error rates."""
        error_rates = [0.0, 0.1, 0.25, 0.375, 0.5]
        test_cases = generator.generate_test_cases(error_rates)

        # Should have 3 sentences × 5 error rates = 15 test cases
        assert len(test_cases) == 15

    def test_test_case_structure(self, generator):
        """Test that TestCase has required fields."""
        error_rates = [0.25]
        test_cases = generator.generate_test_cases(error_rates)
        tc = test_cases[0]

        assert hasattr(tc, 'id')
        assert hasattr(tc, 'original_clean')
        assert hasattr(tc, 'original_corrupted')
        assert hasattr(tc, 'target_error_rate')
        assert hasattr(tc, 'actual_error_rate')
        assert hasattr(tc, 'word_count')
        assert hasattr(tc, 'num_errors')

    def test_test_case_id_sequential(self, generator):
        """Test that test case IDs are sequential."""
        error_rates = [0.0, 0.25]
        test_cases = generator.generate_test_cases(error_rates)

        ids = [tc.id for tc in test_cases]
        assert ids == list(range(len(test_cases)))

    def test_zero_error_rate(self, generator):
        """Test test case with 0% error rate."""
        error_rates = [0.0]
        test_cases = generator.generate_test_cases(error_rates)

        # With 0% error rate, there should still be minimal errors
        for tc in test_cases:
            assert tc.target_error_rate == 0.0
            # Actual errors might be > 0 due to max(1, ...) in error injector

    def test_high_error_rate(self, generator):
        """Test test case with 50% error rate."""
        error_rates = [0.5]
        test_cases = generator.generate_test_cases(error_rates)

        for tc in test_cases:
            assert tc.target_error_rate == 0.5
            assert tc.num_errors > 0
            # Actual error rate should be close to target
            assert abs(tc.actual_error_rate - 0.5) < 0.2

    def test_word_count_accuracy(self, generator):
        """Test that word count is accurate."""
        error_rates = [0.25]
        test_cases = generator.generate_test_cases(error_rates)

        for tc in test_cases:
            actual_words = len(tc.original_clean.split())
            assert tc.word_count == actual_words

    def test_error_count_calculation(self, generator):
        """Test that error count matches actual errors."""
        error_rates = [0.25]
        test_cases = generator.generate_test_cases(error_rates)

        for tc in test_cases:
            # Actual error rate should match num_errors / word_count
            calculated_rate = tc.num_errors / tc.word_count
            assert abs(calculated_rate - tc.actual_error_rate) < 0.01

    def test_corrupted_text_differs_from_clean(self, generator):
        """Test that corrupted text differs from clean text."""
        error_rates = [0.25, 0.5]
        test_cases = generator.generate_test_cases(error_rates)

        for tc in test_cases:
            if tc.num_errors > 0:
                assert tc.original_corrupted != tc.original_clean

    def test_save_and_load_test_cases(self, generator):
        """Test saving and loading test cases to/from JSON."""
        error_rates = [0.25]
        test_cases = generator.generate_test_cases(error_rates)

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_json = f.name

        try:
            # Save
            generator.save_test_cases(test_cases, temp_json)

            # Load
            with open(temp_json, 'r', encoding='utf-8') as f:
                loaded_data = json.load(f)

            # Verify
            assert len(loaded_data) == len(test_cases)
            assert all('id' in tc for tc in loaded_data)
            assert all('original_clean' in tc for tc in loaded_data)
            assert all('target_error_rate' in tc for tc in loaded_data)

        finally:
            Path(temp_json).unlink(missing_ok=True)

    def test_multiple_error_rates_order(self, generator):
        """Test that test cases are ordered by sentence then error rate."""
        error_rates = [0.0, 0.25, 0.5]
        test_cases = generator.generate_test_cases(error_rates)

        # First 3 should be sentence 0 with different error rates
        assert test_cases[0].target_error_rate == 0.0
        assert test_cases[1].target_error_rate == 0.25
        assert test_cases[2].target_error_rate == 0.5

        # Check that same sentence appears with all error rates
        sentence_0_cases = [tc for tc in test_cases if tc.id < 3]
        assert len(set(tc.original_clean for tc in sentence_0_cases)) == 1

    def test_all_sentences_used(self, generator):
        """Test that all base sentences are used."""
        error_rates = [0.25]
        test_cases = generator.generate_test_cases(error_rates)

        # Should have one test case per sentence
        unique_sentences = set(tc.original_clean for tc in test_cases)
        assert len(unique_sentences) == 3

    def test_error_rate_range_validation(self, generator):
        """Test various error rate values."""
        # Valid rates
        valid_rates = [0.0, 0.1, 0.25, 0.5, 1.0]
        test_cases = generator.generate_test_cases(valid_rates)
        assert len(test_cases) == 3 * len(valid_rates)

    def test_empty_error_rates(self, generator):
        """Test with empty error rates list."""
        test_cases = generator.generate_test_cases([])
        assert len(test_cases) == 0

    def test_test_case_to_dict(self, generator):
        """Test TestCase conversion to dictionary."""
        error_rates = [0.25]
        test_cases = generator.generate_test_cases(error_rates)
        tc = test_cases[0]

        # TestCase is a dataclass with to_dict-like behavior via asdict
        from dataclasses import asdict
        tc_dict = asdict(tc)

        assert 'id' in tc_dict
        assert 'original_clean' in tc_dict
        assert 'target_error_rate' in tc_dict
        assert isinstance(tc_dict['id'], int)
        assert isinstance(tc_dict['word_count'], int)

    def test_minimum_word_count(self, generator):
        """Test that all sentences meet minimum word count."""
        error_rates = [0.25]
        test_cases = generator.generate_test_cases(error_rates)

        # All sentences should have reasonable word count
        for tc in test_cases:
            assert tc.word_count >= 5  # Minimum reasonable length
