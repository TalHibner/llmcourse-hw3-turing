"""Semantic embedding generation module."""

import numpy as np
from sentence_transformers import SentenceTransformer
from typing import Union, List
import torch


class SemanticAnalyzer:
    """Generate semantic embeddings and calculate distances."""

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initialize the semantic analyzer.

        Args:
            model_name: Name of the sentence-transformers model
        """
        print(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.cache = {}

    def get_embedding(self, text: str) -> np.ndarray:
        """
        Generate semantic embedding for text.

        Args:
            text: Input text

        Returns:
            Embedding vector as numpy array
        """
        # Check cache
        if text in self.cache:
            return self.cache[text]

        # Generate embedding
        embedding = self.model.encode(text, convert_to_numpy=True)

        # Cache it
        self.cache[text] = embedding

        return embedding

    def calculate_cosine_distance(self, text1: str, text2: str) -> float:
        """
        Calculate cosine distance between two texts.

        Cosine distance = 1 - cosine similarity
        Range: [0, 2] where 0 = identical, 2 = opposite

        Args:
            text1: First text
            text2: Second text

        Returns:
            Cosine distance
        """
        emb1 = self.get_embedding(text1)
        emb2 = self.get_embedding(text2)

        # Cosine similarity
        similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))

        # Cosine distance
        distance = 1.0 - similarity

        return float(distance)

    def calculate_euclidean_distance(self, text1: str, text2: str) -> float:
        """
        Calculate Euclidean distance between two texts.

        Args:
            text1: First text
            text2: Second text

        Returns:
            Euclidean distance
        """
        emb1 = self.get_embedding(text1)
        emb2 = self.get_embedding(text2)

        distance = np.linalg.norm(emb1 - emb2)

        return float(distance)

    def calculate_distance(self, text1: str, text2: str, metric: str = "cosine") -> float:
        """
        Calculate semantic distance between two texts.

        Args:
            text1: First text
            text2: Second text
            metric: Distance metric ("cosine" or "euclidean")

        Returns:
            Distance value
        """
        if metric == "cosine":
            return self.calculate_cosine_distance(text1, text2)
        elif metric == "euclidean":
            return self.calculate_euclidean_distance(text1, text2)
        else:
            raise ValueError(f"Unknown metric: {metric}")

    def batch_calculate_distances(self, text_pairs: List[tuple], metric: str = "cosine") -> List[float]:
        """
        Calculate distances for multiple text pairs.

        Args:
            text_pairs: List of (text1, text2) tuples
            metric: Distance metric to use

        Returns:
            List of distance values
        """
        distances = []
        for text1, text2 in text_pairs:
            distance = self.calculate_distance(text1, text2, metric)
            distances.append(distance)
        return distances
