import requests
from bs4 import BeautifulSoup

url = 'http://books.toscrape.com'

response = requests.get(url, timeout=10)
bs = BeautifulSoup(response.content , 'html.parser')

books = bs.find_all('article', class_='product_pod')
print(f"Found {len(books)} books on the page. Here are their titles:\n")

for book in books:
    title = book.h3.a['title']
    print(title)