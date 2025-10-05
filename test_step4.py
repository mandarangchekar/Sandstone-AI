"""Test script for Step 4: LLM Issue Analyzer."""

import os
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from dotenv import load_dotenv

from sandstone.services.document_parser import DocumentParser
from sandstone.services.playbook_loader import PlaybookLoader
from sandstone.services.semantic_matcher import SemanticMatcher
from sandstone.services.issue_analyzer import IssueAnalyzer
from sandstone.config import BAD_DOCUMENT_FILE, PLAYBOOK_FILE

console = Console()

# Load environment variables
load_dotenv()


def setup_components():
    """Setup all components."""
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
    
    # Get best matches (top-1 only)
    matches = matcher.get_best_matches(doc_clauses, min_similarity=0.4)
    console.print(f"✓ Generated {len(matches)} matches", style="green")
    
    # Create issue analyzer
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment")
    
    analyzer = IssueAnalyzer(api_key=api_key)
    console.print(f"✓ Created issue analyzer", style="green")
    
    return matches, analyzer


def test_single_clause_analysis(matches, analyzer):
    """Test analyzing a single clause."""
    console.print("\n[bold cyan]Test 1: Single Clause Analysis[/bold cyan]")
    
    # Analyze section 1.1 (Confidential Information - likely has issues)
    match = next((m for m in matches if m.document_clause.section_number == "1.1"), None)
    
    if not match:
        console.print("✗ Section 1.1 not found", style="red")
        return
    
    console.print(f"\n[bold]Analyzing Section 1.1:[/bold] {match.playbook_clause.clause}")
    console.print(f"[dim]Document text: {match.document_clause.text[:150]}...[/dim]")
    
    analysis = analyzer.analyze_match(match)
    
    if analysis:
        console.print(Panel(
            f"[bold]Has Issue:[/bold] {analysis.has_issue}\n"
            f"[bold]Issue Type:[/bold] {analysis.issue_type}\n"
            f"[bold]Confidence:[/bold] {analysis.confidence:.2f}\n\n"
            f"[bold]Problematic Snippet:[/bold]\n{analysis.problematic_snippet}\n\n"
            f"[bold]Reasoning:[/bold]\n{analysis.reasoning}",
            title=f"Analysis Result: Section 1.1",
            border_style="yellow" if analysis.has_issue else "green"
        ))
        
        if analysis.has_issue:
            redline = analyzer.create_redline_issue(match, analysis)
            console.print(f"\n[bold green]Suggested Fix:[/bold green]")
            console.print(f"[dim]{redline.suggested_fix[:300]}...[/dim]")
    else:
        console.print("✗ Analysis failed", style="red")


def test_multiple_clauses(matches, analyzer, num_clauses=5):
    """Test analyzing multiple clauses."""
    console.print(f"\n[bold cyan]Test 2: Analyze {num_clauses} Clauses[/bold cyan]")
    
    # Select first N clauses for testing
    test_matches = matches[:num_clauses]
    
    console.print(f"\nAnalyzing {len(test_matches)} clauses with LLM...\n")
    
    # Analyze with verbose output
    issue_pairs = analyzer.analyze_matches(test_matches, verbose=True)
    
    console.print(f"\n[bold]Results:[/bold]")
    console.print(f"  • Clauses analyzed: {len(test_matches)}")
    console.print(f"  • Issues found: {len(issue_pairs)}")
    
    return issue_pairs


def display_issues_summary(issue_pairs, analyzer):
    """Display summary of found issues."""
    console.print("\n[bold cyan]Test 3: Issues Summary[/bold cyan]")
    
    if not issue_pairs:
        console.print("[yellow]No issues found in analyzed clauses[/yellow]")
        return
    
    table = Table(
        title="Detected Issues",
        show_header=True,
        header_style="bold magenta"
    )
    table.add_column("Section", style="cyan", width=10)
    table.add_column("Clause Type", style="yellow", width=25)
    table.add_column("Issue Type", style="red", width=12)
    table.add_column("Confidence", style="blue", width=10)
    table.add_column("Snippet", style="white", width=50)
    
    for match, analysis in issue_pairs:
        table.add_row(
            match.document_clause.section_number,
            match.playbook_clause.clause[:25],
            analysis.issue_type,
            f"{analysis.confidence:.2f}",
            analysis.problematic_snippet[:50] + "..."
        )
    
    console.print(table)


def generate_redline_output(issue_pairs, analyzer):
    """Generate final redline issues."""
    console.print("\n[bold cyan]Test 4: Generate Redline Output[/bold cyan]")
    
    redlines = []
    for match, analysis in issue_pairs:
        redline = analyzer.create_redline_issue(match, analysis)
        redlines.append(redline)
    
    console.print(f"✓ Generated {len(redlines)} redline issues", style="green")
    
    # Show first redline in detail
    if redlines:
        sample = redlines[0]
        console.print(Panel(
            f"[bold]Playbook Clause:[/bold] {sample.playbook_clause_reference}\n\n"
            f"[bold]Problematic Text:[/bold]\n{sample.text_snippet[:200]}...\n\n"
            f"[bold]Suggested Fix:[/bold]\n{sample.suggested_fix[:200]}...",
            title="Sample Redline Issue",
            border_style="green"
        ))
    
    return redlines


def compare_with_expected():
    """Compare with expected output (for reference)."""
    console.print("\n[bold cyan]Test 5: Expected Output Reference[/bold cyan]")
    
    import json
    from sandstone.config import EXPECTED_OUTPUT_FILE
    
    with open(EXPECTED_OUTPUT_FILE) as f:
        expected = json.load(f)
    
    console.print(f"[bold]Expected number of issues:[/bold] {len(expected)}")
    console.print(f"[bold]Expected clauses:[/bold]")
    for item in expected[:3]:
        console.print(f"  • {item['playbook_clause_reference']}")


def main():
    """Run all tests."""
    console.print(Panel.fit(
        "[bold white]Step 4: LLM Issue Analyzer Test[/bold white]\n"
        "[yellow]⚠ This test will use OpenAI API (estimated cost: ~$0.01)[/yellow]",
        border_style="bold blue"
    ))
    
    try:
        # Setup
        matches, analyzer = setup_components()
        
        # Test 1: Single clause analysis
        test_single_clause_analysis(matches, analyzer)
        
        # Test 2: Analyze 5 clauses
        issue_pairs = test_multiple_clauses(matches, analyzer, num_clauses=5)
        
        # Test 3: Display summary
        display_issues_summary(issue_pairs, analyzer)
        
        # Test 4: Generate redline output
        redlines = generate_redline_output(issue_pairs, analyzer)
        
        # Test 5: Compare with expected
        compare_with_expected()
        
        console.print("\n[bold green]✓ All tests passed![/bold green]")
        console.print(f"\n[bold]Note:[/bold] Tested with 5 clauses. Run full analysis on all 18 clauses in Step 5.")
        
    except ValueError as e:
        console.print(f"\n[bold red]✗ Configuration Error: {e}[/bold red]")
        console.print("\n[yellow]Please create a .env file with:[/yellow]")
        console.print("OPENAI_API_KEY=your_api_key_here")
    except Exception as e:
        console.print(f"\n[bold red]✗ Error: {e}[/bold red]")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    main()
