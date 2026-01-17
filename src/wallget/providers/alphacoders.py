"""
Alpha Coders wallpaper provider module

Fetches wallpapers from Alpha Coders based on category and resolution.
"""

import logging
import re
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from wallget.core.downloader import download_file

BASE_URL = 'https://alphacoders.com'

HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/117.0.0.0 Safari/537.36'
    )
}

def _normalize_category(raw: str) -> str:
    """
    Alpha Coders specific category normalization
    
    :param raw: Raw category string
    :type raw: str
    :return: Normalized category string
    :rtype: str
    """
    
    cleaned = re.sub(r'[^a-zA-Z0-9\s]', '', raw)
    return re.sub(r'\s+', '-', cleaned.strip().lower())

def _category_with_resolution(category: str, resolution: str) -> str:
    """
    Construct category string with resolution for Alpha Coders.
    
    :param category: Base category
    :type category: str
    :param resolution: Desired resolution
    :type resolution: str
    :return: Category string with resolution
    :rtype: str
    """
    
    if resolution == '4k':
        return f'{category}-4k-wallpapers'
    return f'{category}-wallpapers'

def _build_image_url(server: str, image_id: str, ext: str) -> str:
    """
    Build the direct image URL from server, image ID, and extension.
    
    :param server: Image server
    :type server: str
    :param image_id: Image ID
    :type image_id: str
    :param ext: Image file extension
    :type ext: str
    :return: Direct image URL
    :rtype: str
    """
    
    return f'https://{server}.alphacoders.com/{image_id[:3]}/{image_id}.{ext}'

def fetch(category: str, resolution: str, pages: int, dest_dir: Path, dry_run: bool) -> None:
    """
    Fetch wallpapers from Alpha Coders for the given category and resolution.
    
    :param category: Wallpaper category
    :type category: str
    :param resolution: Desired resolution
    :type resolution: str
    :param pages: Number of pages to scrape
    :type pages: int
    :param dest_dir: Destination directory for downloads
    :type dest_dir: Path
    :param dry_run: If True, simulate downloads without saving files
    :type dry_run: bool
    """
    
    logging.info('Provider: Alpha Coders')
    logging.info('Raw category input: %s', category)
    
    norm_category = _normalize_category(category)
    cat_with_res = _category_with_resolution(norm_category, resolution)
    
    logging.info('Resolved category: %s', cat_with_res)
    
    if dry_run and not dest_dir.exists():
        logging.info('[DRY RUN] Destination directory would be created: %s', dest_dir)
    
    elif not dry_run:
        dest_dir.mkdir(parents=True, exist_ok=True)
    
    for page in range(1, pages + 1):
        url = f'{BASE_URL}/{cat_with_res}?page={page}'
        logging.info('Fetching page %d: %s', page, url)
        
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        links = [
            a['href'] for a in soup.select(
                'div.thumb-container-wallpaper-desktop a[href*="wall.alphacoders.com/big.php"]'
            )
        ]
        
        logging.debug('Found %d wallpapers on page %d', len(links), page)
        
        if not links:
            logging.info('No wallpapers found, stopping fetch.')
            break
        
        for detail_url in links:
            logging.debug('Processing wallpaper page: %s', detail_url)
            
            _process_wallpaper_page(detail_url, dest_dir, dry_run)
            time.sleep(0.5)  # polite delay

def _process_wallpaper_page(url: str, dest_dir: Path, dry_run: bool) -> None:
    """
    Process a wallpaper detail page to extract and download the wallpaper image.
    
    :param url: Wallpaper detail page URL
    :type url: str
    :param dest_dir: Destination directory for downloads
    :type dest_dir: Path
    :param dry_run: If True, simulate downloads without saving files
    :type dry_run: bool
    """

    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    download_btn = soup.select_one('span.button-download[onclick]')
    
    if not download_btn:
        logging.debug('Skipping: Download button not found')
        return
    
    match = re.search(
        r"downloadContentModal\('(.+?)',\s*(\d+),\s*'(.+?)'",
        download_btn['onclick']
    )
    
    if not match:
        logging.debug('Skipping: Failed to parse download URL')
        return

    server, image_id, extension = match.groups()
    image_url = _build_image_url(server, str(image_id), extension)
    
    logging.debug('Extracted image URL: %s', image_url)
    
    download_file(image_url, dest_dir, dry_run)
