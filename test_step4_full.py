"""Full analysis test - analyze all 18 clauses and compare with expected output."""

import os
import json
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from dotenv import load_dotenv

from sandstone.services.document_parser import DocumentParser
from sandstone.services.playbook_loader import PlaybookLoader
from sandstone.services.semantic_matcher import SemanticMatcher
from sandstone.services.issue_analyzer import IssueAnalyzer
from sandstone.config import BAD_DOCUMENT_FILE, PLAYBOOK_FILE, EXPECTED_OUTPUT_FILE

console = Console()
load_dotenv()


def main():
    """Run full analysis on all 18 clauses."""
    console.print(Panel.fit(
        "[bold white]Full Analysis: All 18 Clauses[/bold white]\n"
        "[yellow]⚠ This will use OpenAI API (estimated cost: ~$0.04)[/yellow]",
        border_style="bold blue"
    ))
    
    # Setup
    console.print("\n[bold cyan]Setup[/bold cyan]")
    parser = DocumentParser()
    doc_clauses = parser.parse(BAD_DOCUMENT_FILE)
    
    loader = PlaybookLoader()
    loader.load(PLAYBOOK_FILE)
    
    matcher = SemanticMatcher(loader)
    matches = matcher.get_best_matches(doc_clauses, min_similarity=0.4)
    
    api_key = os.getenv("OPENAI_API_KEY")
    analyzer = IssueAnalyzer(api_key=api_key)
    
    console.print(f"✓ Ready to analyze {len(matches)} clauses")
    
    # Analyze all clauses
    console.print("\n[bold cyan]Analyzing All Clauses[/bold cyan]")
    redlines = analyzer.analyze_and_generate_redlines(matches, verbose=True)
    
    console.print(f"\n[bold green]✓ Analysis Complete![/bold green]")
    console.print(f"  • Total clauses analyzed: {len(matches)}")
    console.print(f"  • Issues found: {len(redlines)}")
    
    # Load expected output
    with open(EXPECTED_OUTPUT_FILE) as f:
        expected = json.load(f)
    
    console.print(f"  • Expected issues: {len(expected)}")
    
    # Display results table
    console.print("\n[bold cyan]Our Results vs Expected[/bold cyan]")
    
    table = Table(title="Detected Issues", show_header=True, header_style="bold magenta")
    table.add_column("Section", style="cyan", width=10)
    table.add_column("Playbook Clause", style="yellow", width=30)
    table.add_column("Snippet Preview", style="white", width=60)
    
    for i, redline in enumerate(redlines, 1):
        table.add_row(
            f"Issue {i}",
            redline.playbook_clause_reference,
            redline.text_snippet[:60] + "..."
        )
    
    console.print(table)
    
    # Compare clause references
    console.print("\n[bold cyan]Clause Coverage Comparison[/bold cyan]")
    
    our_clauses = {r.playbook_clause_reference for r in redlines}
    expected_clauses = {e['playbook_clause_reference'] for e in expected}
    
    console.print(f"\n[bold]Expected Clauses:[/bold]")
    for clause in sorted(expected_clauses):
        status = "✓" if clause in our_clauses else "✗"
        style = "green" if clause in our_clauses else "red"
        console.print(f"  {status} {clause}", style=style)
    
    console.print(f"\n[bold]Additional Clauses We Found:[/bold]")
    extra = our_clauses - expected_clauses
    if extra:
        for clause in sorted(extra):
            console.print(f"  + {clause}", style="yellow")
    else:
        console.print("  (none)", style="dim")
    
    # Save our output
    output_file = "sandstone/output/redlines.json"
    with open(output_file, 'w') as f:
        json.dump([r.model_dump() for r in redlines], f, indent=2)
    
    console.print(f"\n[bold green]✓ Output saved to {output_file}[/bold green]")
    
    # Summary
    matches_found = len(our_clauses & expected_clauses)
    precision = matches_found / len(our_clauses) if our_clauses else 0
    recall = matches_found / len(expected_clauses) if expected_clauses else 0
    
    console.print(f"\n[bold]Matching Metrics:[/bold]")
    console.print(f"  • Clause overlap: {matches_found}/{len(expected_clauses)}")
    console.print(f"  • Precision: {precision:.1%}")
    console.print(f"  • Recall: {recall:.1%}")


if __name__ == "__main__":
    main()
