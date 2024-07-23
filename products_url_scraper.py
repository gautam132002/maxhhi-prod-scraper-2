import requests
import csv
import xml.etree.ElementTree as ET
from tqdm import tqdm

sitemap_url = "https://www.maxbhi.com/sitemap.xml"
csv_filename = "product_links.csv"

response = requests.get(sitemap_url)

if response.status_code == 200:
    root = ET.fromstring(response.content)

    loc_elements = root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
    all_links = []

    for loc in tqdm(loc_elements, desc="Scraping links"):
        link = loc.text
        link_response = requests.get(link)

        if link_response.status_code == 200:
            link_root = ET.fromstring(link_response.content)

            link_loc_elements = link_root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")

            link_urls = [link_loc.text for link_loc in link_loc_elements]

            all_links.extend(link_urls)

    with open(csv_filename, "w", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["Product Links"])  
        writer.writerows(zip(all_links))  

    print(f"Successfully saved links to {csv_filename}.")
    print(len(all_links), "produsts")
else:
    print(f"Failed to fetch sitemap. Error: {response.status_code}")