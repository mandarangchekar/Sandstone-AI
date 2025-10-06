"""Evaluation system for comparing generated redlines with expected output."""

import json
from pathlib import Path
from typing import Any

from sandstone.models.redline import RedlineIssue
from sandstone.models.evaluation import EvaluationMetrics


class RedlineEvaluator:
    """Evaluates redlining output against expected results."""
    
    def __init__(self):
        """Initialize evaluator."""
        pass
    
    def evaluate(
        self,
        generated: list[RedlineIssue],
        expected: list[dict[str, Any]]
    ) -> EvaluationMetrics:
        """Evaluate generated redlines against expected output.
        
        Args:
            generated: List of generated RedlineIssue objects
            expected: List of expected output dictionaries
            
        Returns:
            EvaluationMetrics with precision, recall, and F1 scores
        """
        # Convert to comparable format
        gen_by_clause = self._group_by_clause(generated)
        exp_by_clause = self._group_by_clause_dict(expected)
        
        # Get clause sets
        gen_clauses = set(gen_by_clause.keys())
        exp_clauses = set(exp_by_clause.keys())
        
        # Calculate clause-level metrics
        correctly_identified = len(gen_clauses & exp_clauses)
        
        precision = correctly_identified / len(gen_clauses) if gen_clauses else 0
        recall = correctly_identified / len(exp_clauses) if exp_clauses else 0
        f1_score = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0
        
        return EvaluationMetrics(
            precision=precision,
            recall=recall,
            f1_score=f1_score,
            total_issues_found=len(generated),
            total_issues_expected=len(expected),
            correctly_identified=correctly_identified
        )
    
    def _group_by_clause(
        self,
        issues: list[RedlineIssue]
    ) -> dict[str, list[RedlineIssue]]:
        """Group issues by clause type."""
        grouped = {}
        for issue in issues:
            clause = issue.playbook_clause_reference
            if clause not in grouped:
                grouped[clause] = []
            grouped[clause].append(issue)
        return grouped
    
    def _group_by_clause_dict(
        self,
        expected: list[dict[str, Any]]
    ) -> dict[str, list[dict]]:
        """Group expected issues by clause type."""
        grouped = {}
        for item in expected:
            clause = item['playbook_clause_reference']
            if clause not in grouped:
                grouped[clause] = []
            grouped[clause].append(item)
        return grouped
    
    def generate_report(
        self,
        metrics: EvaluationMetrics,
        generated: list[RedlineIssue],
        expected: list[dict[str, Any]]
    ) -> str:
        """Generate human-readable evaluation report.
        
        Args:
            metrics: Calculated metrics
            generated: Generated redlines
            expected: Expected redlines
            
        Returns:
            Formatted report string
        """
        gen_clauses = {r.playbook_clause_reference for r in generated}
        exp_clauses = {e['playbook_clause_reference'] for e in expected}
        
        found = sorted(gen_clauses & exp_clauses)
        missing = sorted(exp_clauses - gen_clauses)
        extra = sorted(gen_clauses - exp_clauses)
        
        report = f"""
╔══════════════════════════════════════════════════════════════╗
║              REDLINING EVALUATION REPORT                     ║
╚══════════════════════════════════════════════════════════════╝

CLAUSE-LEVEL METRICS:
  ✓ Precision:  {metrics.precision:.1%}  ({metrics.correctly_identified}/{len(gen_clauses)} clause types correct)
  ✓ Recall:     {metrics.recall:.1%}  ({metrics.correctly_identified}/{len(exp_clauses)} expected clauses found)
  ✓ F1 Score:   {metrics.f1_score:.1%}

ISSUE COUNTS:
  • Generated:  {metrics.total_issues_found} issues
  • Expected:   {metrics.total_issues_expected} issues
  • Matched:    {metrics.correctly_identified} clause types

CLAUSE COVERAGE:
  ✓ Found ({len(found)}):
    {self._format_list(found)}
  
  ✗ Missing ({len(missing)}):
    {self._format_list(missing) if missing else '    (none)'}
  
  + Extra ({len(extra)}):
    {self._format_list(extra) if extra else '    (none)'}

PASS/FAIL CRITERIA:
  {'✓ PASS' if metrics.recall >= 0.8 else '✗ FAIL'} Recall ≥ 80%        (actual: {metrics.recall:.1%})
  {'✓ PASS' if metrics.precision >= 0.6 else '✗ FAIL'} Precision ≥ 60%     (actual: {metrics.precision:.1%})

OVERALL: {'✓ SYSTEM PASSES' if (metrics.recall >= 0.8 and metrics.precision >= 0.6) else '⚠ NEEDS IMPROVEMENT'}
"""
        return report
    
    def _format_list(self, items: list[str]) -> str:
        """Format list of items for report."""
        if not items:
            return "    (none)"
        return "\n    ".join([f"• {item}" for item in items])
    
    @staticmethod
    def load_expected_output(file_path: Path) -> list[dict[str, Any]]:
        """Load expected output from JSON file."""
        with open(file_path) as f:
            return json.load(f)
