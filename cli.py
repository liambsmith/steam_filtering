"""CLI commands for Steam Filter."""
import typer
from typing import Optional, List
from pathlib import Path
import pandas as pd
import time
from models import SteamGame
from steam_api import search_games, get_game_details, SteamAPIError
from matcher import match_games
from cache import init_db, get_cache, set_cache, clear_cache
from output import print_table, export_csv, export_json


app = typer.Typer(
    name="steam-filter",
    help="Filter and analyze your Steam game key redemption list."
)


def validate_csv(ctx: typer.Context, value: Optional[str]):
    """Validate CSV file exists."""
    if value:
        path = Path(value)
        if not path.exists():
            raise typer.BadParameter(f"File not found: {value}")
    return value


@app.command()
def main(
    csv_file: str = typer.Argument(
        ...,
        help="Path to CSV file with game titles",
        callback=validate_csv
    ),
    output: Optional[str] = typer.Option(
        None, "--output", "-o",
        help="Output CSV file path"
    ),
    min_rating: Optional[int] = typer.Option(
        None, "--min-rating",
        help="Minimum review rating (0-100)"
    ),
    tags: Optional[str] = typer.Option(
        None, "--tags",
        help="Filter by tags (comma-separated, partial match)"
    ),
    sort_by: Optional[str] = typer.Option(
        None, "--sort-by",
        help="Sort by field (rating, match_score, released)"
    ),
    sort_order: str = typer.Option(
        "desc", "--sort-order",
        help="Sort order (asc, desc)"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v",
        help="Show verbose output"
    ),
    clear_cache_flag: bool = typer.Option(
        False, "--clear-cache",
        help="Clear cache before processing"
    )
):
    """
    Process a CSV file of game titles and enrich with Steam data.
    
    Example:
        steam-filter games.csv
        steam-filter games.csv --min-rating 80 --tags "rpg,adventure"
        steam-filter games.csv -o results.csv --sort-by rating
    """
    # Initialize cache
    init_db()
    
    if clear_cache_flag:
        clear_cache()
        if verbose:
            print("Cache cleared.")
    
    # Read CSV
    if verbose:
        print(f"Reading CSV: {csv_file}")
    
    df = pd.read_csv(csv_file)
    
    # Auto-detect title column
    title_col = None
    for col in df.columns:
        if any(keyword in col.lower() for keyword in ['title', 'game', 'name']):
            title_col = col
            break
    
    if not title_col:
        title_col = df.columns[0]
    
    if verbose:
        print(f"Using column: {title_col}")
    
    # Extract titles
    titles = df[title_col].dropna().astype(str).tolist()
    total = len(titles)
    
    if verbose:
        print(f"Found {total} games to process\n")
    
    # Process games
    games: List[SteamGame] = []
    api_calls = 0
    
    for i, title in enumerate(titles, 1):
        if verbose:
            print(f"[{i}/{total}] Processing: {title}")
        
        # Try cache first
        cached = get_cache('search', title)
        if cached:
            if verbose:
                print(f"  ✓ Cache hit")
            results = cached
        else:
            # Search Steam
            try:
                results = search_games(title)
                set_cache('search', title, results)
                api_calls += 1
            except SteamAPIError as e:
                typer.echo(f"\n❌ Error searching '{title}': {e}", err=True)
                raise typer.Exit(code=1)
        
        # Get best match
        game = match_games(results, title)
        
        # Enrich with details (optional, could be slow)
        # For now, skip detailed fetching to keep it fast
        
        games.append(game)
        
        # Simple progress
        if verbose and i % 10 == 0:
            print(f"  Processed {i}/{total} games")
    
    # Apply filters
    if min_rating:
        games = [g for g in games if (g.review_score or 0) >= min_rating]
        if verbose:
            print(f"\nFiltered by min rating {min_rating}: {len(games)} games")
    
    if tags:
        tag_list = [t.strip().lower() for t in tags.split(",")]
        games = [g for g in games if any(
            tag.lower() in " ".join(g.top_tags).lower() or 
            any(tag.lower() in t.lower() for t in g.top_tags)
            for tag in tag_list
        )]
        if verbose:
            print(f"Filtered by tags: {len(games)} games")
    
    # Apply sorting
    if sort_by:
        reverse = sort_order.lower() == "desc"
        if sort_by == "rating":
            games.sort(key=lambda g: g.review_score or 0, reverse=reverse)
        elif sort_by == "match_score":
            games.sort(key=lambda g: g.match_score, reverse=reverse)
        elif sort_by == "released":
            games.sort(key=lambda g: g.released or "", reverse=reverse)
    
    # Print results
    print_table(games)
    
    # Export if requested
    if output:
        export_csv(games, output)


if __name__ == "__main__":
    app()
