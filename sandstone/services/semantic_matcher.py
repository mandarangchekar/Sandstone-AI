"""Semantic matcher for connecting document clauses with playbook clauses."""

from sandstone.models.document import DocumentClause
from sandstone.models.redline import ClauseMatch
from sandstone.services.playbook_loader import PlaybookLoader


class SemanticMatcher:
    """Matches document clauses to playbook clauses using semantic similarity."""
    
    def __init__(self, playbook_loader: PlaybookLoader):
        """Initialize semantic matcher.
        
        Args:
            playbook_loader: Loaded playbook with semantic search index
        """
        self.playbook_loader = playbook_loader
    
    def match_clauses(
        self,
        doc_clauses: list[DocumentClause],
        top_k: int = 1,
        min_similarity: float = 0.0
    ) -> list[ClauseMatch]:
        """Match document clauses to playbook clauses.
        
        For each document clause, finds the top-k most similar playbook clauses
        using semantic search.
        
        Args:
            doc_clauses: List of document clauses to match
            top_k: Number of matches to return per document clause
            min_similarity: Minimum similarity threshold (0-1)
            
        Returns:
            List of ClauseMatch objects
        """
        all_matches = []
        
        for doc_clause in doc_clauses:
            # Find similar playbook clauses
            similar_clauses = self.playbook_loader.find_similar(
                query_text=doc_clause.text,
                k=top_k
            )
            
            # Create ClauseMatch for each result
            for rank, (playbook_clause, similarity) in enumerate(similar_clauses, start=1):
                # Filter by minimum similarity
                if similarity < min_similarity:
                    continue
                
                match = ClauseMatch(
                    document_clause=doc_clause,
                    playbook_clause=playbook_clause,
                    similarity_score=similarity,
                    rank=rank
                )
                all_matches.append(match)
        
        return all_matches
    
    def match_single_clause(
        self,
        doc_clause: DocumentClause,
        top_k: int = 3
    ) -> list[ClauseMatch]:
        """Match a single document clause to playbook clauses.
        
        Useful for analyzing a specific clause in detail.
        
        Args:
            doc_clause: Document clause to match
            top_k: Number of matches to return
            
        Returns:
            List of ClauseMatch objects sorted by similarity
        """
        similar_clauses = self.playbook_loader.find_similar(
            query_text=doc_clause.text,
            k=top_k
        )
        
        matches = []
        for rank, (playbook_clause, similarity) in enumerate(similar_clauses, start=1):
            match = ClauseMatch(
                document_clause=doc_clause,
                playbook_clause=playbook_clause,
                similarity_score=similarity,
                rank=rank
            )
            matches.append(match)
        
        return matches
    
    def get_best_matches(
        self,
        doc_clauses: list[DocumentClause],
        min_similarity: float = 0.4
    ) -> list[ClauseMatch]:
        """Get only the best match for each document clause.
        
        Convenience method that returns top-1 matches above threshold.
        
        Args:
            doc_clauses: List of document clauses
            min_similarity: Minimum similarity threshold
            
        Returns:
            List of ClauseMatch objects (one per document clause)
        """
        return self.match_clauses(
            doc_clauses=doc_clauses,
            top_k=1,
            min_similarity=min_similarity
        )

