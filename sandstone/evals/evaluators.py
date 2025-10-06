"""Custom evaluators for redlining evaluation."""

from typing import Any

from pydantic_evals.evaluators import Evaluator, EvaluatorContext
from sentence_transformers import SentenceTransformer, util


class SemanticSimilarity(Evaluator):
    """Evaluates semantic similarity between snippets using embeddings."""
    
    def __init__(
        self,
        threshold: float = 0.75,
        embedding_model: str = "all-MiniLM-L6-v2"
    ):
        """Initialize semantic similarity evaluator.
        
        Args:
            threshold: Minimum similarity score to pass (0.0 to 1.0)
            embedding_model: Sentence transformer model name
        """
        self.threshold = threshold
        self.encoder = SentenceTransformer(embedding_model)
    
    async def evaluate(self, ctx: EvaluatorContext[Any, Any]) -> dict[str, Any]:
        """Evaluate semantic similarity between generated and expected snippets.
        
        Args:
            ctx: Evaluation context with output and expected output
            
        Returns:
            Dict with assertion result, score, and message
        """
        # Extract snippets
        generated_snippet = ctx.output.text_snippet
        expected_snippet = ctx.expected_output["text_snippet"]
        
        # Compute embeddings
        embedding1 = self.encoder.encode(generated_snippet, convert_to_tensor=True)
        embedding2 = self.encoder.encode(expected_snippet, convert_to_tensor=True)
        
        # Compute cosine similarity
        similarity = util.cos_sim(embedding1, embedding2).item()
        similarity = max(0.0, min(1.0, similarity))
        
        return {
            "assertion": similarity >= self.threshold,
            "score": similarity,
            "message": f"Snippet similarity: {similarity:.2%} (threshold: {self.threshold:.2%})"
        }
