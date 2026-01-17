import argparse
from pathlib import Path

from wallget.providers import alphacoders
from wallget.utils.log import setup_logging

def main() -> None:
    """Main entry point for the wallget CLI."""
    
    parser = argparse.ArgumentParser(
        prog='wallget',
        description='Wallpaper downloader from various online providers.'
    )
    
    parser.add_argument(
        '-P', '--provider',
        default='alphacoders',
        help='Wallpaper provider to use (default: alphacoders)'
    )
    
    parser.add_argument(
        '-c', '--category',
        required=True,
        help='Wallpaper category to fetch (e.g., Nature, "Fantasy art", space, cars)'
    )
    
    parser.add_argument(
        '-r', '--resolution',
        choices=['hd', '4k'],
        default='hd',
        help='Minimum resolution of wallpapers (default: hd)'
    )
    
    parser.add_argument(
        '-p', '--pages',
        type=int,
        default=1,
        help='Number of pages to scrape (default: 1)'
    )
    
    parser.add_argument(
        '-d', '--dest',
        default=None,
        help='Destination directory for downloaded wallpapers (default: ~/Pictures/Wallget/[provider]/[category])'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Simulate downloads without saving files'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    setup_logging(args.verbose or args.dry_run)
        
    if args.provider.lower() == 'alphacoders':
        if args.dest is None:
            dest_dir = Path.home() / 'Pictures' / 'Wallget' / 'Alpha Coders' / args.category.title()
        else:
            dest_dir = Path(args.dest)

        alphacoders.fetch(
            category=args.category,
            resolution=args.resolution,
            pages=args.pages,
            dest_dir=dest_dir,
            dry_run=args.dry_run
        )
    else:
        raise SystemError(f'Unsupported provider: {args.provider}')
