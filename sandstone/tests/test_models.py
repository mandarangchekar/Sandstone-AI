"""Test script to verify Pydantic models work with actual data."""

import json
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

from sandstone.models.playbook import PlaybookClause
from sandstone.models.redline import RedlineIssue
from sandstone.config import PLAYBOOK_FILE, EXPECTED_OUTPUT_FILE

console = Console()


def test_playbook_loading():
    """Test loading playbook.json into Pydantic models."""
    console.print("\n[bold cyan]Testing Playbook Loading...[/bold cyan]")
    
    with open(PLAYBOOK_FILE, "r") as f:
        playbook_data = json.load(f)
    
    clauses = [PlaybookClause(**clause) for clause in playbook_data]
    
    console.print(f"✓ Loaded {len(clauses)} playbook clauses", style="bold green")
    
    # Show sample
    sample = clauses[0]
    console.print(Panel(
        f"[bold]Clause:[/bold] {sample.clause}\n"
        f"[bold]Required:[/bold] {sample.is_required}\n"
        f"[bold]Ideal (first 200 chars):[/bold] {sample.ideal[:200]}...",
        title="Sample Playbook Clause",
        border_style="cyan"
    ))
    
    return clauses


def test_expected_output_loading():
    """Test loading expected_output.json into Pydantic models."""
    console.print("\n[bold cyan]Testing Expected Output Loading...[/bold cyan]")
    
    with open(EXPECTED_OUTPUT_FILE, "r") as f:
        expected_data = json.load(f)
    
    issues = [RedlineIssue(**issue) for issue in expected_data]
    
    console.print(f"✓ Loaded {len(issues)} expected redline issues", style="bold green")
    
    # Show sample
    sample = issues[0]
    console.print(Panel(
        f"[bold]Playbook Reference:[/bold] {sample.playbook_clause_reference}\n"
        f"[bold]Text Snippet (first 150 chars):[/bold] {sample.text_snippet[:150]}...\n"
        f"[bold]Suggested Fix (first 150 chars):[/bold] {sample.suggested_fix[:150]}...",
        title="Sample Expected Redline Issue",
        border_style="green"
    ))
    
    return issues


def main():
    """Run all tests."""
    console.print(Panel.fit(
        "[bold white]Sandstone Model Validation Test[/bold white]",
        border_style="bold blue"
    ))
    
    try:
        playbook_clauses = test_playbook_loading()
        expected_issues = test_expected_output_loading()
        
        console.print("\n[bold green]✓ All models validated successfully![/bold green]")
        console.print(f"\n[bold]Summary:[/bold]")
        console.print(f"  • Playbook clauses: {len(playbook_clauses)}")
        console.print(f"  • Expected issues: {len(expected_issues)}")
        
    except Exception as e:
        console.print(f"\n[bold red]✗ Error: {e}[/bold red]")
        raise


if __name__ == "__main__":
    main()

