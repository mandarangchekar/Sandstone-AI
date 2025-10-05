"""Evaluation system for comparing generated redlines with expected output."""

import json
from pathlib import Path
from rouge_score import rouge_scorer
from typing import Any

from sandstone.models.redline import RedlineIssue
from sandstone.models.evaluation import EvaluationMetrics


class RedlineEvaluator:
    """Evaluates redlining output against expected results."""
    
    def __init__(self):
        """Initialize evaluator with ROUGE scorer."""
        self.rouge_scorer = rouge_scorer.RougeScorer(
            ['rouge1', 'rouge2', 'rougeL'],
            use_stemmer=True
        )
    
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
            EvaluationMetrics with precision, recall, F1, and ROUGE scores
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
        
        # Calculate ROUGE scores for matched clauses
        rouge_scores = self._calculate_rouge_scores(gen_by_clause, exp_by_clause)
        
        return EvaluationMetrics(
            precision=precision,
            recall=recall,
            f1_score=f1_score,
            rouge_1=rouge_scores['rouge1'],
            rouge_2=rouge_scores['rouge2'],
            rouge_l=rouge_scores['rougeL'],
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
    
    def _calculate_rouge_scores(
        self,
        generated: dict[str, list[RedlineIssue]],
        expected: dict[str, list[dict]]
    ) -> dict[str, float]:
        """Calculate average ROUGE scores for matched clauses.
        
        For clauses that appear in both generated and expected,
        compare the text snippets using ROUGE metrics.
        """
        rouge1_scores = []
        rouge2_scores = []
        rougeL_scores = []
        
        # For each clause type that appears in both
        common_clauses = set(generated.keys()) & set(expected.keys())
        
        for clause in common_clauses:
            gen_issues = generated[clause]
            exp_issues = expected[clause]
            
            # Compare first issue from each (or all pairs if multiple)
            for gen_issue in gen_issues[:1]:  # Take first generated issue
                for exp_issue in exp_issues[:1]:  # Compare with first expected
                    scores = self.rouge_scorer.score(
                        exp_issue['text_snippet'],
                        gen_issue.text_snippet
                    )
                    
                    rouge1_scores.append(scores['rouge1'].fmeasure)
                    rouge2_scores.append(scores['rouge2'].fmeasure)
                    rougeL_scores.append(scores['rougeL'].fmeasure)
        
        # Return averages
        return {
            'rouge1': sum(rouge1_scores) / len(rouge1_scores) if rouge1_scores else 0.0,
            'rouge2': sum(rouge2_scores) / len(rouge2_scores) if rouge2_scores else 0.0,
            'rougeL': sum(rougeL_scores) / len(rougeL_scores) if rougeL_scores else 0.0
        }
    
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

TEXT SIMILARITY (ROUGE):
  • ROUGE-1:  {metrics.rouge_1:.1%}  (word overlap)
  • ROUGE-2:  {metrics.rouge_2:.1%}  (bigram overlap)
  • ROUGE-L:  {metrics.rouge_l:.1%}  (longest common subsequence)

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
  {'✓ PASS' if metrics.rouge_1 >= 0.5 else '✗ FAIL'} ROUGE-1 ≥ 50%      (actual: {metrics.rouge_1:.1%})

OVERALL: {'✓ SYSTEM PASSES' if (metrics.recall >= 0.8 and metrics.precision >= 0.6 and metrics.rouge_1 >= 0.5) else '⚠ NEEDS IMPROVEMENT'}
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
