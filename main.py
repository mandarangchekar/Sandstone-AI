"""
Main Redlining Script: Document Redlining with LLMs

This script analyzes NDA documents against a legal playbook and identifies issues.

Usage:
    uv run python main.py --document docs/bad_document.txt.rtf --playbook docs/playbook.json
    
    Or simply:
    uv run python main.py  (uses default paths)
"""

import os
import json
import argparse
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.table import Table
from dotenv import load_dotenv

from sandstone.services.document_parser import DocumentParser
from sandstone.services.playbook_loader import PlaybookLoader
from sandstone.services.semantic_matcher import SemanticMatcher
from sandstone.services.issue_analyzer import IssueAnalyzer
from sandstone.services.evaluator import RedlineEvaluator
from sandstone.config import (
    BAD_DOCUMENT_FILE,
    PLAYBOOK_FILE,
    REDLINES_OUTPUT_FILE,
    EXPECTED_OUTPUT_FILE
)

console = Console()
load_dotenv()


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="AI-powered NDA document redlining system"
    )
    parser.add_argument(
        "--document",
        type=Path,
        default=BAD_DOCUMENT_FILE,
        help="Path to RTF document to analyze"
    )
    parser.add_argument(
        "--playbook",
        type=Path,
        default=PLAYBOOK_FILE,
        help="Path to playbook JSON file"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=REDLINES_OUTPUT_FILE,
        help="Path to output JSON file"
    )
    parser.add_argument(
        "--evaluate",
        action="store_true",
        help="Run evaluation against expected output"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed progress"
    )
    
    return parser.parse_args()


def main():
    """Main redlining pipeline."""
    # Parse arguments
    args = parse_arguments()
    
    # Display header
    console.print(Panel.fit(
        "[bold white]AI-Powered NDA Document Redlining System[/bold white]\n"
        "[dim]Analyzing documents with LLM and legal playbook[/dim]",
        border_style="bold blue"
    ))
    
    # Check API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        console.print("\n[bold red]Error: OPENAI_API_KEY not found![/bold red]")
        console.print("Please create a .env file with your API key:")
        console.print("  OPENAI_API_KEY=your_key_here")
        return 1
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            
            # Step 1: Parse Document
            task = progress.add_task("[cyan]Parsing document...", total=None)
            parser = DocumentParser()
            doc_clauses = parser.parse(args.document)
            progress.update(task, completed=True)
            console.print(f"✓ Parsed document: {len(doc_clauses)} clauses found")
            
            # Step 2: Load Playbook
            task = progress.add_task("[cyan]Loading playbook...", total=None)
            loader = PlaybookLoader()
            loader.load(args.playbook)
            progress.update(task, completed=True)
            console.print(f"✓ Loaded playbook: {len(loader.clause_list)} clauses indexed")
            
            # Step 3: Semantic Matching
            task = progress.add_task("[cyan]Matching clauses...", total=None)
            matcher = SemanticMatcher(loader)
            matches = matcher.get_best_matches(doc_clauses, min_similarity=0.4)
            progress.update(task, completed=True)
            console.print(f"✓ Matched clauses: {len(matches)} pairs created")
            
            # Step 4: LLM Issue Analysis
            console.print(f"\n[yellow]Analyzing with LLM (this may take 30-60 seconds)...[/yellow]")
            analyzer = IssueAnalyzer(api_key=api_key)
            redlines = analyzer.analyze_and_generate_redlines(
                matches, 
                verbose=args.verbose
            )
            console.print(f"✓ Analysis complete: {len(redlines)} issues detected")
            
            # Step 5: Save Output
            task = progress.add_task("[cyan]Saving output...", total=None)
            args.output.parent.mkdir(parents=True, exist_ok=True)
            with open(args.output, 'w') as f:
                json.dump(
                    [r.model_dump() for r in redlines],
                    f,
                    indent=2,
                    ensure_ascii=False
                )
            progress.update(task, completed=True)
            console.print(f"✓ Output saved: {args.output}")
        
        # Display Results Summary
        console.print("\n" + "="*70)
        console.print("[bold green]Redlining Complete![/bold green]")
        console.print("="*70)
        
        # Show issues by clause type
        console.print("\n[bold]Issues Found by Clause Type:[/bold]")
        clause_counts = {}
        for r in redlines:
            clause = r.playbook_clause_reference
            clause_counts[clause] = clause_counts.get(clause, 0) + 1
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Clause Type", style="cyan", width=35)
        table.add_column("Issues", style="yellow", width=10)
        
        for clause, count in sorted(clause_counts.items()):
            table.add_row(clause, str(count))
        
        console.print(table)
        console.print(f"\n[bold]Total Issues:[/bold] {len(redlines)}")
        
        # Run Evaluation (if requested)
        if args.evaluate:
            console.print("\n" + "="*70)
            console.print("[bold cyan]Running Evaluation...[/bold cyan]")
            console.print("="*70)
            
            evaluator = RedlineEvaluator()
            expected = evaluator.load_expected_output(EXPECTED_OUTPUT_FILE)
            metrics = evaluator.evaluate(redlines, expected)
            report = evaluator.generate_report(metrics, redlines, expected)
            
            console.print(report)
        
        console.print(f"\n[bold green]✓ Success![/bold green]")
        console.print(f"Output: {args.output}")
        
        return 0
        
    except FileNotFoundError as e:
        console.print(f"\n[bold red]Error: File not found - {e}[/bold red]")
        return 1
    except Exception as e:
        console.print(f"\n[bold red]Error: {e}[/bold red]")
        import traceback
        if args.verbose:
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())