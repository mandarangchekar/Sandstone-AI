"""Test script for Step 2B: Playbook Loader."""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from sandstone.services.playbook_loader import PlaybookLoader
from sandstone.config import PLAYBOOK_FILE

console = Console()


def test_playbook_loading():
    """Test basic playbook loading."""
    console.print("\n[bold cyan]Test 1: Loading Playbook[/bold cyan]")
    
    loader = PlaybookLoader()
    loader.load(PLAYBOOK_FILE)
    
    console.print(f"✓ Loaded {loader.num_clauses} playbook clauses", style="bold green")
    console.print(f"✓ Embedding dimension: {loader.embeddings.shape[1]}", style="bold green")
    console.print(f"✓ FAISS index ready", style="bold green")
    
    return loader


def test_clause_lookup(loader: PlaybookLoader):
    """Test looking up clauses by name."""
    console.print("\n[bold cyan]Test 2: Clause Lookup[/bold cyan]")
    
    clause = loader.get_clause("Confidential Information")
    
    if clause:
        console.print(Panel(
            f"[bold]Name:[/bold] {clause.clause}\n"
            f"[bold]Required:[/bold] {clause.is_required}\n"
            f"[bold]Definition:[/bold] {clause.clause_definition[:150]}...",
            title="Confidential Information Clause",
            border_style="green"
        ))
    else:
        console.print("✗ Clause not found", style="bold red")


def test_semantic_search(loader: PlaybookLoader):
    """Test semantic search with various queries."""
    console.print("\n[bold cyan]Test 3: Semantic Search[/bold cyan]")
    
    test_queries = [
        ("\"Confidential Information\" shall mean any and all data, materials...", 
         "Document text about confidential info definition"),
        
        ("Upon written request of Discloser, Recipient will return all materials...", 
         "Document text about returning materials"),
        
        ("This Agreement shall commence on the Effective Date and remain in effect for three years", 
         "Document text about agreement duration"),
        
        ("Recipient may freely assign this Agreement to any affiliate without consent",
         "Document text about assignment rights"),
    ]
    
    for query, description in test_queries:
        console.print(f"\n[bold yellow]Query:[/bold yellow] {description}")
        console.print(f"[dim]{query[:100]}...[/dim]")
        
        matches = loader.find_similar(query, k=3)
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Rank", style="cyan", width=6)
        table.add_column("Playbook Clause", style="green", width=30)
        table.add_column("Similarity", style="yellow", width=12)
        
        for rank, (clause, score) in enumerate(matches, 1):
            table.add_row(
                str(rank),
                clause.clause,
                f"{score:.4f}"
            )
        
        console.print(table)


def test_all_clause_names(loader: PlaybookLoader):
    """Test getting all clause names."""
    console.print("\n[bold cyan]Test 4: All Clause Names[/bold cyan]")
    
    names = loader.get_all_clause_names()
    
    console.print(f"[bold]All {len(names)} Playbook Clauses:[/bold]")
    for i, name in enumerate(names, 1):
        console.print(f"  {i:2d}. {name}")


def main():
    """Run all tests."""
    console.print(Panel.fit(
        "[bold white]Step 2B: Playbook Loader Test[/bold white]",
        border_style="bold blue"
    ))
    
    try:
        # Test 1: Load playbook
        loader = test_playbook_loading()
        
        # Test 2: Lookup by name
        test_clause_lookup(loader)
        
        # Test 3: Semantic search
        test_semantic_search(loader)
        
        # Test 4: All clause names
        test_all_clause_names(loader)
        
        console.print("\n[bold green]✓ All tests passed![/bold green]")
        
    except Exception as e:
        console.print(f"\n[bold red]✗ Error: {e}[/bold red]")
        raise


if __name__ == "__main__":
    main()

