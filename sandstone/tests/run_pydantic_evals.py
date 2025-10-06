"""Run Pydantic Evals evaluation on NDA redlining system."""

import os
import sys
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

os.environ["TOKENIZERS_PARALLELISM"] = "false"

import asyncio
from rich.console import Console
from rich.table import Table

from sandstone.evals.dataset import redlining_dataset
from sandstone.evals.task import redline_document

console = Console()


def format_report(report):
    """Format evaluation report as a clean table."""
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Test Case", style="white", width=30)
    table.add_column("Status", justify="center", width=8)
    table.add_column("Semantic Score", justify="center", width=15)
    table.add_column("LLM Judge", justify="center", width=10)
    
    passed = 0
    total = len(report.cases)
    
    for case in report.cases:
        # Extract semantic similarity score
        semantic_score = case.scores.get('score')
        score_value = semantic_score.value if semantic_score else 0.0
        score_str = f"{score_value:.1%}"
        
        # Extract assertion results
        assertion = case.assertions.get('assertion')
        llm_judge = case.assertions.get('LLMJudge')
        
        # Determine overall status
        all_passed = assertion and assertion.value and llm_judge and llm_judge.value
        status = "✓ PASS" if all_passed else "✗ FAIL"
        status_color = "green" if all_passed else "red"
        
        # Format individual checks
        semantic_check = "✓" if assertion and assertion.value else "✗"
        llm_check = "✓ PASS" if llm_judge and llm_judge.value else "✗ FAIL"
        
        if all_passed:
            passed += 1
        
        table.add_row(
            case.name.replace('_', ' ').title(),
            f"[{status_color}]{status}[/{status_color}]",
            f"{semantic_check} {score_str}",
            llm_check
        )
    
    console.print("\n")
    console.print(table)
    console.print(f"\n[bold]Overall:[/bold] {passed}/{total} tests passed ({passed/total:.1%})")


async def main():
    """Run comprehensive evaluation using Pydantic Evals."""
    console.print("\n[bold cyan]🚀 Running Pydantic Evals Evaluation[/bold cyan]\n")
    console.print("[yellow]⚠ This uses OpenAI API for LLM-as-judge (estimated cost: ~$0.03)[/yellow]\n")
    
    # Run evaluation
    report = await redlining_dataset.evaluate(redline_document)
    
    # Print formatted report
    format_report(report)
    
    # Print summary
    console.print("\n[bold green]✓ Evaluation Complete![/bold green]\n")


if __name__ == "__main__":
    asyncio.run(main())
