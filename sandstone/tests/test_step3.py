"""Test script for Step 3: Semantic Matcher."""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from sandstone.services.document_parser import DocumentParser
from sandstone.services.playbook_loader import PlaybookLoader
from sandstone.services.semantic_matcher import SemanticMatcher
from sandstone.config import BAD_DOCUMENT_FILE, PLAYBOOK_FILE

console = Console()


def setup_components():
    """Setup document parser, playbook loader, and matcher."""
    console.print("\n[bold cyan]Setup: Loading Components[/bold cyan]")
    
    # Parse document
    parser = DocumentParser()
    doc_clauses = parser.parse(BAD_DOCUMENT_FILE)
    console.print(f"✓ Parsed document: {len(doc_clauses)} clauses", style="green")
    
    # Load playbook
    loader = PlaybookLoader()
    loader.load(PLAYBOOK_FILE)
    console.print(f"✓ Loaded playbook: {loader.num_clauses} clauses", style="green")
    
    # Create matcher
    matcher = SemanticMatcher(loader)
    console.print(f"✓ Created semantic matcher", style="green")
    
    return doc_clauses, loader, matcher


def test_matching_all_clauses(doc_clauses, matcher):
    """Test matching all document clauses."""
    console.print("\n[bold cyan]Test 1: Match All Document Clauses[/bold cyan]")
    
    # Get best match for each document clause
    matches = matcher.get_best_matches(doc_clauses, min_similarity=0.4)
    
    console.print(f"✓ Matched {len(matches)} clauses (above 0.4 similarity)", style="green")
    
    # Display results
    table = Table(
        title="Document → Playbook Matches",
        show_header=True,
        header_style="bold magenta"
    )
    table.add_column("Doc Section", style="cyan", width=12)
    table.add_column("Doc Title", style="yellow", width=25)
    table.add_column("→", style="white", width=3)
    table.add_column("Playbook Clause", style="green", width=30)
    table.add_column("Score", style="blue", width=8)
    
    for match in matches:
        table.add_row(
            match.document_clause.section_number,
            match.document_clause.section_title[:25] if match.document_clause.section_title else "N/A",
            "→",
            match.playbook_clause.clause[:30],
            f"{match.similarity_score:.3f}"
        )
    
    console.print(table)
    
    return matches


def test_top_k_matching(doc_clauses, matcher):
    """Test getting top-3 matches for each clause."""
    console.print("\n[bold cyan]Test 2: Top-3 Matches for Sample Clauses[/bold cyan]")
    
    # Pick a few interesting clauses
    sample_sections = ["1.1", "5.1", "8.1"]
    
    for section in sample_sections:
        doc_clause = next((c for c in doc_clauses if c.section_number == section), None)
        
        if not doc_clause:
            continue
        
        console.print(f"\n[bold yellow]Section {section}:[/bold yellow] {doc_clause.section_title}")
        console.print(f"[dim]{doc_clause.text[:100]}...[/dim]")
        
        # Get top-3 matches
        matches = matcher.match_single_clause(doc_clause, top_k=3)
        
        table = Table(show_header=True, header_style="bold magenta", box=None)
        table.add_column("Rank", style="cyan", width=6)
        table.add_column("Playbook Clause", style="green", width=35)
        table.add_column("Similarity", style="blue", width=10)
        
        for match in matches:
            table.add_row(
                str(match.rank),
                match.playbook_clause.clause,
                f"{match.similarity_score:.4f}"
            )
        
        console.print(table)


def test_match_quality_analysis(matches):
    """Analyze quality of matches."""
    console.print("\n[bold cyan]Test 3: Match Quality Analysis[/bold cyan]")
    
    # Categorize by similarity score
    high_confidence = [m for m in matches if m.similarity_score >= 0.6]
    medium_confidence = [m for m in matches if 0.4 <= m.similarity_score < 0.6]
    low_confidence = [m for m in matches if m.similarity_score < 0.4]
    
    console.print(f"[bold]Match Quality Distribution:[/bold]")
    console.print(f"  🟢 High confidence (≥0.6): {len(high_confidence)} matches")
    console.print(f"  🟡 Medium confidence (0.4-0.6): {len(medium_confidence)} matches")
    console.print(f"  🔴 Low confidence (<0.4): {len(low_confidence)} matches")
    
    # Show best and worst matches
    if matches:
        sorted_matches = sorted(matches, key=lambda m: m.similarity_score, reverse=True)
        
        best = sorted_matches[0]
        console.print(f"\n[bold green]Best Match:[/bold green]")
        console.print(f"  Section {best.document_clause.section_number} → {best.playbook_clause.clause}")
        console.print(f"  Score: {best.similarity_score:.4f}")
        
        worst = sorted_matches[-1]
        console.print(f"\n[bold red]Weakest Match:[/bold red]")
        console.print(f"  Section {worst.document_clause.section_number} → {worst.playbook_clause.clause}")
        console.print(f"  Score: {worst.similarity_score:.4f}")


def test_specific_clause_detail(doc_clauses, matcher):
    """Show detailed matching for a specific clause."""
    console.print("\n[bold cyan]Test 4: Detailed Match Analysis[/bold cyan]")
    
    # Get section 1.1 (Confidential Information)
    doc_clause = next((c for c in doc_clauses if c.section_number == "1.1"), None)
    
    if doc_clause:
        matches = matcher.match_single_clause(doc_clause, top_k=3)
        best_match = matches[0]
        
        console.print(Panel(
            f"[bold]Document Section:[/bold] {doc_clause.section_number}\n"
            f"[bold]Section Title:[/bold] {doc_clause.section_title}\n"
            f"[bold]Text:[/bold] {doc_clause.text[:200]}...\n\n"
            f"[bold green]Matched Playbook Clause:[/bold green] {best_match.playbook_clause.clause}\n"
            f"[bold]Similarity:[/bold] {best_match.similarity_score:.4f}\n"
            f"[bold]Required:[/bold] {best_match.playbook_clause.is_required}\n\n"
            f"[bold]Playbook Definition:[/bold]\n{best_match.playbook_clause.clause_definition}",
            title="Detailed Match: Section 1.1",
            border_style="green"
        ))


def main():
    """Run all tests."""
    console.print(Panel.fit(
        "[bold white]Step 3: Semantic Matcher Test[/bold white]",
        border_style="bold blue"
    ))
    
    try:
        # Setup
        doc_clauses, loader, matcher = setup_components()
        
        # Test 1: Match all clauses
        matches = test_matching_all_clauses(doc_clauses, matcher)
        
        # Test 2: Top-k matching
        test_top_k_matching(doc_clauses, matcher)
        
        # Test 3: Quality analysis
        test_match_quality_analysis(matches)
        
        # Test 4: Detailed analysis
        test_specific_clause_detail(doc_clauses, matcher)
        
        console.print("\n[bold green]✓ All tests passed![/bold green]")
        console.print(f"\n[bold]Summary:[/bold]")
        console.print(f"  • Document clauses: {len(doc_clauses)}")
        console.print(f"  • Playbook clauses: {loader.num_clauses}")
        console.print(f"  • Successful matches: {len(matches)}")
        
    except Exception as e:
        console.print(f"\n[bold red]✗ Error: {e}[/bold red]")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    main()

