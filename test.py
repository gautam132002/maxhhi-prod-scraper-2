from bs4 import BeautifulSoup
import csv
import requests
from tqdm import tqdm

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
        image_tag = image_divs.find_all('img')
        for image in image_tag:
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
        print("Error occurred during scraping:", str(e))

csv_filename = "product_links.csv"
output_file = "out.csv"
data_list = []

with open(csv_filename, 'r') as file:
    reader = csv.DictReader(file)
    total_rows = sum(1 for _ in reader)  # Count total rows for progress bar
    file.seek(0)  # Reset file pointer to the beginning
    reader.__next__()

    for row in tqdm(reader, desc="Scraping products", total=total_rows-1, unit="product"):
        product_link = row['Product Links']
        result_dict = scrape_product_info(product_link)
        data_list.append(result_dict)

if data_list:  # Ensure data_list is not empty before accessing keys
    header = data_list[0].keys()

    with open(output_file, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=header)
        writer.writeheader()
        try:
            writer.writerows(data_list)
        except Exception as e:
            print(e)
else:
    print("No data to write.")
