"""Playbook loader with semantic search capabilities."""

import json
import numpy as np
import faiss
from pathlib import Path
from sentence_transformers import SentenceTransformer

from sandstone.models.playbook import PlaybookClause


class PlaybookLoader:
    """Loads playbook and creates semantic search index."""
    
    def __init__(self, embedding_model: str = "all-MiniLM-L6-v2"):
        """Initialize playbook loader.
        
        Args:
            embedding_model: Name of sentence-transformer model to use
        """
        self.clauses: dict[str, PlaybookClause] = {}
        self.clause_list: list[PlaybookClause] = []
        self.searchable_texts: list[str] = []
        self.embeddings: np.ndarray | None = None
        self.index: faiss.Index | None = None
        self.model = SentenceTransformer(embedding_model)
    
    def load(self, playbook_file: Path) -> None:
        """Load playbook from JSON file and create semantic index.
        
        Args:
            playbook_file: Path to playbook.json
        """
        # Load and parse JSON
        with open(playbook_file, 'r') as f:
            data = json.load(f)
        
        # Create Pydantic models
        self.clause_list = [PlaybookClause(**item) for item in data]
        self.clauses = {clause.clause: clause for clause in self.clause_list}
        
        # Create searchable content (name + definition + instructions)
        self.searchable_texts = [
            self._create_searchable_text(clause)
            for clause in self.clause_list
        ]
        
        # Generate embeddings
        self.embeddings = self.model.encode(
            self.searchable_texts,
            show_progress_bar=False,
            convert_to_numpy=True
        )
        
        # Build FAISS index
        dimension = self.embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(self.embeddings.astype('float32'))
    
    def _create_searchable_text(self, clause: PlaybookClause) -> str:
        """Create searchable text from clause fields.
        
        Combines clause name, definition, and review instructions
        for better semantic matching.
        
        Args:
            clause: PlaybookClause object
            
        Returns:
            Combined searchable text
        """
        return f"{clause.clause}. {clause.clause_definition}. {clause.review_instruction}"
    
    def find_similar(
        self, 
        query_text: str, 
        k: int = 3
    ) -> list[tuple[PlaybookClause, float]]:
        """Find top-k most similar playbook clauses.
        
        Args:
            query_text: Document clause text to search
            k: Number of top results to return
            
        Returns:
            List of (PlaybookClause, similarity_score) tuples
        """
        if self.index is None:
            raise RuntimeError("Playbook not loaded. Call load() first.")
        
        # Encode query text
        query_embedding = self.model.encode(
            [query_text],
            show_progress_bar=False,
            convert_to_numpy=True
        )
        
        # Search FAISS index
        distances, indices = self.index.search(
            query_embedding.astype('float32'), 
            k
        )
        
        # Convert to results with similarity scores
        results = []
        for idx, dist in zip(indices[0], distances[0]):
            playbook_clause = self.clause_list[idx]
            # Convert L2 distance to similarity score (0-1 range)
            similarity = 1.0 / (1.0 + float(dist))
            results.append((playbook_clause, similarity))
        
        return results
    
    def get_clause(self, clause_name: str) -> PlaybookClause | None:
        """Get playbook clause by name.
        
        Args:
            clause_name: Name of the clause
            
        Returns:
            PlaybookClause object or None if not found
        """
        return self.clauses.get(clause_name)
    
    def get_all_clause_names(self) -> list[str]:
        """Get list of all playbook clause names.
        
        Returns:
            List of clause names
        """
        return list(self.clauses.keys())
    
    @property
    def num_clauses(self) -> int:
        """Number of clauses in playbook."""
        return len(self.clause_list)

