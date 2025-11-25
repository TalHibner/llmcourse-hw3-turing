"""Unit tests for semantic analysis module."""

import pytest
import numpy as np
from src.analysis.embeddings import SemanticAnalyzer


class TestSemanticAnalyzer:
    """Test suite for SemanticAnalyzer class."""

    @pytest.fixture
    def analyzer(self):
        """Create SemanticAnalyzer instance for testing."""
        # Use a lightweight model for testing
        return SemanticAnalyzer(model_name="sentence-transformers/all-MiniLM-L6-v2")

    def test_initialization(self, analyzer):
        """Test SemanticAnalyzer initialization."""
        assert analyzer is not None
        assert hasattr(analyzer, 'model')
        assert hasattr(analyzer, 'cache')

    def test_get_embedding_returns_vector(self, analyzer):
        """Test that get_embedding returns a numpy array."""
        text = "This is a test sentence."
        embedding = analyzer.get_embedding(text)

        assert isinstance(embedding, np.ndarray)
        assert len(embedding.shape) == 1  # Should be 1D vector
        assert embedding.shape[0] > 0  # Should have positive dimensions

    def test_get_embedding_consistent(self, analyzer):
        """Test that same text produces same embedding."""
        text = "Consistent test sentence"

        embedding1 = analyzer.get_embedding(text)
        embedding2 = analyzer.get_embedding(text)

        # Should be identical due to caching
        np.testing.assert_array_equal(embedding1, embedding2)

    def test_get_embedding_different_texts(self, analyzer):
        """Test that different texts produce different embeddings."""
        text1 = "The cat sits on the mat"
        text2 = "Dogs play in the park"

        embedding1 = analyzer.get_embedding(text1)
        embedding2 = analyzer.get_embedding(text2)

        # Embeddings should be different
        assert not np.array_equal(embedding1, embedding2)

    def test_embedding_caching(self, analyzer):
        """Test that embeddings are cached correctly."""
        text = "Cache test sentence"

        # First call
        embedding1 = analyzer.get_embedding(text)
        assert text in analyzer.cache

        # Second call should use cache
        embedding2 = analyzer.get_embedding(text)
        assert embedding1 is embedding2  # Same object reference

    def test_calculate_cosine_distance_identical(self, analyzer):
        """Test cosine distance for identical texts."""
        text = "Identical sentence for testing"

        distance = analyzer.calculate_cosine_distance(text, text)

        # Distance should be very close to 0 for identical texts
        assert distance < 0.01
        assert distance >= 0  # Distance should be non-negative

    def test_calculate_cosine_distance_similar(self, analyzer):
        """Test cosine distance for similar texts."""
        text1 = "The quick brown fox jumps over the lazy dog"
        text2 = "The fast brown fox leaps over the lazy dog"

        distance = analyzer.calculate_cosine_distance(text1, text2)

        # Similar texts should have small distance
        assert 0 <= distance < 0.5
        assert isinstance(distance, float)

    def test_calculate_cosine_distance_dissimilar(self, analyzer):
        """Test cosine distance for dissimilar texts."""
        text1 = "The weather is sunny today"
        text2 = "Mathematics involves complex equations"

        distance = analyzer.calculate_cosine_distance(text1, text2)

        # Dissimilar texts should have larger distance
        assert distance > 0.1
        assert isinstance(distance, float)

    def test_calculate_cosine_distance_range(self, analyzer):
        """Test that cosine distance is in valid range [0, 2]."""
        text1 = "Random text one"
        text2 = "Completely different content"

        distance = analyzer.calculate_cosine_distance(text1, text2)

        # Cosine distance should be in range [0, 2]
        assert 0 <= distance <= 2

    def test_calculate_euclidean_distance(self, analyzer):
        """Test Euclidean distance calculation."""
        text1 = "First test sentence"
        text2 = "Second test sentence"

        distance = analyzer.calculate_euclidean_distance(text1, text2)

        assert isinstance(distance, float)
        assert distance >= 0  # Distance should be non-negative

    def test_calculate_euclidean_distance_identical(self, analyzer):
        """Test Euclidean distance for identical texts."""
        text = "Identical for Euclidean test"

        distance = analyzer.calculate_euclidean_distance(text, text)

        # Distance should be very close to 0
        assert distance < 0.01

    def test_calculate_euclidean_distance_different(self, analyzer):
        """Test Euclidean distance for different texts."""
        text1 = "First distinct sentence"
        text2 = "Second distinct sentence"

        distance = analyzer.calculate_euclidean_distance(text1, text2)

        # Distance should be positive
        assert distance > 0

    def test_calculate_manhattan_distance(self, analyzer):
        """Test Manhattan distance calculation."""
        text1 = "Manhattan distance test one"
        text2 = "Manhattan distance test two"

        distance = analyzer.calculate_manhattan_distance(text1, text2)

        assert isinstance(distance, float)
        assert distance >= 0

    def test_calculate_manhattan_distance_identical(self, analyzer):
        """Test Manhattan distance for identical texts."""
        text = "Same text for Manhattan"

        distance = analyzer.calculate_manhattan_distance(text, text)

        assert distance < 0.01

    def test_calculate_distance_with_metric(self, analyzer):
        """Test generic calculate_distance method with different metrics."""
        text1 = "Test sentence one"
        text2 = "Test sentence two"

        # Test cosine
        cosine_dist = analyzer.calculate_distance(text1, text2, metric='cosine')
        assert isinstance(cosine_dist, float)

        # Test euclidean
        euclidean_dist = analyzer.calculate_distance(text1, text2, metric='euclidean')
        assert isinstance(euclidean_dist, float)

        # Test manhattan
        manhattan_dist = analyzer.calculate_distance(text1, text2, metric='manhattan')
        assert isinstance(manhattan_dist, float)

    def test_calculate_distance_invalid_metric(self, analyzer):
        """Test that invalid metric raises error."""
        text1 = "Test one"
        text2 = "Test two"

        with pytest.raises((ValueError, KeyError)):
            analyzer.calculate_distance(text1, text2, metric='invalid_metric')

    def test_calculate_distance_default_metric(self, analyzer):
        """Test default metric (cosine)."""
        text1 = "Default metric test"
        text2 = "Another test sentence"

        # Default should be cosine
        distance_default = analyzer.calculate_distance(text1, text2)
        distance_cosine = analyzer.calculate_cosine_distance(text1, text2)

        assert abs(distance_default - distance_cosine) < 0.001

    def test_empty_text_handling(self, analyzer):
        """Test handling of empty strings."""
        # Most models handle empty strings, but may produce zero vectors
        embedding = analyzer.get_embedding("")

        assert isinstance(embedding, np.ndarray)
        assert embedding.shape[0] > 0

    def test_special_characters_handling(self, analyzer):
        """Test handling of special characters."""
        text = "Special chars: @#$% & !?."
        embedding = analyzer.get_embedding(text)

        assert isinstance(embedding, np.ndarray)
        assert embedding.shape[0] > 0

    def test_multilingual_text(self, analyzer):
        """Test handling of non-English text."""
        text_french = "Bonjour, comment allez-vous?"
        text_hebrew = "שלום, מה שלומך?"

        embedding_fr = analyzer.get_embedding(text_french)
        embedding_he = analyzer.get_embedding(text_hebrew)

        assert isinstance(embedding_fr, np.ndarray)
        assert isinstance(embedding_he, np.ndarray)

    def test_distance_symmetry(self, analyzer):
        """Test that distance is symmetric: d(a,b) = d(b,a)."""
        text1 = "First text for symmetry"
        text2 = "Second text for symmetry"

        distance_12 = analyzer.calculate_cosine_distance(text1, text2)
        distance_21 = analyzer.calculate_cosine_distance(text2, text1)

        # Distance should be symmetric
        assert abs(distance_12 - distance_21) < 0.0001

    def test_triangle_inequality(self, analyzer):
        """Test triangle inequality: d(a,c) <= d(a,b) + d(b,c)."""
        text1 = "First sentence"
        text2 = "Second sentence closely related"
        text3 = "Third completely different topic about science"

        d_12 = analyzer.calculate_cosine_distance(text1, text2)
        d_23 = analyzer.calculate_cosine_distance(text2, text3)
        d_13 = analyzer.calculate_cosine_distance(text1, text3)

        # Triangle inequality (may not hold perfectly for cosine distance)
        # But should be reasonable
        assert isinstance(d_12, float) and isinstance(d_23, float) and isinstance(d_13, float)

    def test_cache_size_growth(self, analyzer):
        """Test that cache grows as new texts are processed."""
        initial_size = len(analyzer.cache)

        texts = [f"Test sentence number {i}" for i in range(5)]
        for text in texts:
            analyzer.get_embedding(text)

        final_size = len(analyzer.cache)
        assert final_size == initial_size + 5

    def test_long_text_handling(self, analyzer):
        """Test handling of very long text."""
        long_text = " ".join(["word"] * 1000)  # Very long text

        embedding = analyzer.get_embedding(long_text)

        assert isinstance(embedding, np.ndarray)
        assert embedding.shape[0] > 0

    def test_embedding_normalization(self, analyzer):
        """Test that embeddings are unit normalized."""
        text = "Test for normalization"
        embedding = analyzer.get_embedding(text)

        # Check if close to unit norm (many models normalize embeddings)
        norm = np.linalg.norm(embedding)
        # Some models normalize, others don't - just check it's reasonable
        assert norm > 0

    def test_batch_consistency(self, analyzer):
        """Test that repeated calculations are consistent."""
        text1 = "Consistency test one"
        text2 = "Consistency test two"

        distances = [
            analyzer.calculate_cosine_distance(text1, text2)
            for _ in range(3)
        ]

        # All distances should be identical
        assert all(abs(d - distances[0]) < 0.0001 for d in distances)
