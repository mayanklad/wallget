"""
Deprecated: Use src/wallget/downloader.py instead

wallget Alpha Coders wallpaper scraper

Downloads wallpapers from a given Alpha Coders category by parsing wallpaper cards and extracting image URLs.
"""

import logging
import time
import re
from pathlib import Path

import requests
from bs4 import BeautifulSoup

#  ============================================================================
#  Configuration
#  ============================================================================

BASE_URL = 'https://alphacoders.com'

HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/117.0.0.0 Safari/537.36'
    )
}

#  ============================================================================
# Utlility Functions
#  ============================================================================

def build_image_url(server: str, image_id: int, extension: str) -> str:
    """Construct the full image URL from server, image ID, and extension."""
    return f'https://{server}.alphacoders.com/{str(image_id)[:3]}/{image_id}.{extension}'

def download_image(url: str, dest_dir: Path) -> None:
    """Download an image from the given URL to the specified directory if it doesn not already exist."""
    
    filename = url.split('/')[-1]
    filepath = dest_dir / filename
    
    if filepath.exists():
        logging.info('Skipping (already exists): %s', filename)
        return
    
    logging.info('Downloading: %s', filename)
    response = requests.get(url, headers=HEADERS, timeout=10)
    response.raise_for_status()
    
    with open(filepath, 'wb') as file:
        file.write(response.content)
        logging.info('Downloaded: %s', filename)

#  ============================================================================
# Scraping Functions
#  ============================================================================

def get_wallpaper_page_links(category: str, page: int) -> list[str]:
    """Extract wallpaper detail page links from given category and page number."""
    category = re.sub(
        r'\s+',
        '-',
        re.sub(r'[^a-z0-9\s]', '', category.lower().strip())
    )
    url = f'{BASE_URL}/{category}-wallpapers?page={page}'
    
    logging.info('Loading page: %d', page)
    
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    links = [
        a['href'] for a in soup.select('div.thumb-container-wallpaper-desktop a[href*="wall.alphacoders.com/big.php"]')
    ]
    
    logging.info('Found %d wallpapers on page %d', len(links), page)
    
    return links

def process_wallpaper_page(detail_url: str, dest_dir: Path) -> None:
    """Process a wallpaper detail page to extract and download the wallpaper image."""
    logging.info('Processing wallpaper page: %s', detail_url)
    
    response = requests.get(detail_url, headers=HEADERS)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    download_btn = soup.select_one('span.button-download[onclick]')
    
    if not download_btn:
        logging.warning('Download button not found, skipping')
        return
    
    onclick = download_btn['onclick']
    match = re.search(r"downloadContentModal\('(.+?)',\s*(\d+),\s*'(.+?)'", onclick)
    
    if not match:
        logging.warning('Failed to parse download URL, skipping')
        return
    
    server, image_id, extension = match.groups()
    image_url = build_image_url(server, int(image_id), extension)
    
    logging.info('Extracted image URL: %s', image_url)
    
    download_image(image_url, dest_dir)
    
    time.sleep(0.5)  # polite delay
    
# ============================================================================
# Main Function
# ============================================================================

def main(category: str, pages: int, dest_dir: str) -> None:
    """Main function to scrape wallpapers from a given category and number of pages."""
    
    dest_dir = Path(dest_dir + '/Alpha Coders/' + category)
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    for page in range(1, pages + 1):
        wallpaper_page_links = get_wallpaper_page_links(category, page)
        
        for detail_url in wallpaper_page_links:
            process_wallpaper_page(detail_url, dest_dir)

    logging.info('Finished downloading wallpapers')

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    main(category='', pages=1, dest_dir='')
