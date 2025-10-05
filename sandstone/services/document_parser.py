"""Document parser for extracting clauses from RTF files."""

import re
from pathlib import Path
from striprtf.striprtf import rtf_to_text

from sandstone.models.document import DocumentClause


class DocumentParser:
    """Parses RTF documents and extracts structured clauses."""
    
    def parse(self, rtf_file: Path) -> list[DocumentClause]:
        """Parse RTF document and extract clauses.
        
        Args:
            rtf_file: Path to RTF document
            
        Returns:
            List of DocumentClause objects
        """
        # Step 1: Strip RTF formatting
        clean_text = self._strip_rtf(rtf_file)
        
        # Step 2: Extract section titles (1. Definitions, 2. Confidentiality...)
        section_titles = self._extract_section_titles(clean_text)
        
        # Step 3: Extract subsections with their text
        clauses = self._extract_subsections(clean_text, section_titles)
        
        return clauses
    
    def _strip_rtf(self, rtf_file: Path) -> str:
        """Convert RTF to plain text.
        
        Args:
            rtf_file: Path to RTF file
            
        Returns:
            Clean plain text
        """
        with open(rtf_file, 'r', encoding='utf-8') as f:
            rtf_content = f.read()
        
        # Convert RTF to text
        text = rtf_to_text(rtf_content)
        
        # Clean up extra whitespace
        text = re.sub(r'\n\s*\n', '\n\n', text)  # Normalize line breaks
        text = text.strip()
        
        return text
    
    def _extract_section_titles(self, text: str) -> dict[str, str]:
        """Extract main section titles.
        
        Finds patterns like:
        - "1. Definitions"
        - "2. Confidentiality Obligations"
        
        Args:
            text: Clean document text
            
        Returns:
            Dictionary mapping section number to title
            e.g., {"1": "Definitions", "2": "Confidentiality Obligations"}
        """
        # Pattern: digit(s) followed by period, space, and title text
        # Captures: (section_num, title)
        pattern = r'^(\d+)\.\s+([^\n]+?)(?:\s*\n|$)'
        
        matches = re.findall(pattern, text, re.MULTILINE)
        
        section_titles = {}
        for num, title in matches:
            # Clean title (remove extra spaces, special chars at end)
            title = title.strip()
            section_titles[num] = title
        
        return section_titles
    
    def _extract_subsections(
        self, 
        text: str, 
        section_titles: dict[str, str]
    ) -> list[DocumentClause]:
        """Extract subsections (1.1, 2.1, etc.) with their text.
        
        Args:
            text: Clean document text
            section_titles: Dictionary of section titles
            
        Returns:
            List of DocumentClause objects
        """
        clauses = []
        
        # Pattern: subsection number followed by content
        # Captures: (main_num, sub_num, content)
        # Matches: "1.1 content..." until next section/subsection or end
        pattern = r'(\d+)\.(\d+)\s+(.*?)(?=\n\s*\d+\.\d+|\n\s*\d+\.|IN WITNESS|$)'
        
        matches = re.findall(pattern, text, re.DOTALL)
        
        for main_num, sub_num, content in matches:
            section_number = f"{main_num}.{sub_num}"
            section_title = section_titles.get(main_num)
            
            # Clean content
            content = content.strip()
            content = re.sub(r'\s+', ' ', content)  # Normalize whitespace
            
            # Skip if content is too short (likely parsing error)
            if len(content) < 10:
                continue
            
            clauses.append(DocumentClause(
                text=content,
                section_number=section_number,
                section_title=section_title
            ))
        
        return clauses
    
    @property
    def supported_formats(self) -> list[str]:
        """List of supported file formats."""
        return ['.rtf']

