"""Test script for Step 2A: Document Parser."""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from sandstone.services.document_parser import DocumentParser
from sandstone.config import BAD_DOCUMENT_FILE

console = Console()


def test_document_parsing():
    """Test parsing the bad document."""
    console.print("\n[bold cyan]Test 1: Parse RTF Document[/bold cyan]")
    
    parser = DocumentParser()
    clauses = parser.parse(BAD_DOCUMENT_FILE)
    
    console.print(f"✓ Parsed RTF successfully", style="bold green")
    console.print(f"✓ Extracted {len(clauses)} clauses", style="bold green")
    
    return clauses


def display_clauses(clauses: list):
    """Display all extracted clauses in a table."""
    console.print("\n[bold cyan]Test 2: Display Extracted Clauses[/bold cyan]")
    
    table = Table(
        show_header=True, 
        header_style="bold magenta",
        title="Extracted Document Clauses",
        title_style="bold white"
    )
    table.add_column("Section", style="cyan", width=10)
    table.add_column("Parent Section", style="yellow", width=25)
    table.add_column("Text (first 80 chars)", style="white", width=80)
    
    for clause in clauses:
        table.add_row(
            clause.section_number,
            clause.section_title or "N/A",
            clause.text[:80] + ("..." if len(clause.text) > 80 else "")
        )
    
    console.print(table)


def display_sample_clause(clauses: list):
    """Display one full clause as a sample."""
    console.print("\n[bold cyan]Test 3: Sample Full Clause[/bold cyan]")
    
    if clauses:
        sample = clauses[0]
        console.print(Panel(
            f"[bold]Section:[/bold] {sample.section_number}\n"
            f"[bold]Parent:[/bold] {sample.section_title}\n"
            f"[bold]Text:[/bold] {sample.text[:300]}...",
            title=f"Sample: Section {sample.section_number}",
            border_style="green"
        ))


def analyze_sections(clauses: list):
    """Analyze section distribution."""
    console.print("\n[bold cyan]Test 4: Section Distribution[/bold cyan]")
    
    # Count clauses per section
    section_counts = {}
    for clause in clauses:
        parent = clause.section_title or "Unknown"
        section_counts[parent] = section_counts.get(parent, 0) + 1
    
    console.print("[bold]Clauses per section:[/bold]")
    for section, count in sorted(section_counts.items()):
        console.print(f"  • {section}: {count} clause(s)")
    
    console.print(f"\n[bold]Total clauses:[/bold] {len(clauses)}")


def test_specific_sections(clauses: list):
    """Test extraction of specific known sections."""
    console.print("\n[bold cyan]Test 5: Verify Key Sections[/bold cyan]")
    
    # Look for specific clauses we know should exist
    expected_sections = [
        "1.1",  # Confidential Information definition
        "5.1",  # Return or Destruction
        "8.1",  # Indemnification
        "9.1",  # Assignment
    ]
    
    found = []
    missing = []
    
    for expected in expected_sections:
        clause = next((c for c in clauses if c.section_number == expected), None)
        if clause:
            found.append(expected)
            console.print(
                f"✓ Found section {expected}: {clause.section_title}", 
                style="green"
            )
        else:
            missing.append(expected)
            console.print(f"✗ Missing section {expected}", style="red")
    
    if not missing:
        console.print(f"\n[bold green]✓ All key sections found![/bold green]")
    else:
        console.print(f"\n[bold yellow]⚠ Some sections missing: {missing}[/bold yellow]")


def main():
    """Run all tests."""
    console.print(Panel.fit(
        "[bold white]Step 2A: Document Parser Test[/bold white]",
        border_style="bold blue"
    ))
    
    try:
        # Test 1: Parse document
        clauses = test_document_parsing()
        
        if not clauses:
            console.print("[bold red]✗ No clauses extracted![/bold red]")
            return
        
        # Test 2: Display all clauses
        display_clauses(clauses)
        
        # Test 3: Show sample clause
        display_sample_clause(clauses)
        
        # Test 4: Analyze distribution
        analyze_sections(clauses)
        
        # Test 5: Verify specific sections
        test_specific_sections(clauses)
        
        console.print("\n[bold green]✓ All tests passed![/bold green]")
        
    except Exception as e:
        console.print(f"\n[bold red]✗ Error: {e}[/bold red]")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    main()

