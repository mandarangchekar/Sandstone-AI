"""Test proper evaluation with ROUGE scores."""

import json
from rich.console import Console

from sandstone.services.evaluator import RedlineEvaluator
from sandstone.models.redline import RedlineIssue
from sandstone.config import EXPECTED_OUTPUT_FILE

console = Console()


def main():
    """Run proper evaluation."""
    console.print("\n[bold cyan]Running Proper Evaluation[/bold cyan]\n")
    
    # Load generated output
    with open("sandstone/output/redlines.json") as f:
        generated_data = json.load(f)
    generated = [RedlineIssue(**item) for item in generated_data]
    
    # Load expected output
    with open(EXPECTED_OUTPUT_FILE) as f:
        expected = json.load(f)
    
    # Create evaluator
    evaluator = RedlineEvaluator()
    
    # Evaluate
    metrics = evaluator.evaluate(generated, expected)
    
    # Generate report
    report = evaluator.generate_report(metrics, generated, expected)
    
    console.print(report)


if __name__ == "__main__":
    main()
