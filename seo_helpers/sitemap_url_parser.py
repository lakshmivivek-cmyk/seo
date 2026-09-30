#Reads an XML sitemap file, loops through the URL elements, grabs all the web links, and neatly exports them into a CSV file for your SEO or tracking analysis.
import xml.etree.ElementTree as ET
import csv
from pathlib import Path

def parse_sitemap(input_file, output_csv):
    try:
        # Ensure the output directory exists
        output_csv.parent.mkdir(parents=True, exist_ok=True)

        # Parse the XML content
        tree = ET.parse(input_file)
        root = tree.getroot()

        # Extract URLs and remove duplicates while preserving order
        namespaces = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        raw_urls = [url.find('ns:loc', namespaces).text for url in root.findall('ns:url', namespaces)]
        urls = list(dict.fromkeys(raw_urls))

        # Save to CSV
        with open(output_csv, 'w', newline='', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(['URL'])
            writer.writerows([[url] for url in urls])

        print(f"Successfully saved {len(urls)} unique URLs to {output_csv}")
    except Exception as e:
        print(f"Error: {e}")

# Input XML file path (update this to your local file path when ready)
input_file = "path_to_your_local_sitemap.xml"

# Define output using pathlib so it drops cleanly into your 'outputs' folder
output_csv = Path("outputs") / "sitemap_urls_establishment_listings.csv"

parse_sitemap(input_file, output_csv)