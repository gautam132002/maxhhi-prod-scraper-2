import os
import csv
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

# Function to scrape product information
def scrape_product_info(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract product information
        product_info = {}

        title_tag = soup.find('h1', class_='ty-product-block-title')
        product_info['Product Title'] = title_tag.text.strip() if title_tag else ''

        image_divs = soup.find('div', class_='ty-product-img cm-preview-wrapper')
        
        image_urls = []
        if image_divs:
            image_tags = image_divs.find_all('img')
            for image in image_tags:
                image_url = image.get("src", "")
                image_urls.append(image_url)
        product_info['Product Image URLs'] = image_urls

        description_div = soup.find('div', id='content_description')
        product_info['Product Description'] = description_div.text.strip() if description_div else ''

        price_div = soup.find('div', class_='ty-product-block__price-actual')
        product_info['Product Price'] = price_div.text.strip() if price_div else ''

        stock_div = soup.find('div', class_='ty-control-group product-list-field')
        stock_span = stock_div.find('span')
        product_info['Product Stock'] = stock_span.text.strip() if stock_span else ''

        code_div = soup.find('div', class_='ty-product-block__sku')
        code_span = code_div.find('span')
        product_info['Product Code'] = code_span.text.strip() if code_span else ''

        breadcrumbs_div = soup.find('div', class_='ty-breadcrumbs clearfix')
        breadcrumbs_text = breadcrumbs_div.text.strip() if breadcrumbs_div else ''
        breadcrumbs_parts = breadcrumbs_text.split('/')
        if len(breadcrumbs_parts) >= 3:
            product_info['Device Type'] = breadcrumbs_parts[-2].strip()
            product_info['Device Category'] = breadcrumbs_parts[-3].strip()
        else:
            product_info['Device Type'] = ''
            product_info['Device Category'] = ''

        return product_info

    except Exception as e:
        print(f"Error occurred during scraping {url}: {str(e)}")
        return {}

# Function to process a single CSV file
def process_csv(file_path, output_dir):
    print(f"Processing file: {file_path}")
    
    data_list = []
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        urls = [row['Product Links'] for row in reader]

    # Use ThreadPoolExecutor to scrape data concurrently
    with ThreadPoolExecutor(max_workers=15) as executor:
        future_to_url = {executor.submit(scrape_product_info, url): url for url in urls}
        
        # Use tqdm to display the progress bar for scraping
        for future in tqdm(as_completed(future_to_url), total=len(urls), desc="Scraping URLs"):
            url = future_to_url[future]
            try:
                data = future.result()
                if data:
                    data_list.append(data)
            except Exception as e:
                print(f"Error scraping {url}: {str(e)}")

    if data_list:
        header = data_list[0].keys()
        output_file_path = os.path.join(output_dir, os.path.basename(file_path).replace('.csv', '_result.csv'))
        
        with open(output_file_path, 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=header)
            writer.writeheader()
            writer.writerows(data_list)
        print(f"Processed and saved: {output_file_path}")

# Wrapper code to process all CSV files in a folder one at a time
def process_all_csvs(input_dir, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    csv_files = [f for f in os.listdir(input_dir) if f.endswith('.csv')]
    num_files = len(csv_files)
    print(f"Found {num_files} CSV files in the folder: {input_dir}")

    # Process each CSV file one by one
    for csv_file in tqdm(csv_files, desc="Processing CSV files"):
        file_path = os.path.join(input_dir, csv_file)
        process_csv(file_path, output_dir)

# Directory containing the CSV files
input_directory = 'a'  # Replace with your input directory path
output_directory = 'outputs'

# Process all CSV files in the input directory
process_all_csvs(input_directory, output_directory)
