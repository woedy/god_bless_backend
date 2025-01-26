import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse


# Function to download a page and save it
def download_page(url, folder):
    try:
        # Send a GET request to fetch the page content
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Failed to retrieve {url}")
            return

        # Get the base URL to resolve relative links
        base_url = urlparse(url).netloc

        # Parse the page using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Create the directory if it doesn't exist
        os.makedirs(folder, exist_ok=True)

        # Save the HTML page to the folder
        page_name = os.path.join(folder, 'index.html')
        with open(page_name, 'w', encoding='utf-8') as f:
            f.write(soup.prettify())

        # Download all assets (images, CSS, JS)
        download_assets(soup, url, folder)
        print(f"Page {url} has been saved to {page_name}")

    except Exception as e:
        print(f"Error downloading {url}: {e}")


# Function to download assets like images, CSS, JS
def download_assets(soup, base_url, folder):
    for tag in soup.find_all(['img', 'link', 'script']):
        src = None
        if tag.name == 'img':
            src = tag.get('src')
        elif tag.name == 'link' and tag.get('rel') == ['stylesheet']:
            src = tag.get('href')
        elif tag.name == 'script':
            src = tag.get('src')

        if src:
            # Resolve relative URLs
            asset_url = urljoin(base_url, src)
            asset_name = os.path.join(folder, os.path.basename(asset_url))
            try:
                # Fetch and save the asset
                asset_response = requests.get(asset_url)
                if asset_response.status_code == 200:
                    with open(asset_name, 'wb') as f:
                        f.write(asset_response.content)
                    print(f"Downloaded: {asset_url} -> {asset_name}")
                else:
                    print(f"Failed to download asset: {asset_url}")
            except Exception as e:
                print(f"Error downloading asset {asset_url}: {e}")


# Main function to start the cloning process
def clone_website(url, output_folder):
    print(f"Cloning website: {url}")
    download_page(url, output_folder)


# Example usage
url = 'https://example.com'  # Replace with the website URL you want to clone
output_folder = 'cloned_website'  # Folder where you want to store the cloned website

clone_website(url, output_folder)
