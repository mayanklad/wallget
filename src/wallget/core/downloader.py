"""
wallget downloader module
"""

import logging
from pathlib import Path
import requests

def download_file(url: str, dest_dir: Path, dry_run: bool) -> None:
    """Download a file from the given URL to the specified directory"""

    filename = url.split('/')[-1]
    filepath = dest_dir / filename
    
    if filepath.exists():
        logging.info('Skipping (exists): %s', filename)
        return
    
    if dry_run:
        logging.debug('[DRY RUN] Would download %s to %s', url, filepath)
        return
    
    logging.info('Downloading: %s', filename)
    
    response = requests.get(url, timeout=15)
    response.raise_for_status()
    
    with open(filepath, 'wb') as file:
        file.write(response.content)
        logging.info('Downloaded: %s', filename)
