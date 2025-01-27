import requests
from bs4 import BeautifulSoup
import re
import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

ENGINE_BASE = "https://baresearch.org/search?q="  # Base URL for the search engine
PAGE_TIMEOUT = 10  # Maximum wait time (in seconds) for a page to load
MAX_CHARACTERS = 2000  # Maximum number of characters to extract from a web page

def get_web_page_selenium(url):
    """
    Fetch a web page using Selenium.
    
    Args:
        url (str): The URL of the web page to retrieve.

    Returns:
        str: The page source HTML as a string, or None if an error occurs.
    """
    print(f"\nFetching page: {url}")
    if not url:
        raise ValueError("Invalid URL provided.")

    start_time = time.time()  # Measure time taken to load the page

    # Configure Selenium options
    options = Options()
    options.add_argument("--headless=new")  # Run browser in headless mode
    options.add_argument("--memory-model-cache-size-mb=512")
    options.add_argument("--enable-javascript")

    # Rotate user agents for added anonymity
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "AppleWebKit/537.36 (KHTML, like Gecko)",
        "Chrome/92.0.4515.107 Safari/537.36"
    ]
    options.add_argument(f"user-agent={user_agents[0]}")

    driver = webdriver.Chrome(options=options)  # Initialize the Selenium driver
    page_source = None

    try:
        driver.get(url)

        # Wait for the page to fully load
        for _ in range(3):
            try:
                WebDriverWait(driver, PAGE_TIMEOUT).until(
                    lambda d: d.execute_script("return document.readyState") == "complete"
                )
                page_source = driver.page_source
                if page_source:
                    break
            except TimeoutException:
                print("Page load timed out. Retrying...")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.delete_all_cookies()
        driver.quit()

    elapsed_time = time.time() - start_time
    print(f"Time taken to fetch page: {elapsed_time:.4f} seconds")
    return page_source

def query_search_engine(query):
    """
    Query the search engine and return search results.
    
    Args:
        query (str): The search query.

    Returns:
        list: A list of search results with text summaries and URLs, or False if no results.
    """
    url = ENGINE_BASE + query.replace(" ", "+")
    print(f"Search URL: {url}")
    page_source = get_web_page_selenium(url)

    if page_source:
        soup = BeautifulSoup(page_source, "html.parser")
        return extract_results_list(soup)
    return False

def remove_non_ascii(text):
    """
    Remove non-ASCII characters from the input text.

    Args:
        text (str): The input text.

    Returns:
        str: Cleaned text with only ASCII characters.
    """
    return re.sub(r"[^\x00-\x7F]+", "", text)

def remove_excess_spaces(text):
    """
    Remove extra spaces from the input text.

    Args:
        text (str): The input text.

    Returns:
        str: Text with excess spaces removed.
    """
    return re.sub(r"\s{2,}", " ", text)

def extract_text(page_soup, max_chars):
    """
    Extract text content from HTML elements in the soup object.
    
    Args:
        page_soup (BeautifulSoup): Parsed HTML content.
        max_chars (int): Maximum number of characters to extract.

    Returns:
        str: Extracted and cleaned text.
    """
    output = ""
    text_elements = page_soup.find_all(string=True)
    whitelist = ["p", "b", "i", "a", "h1", "h2", "h3", "h4", "h5", "h6", "blockquote", "span"]

    for text in text_elements:
        if text.parent.name in whitelist and len(output) < max_chars:
            output += f"{text} "

    output = remove_non_ascii(output.replace("\n", " ").replace("\r", "").replace("\t", ""))
    return remove_excess_spaces(output)

def extract_results_list(page_soup):
    """
    Extract a list of search results from the soup object.
    
    Args:
        page_soup (BeautifulSoup): Parsed HTML content of the search results page.

    Returns:
        list: A list of dictionaries containing the text and URL of each result.
    """
    articles = page_soup.find_all("article")  # Adjust tag for other search engines
    results = []

    for article in articles:
        uri = article.find("a")["href"]
        text = extract_text(article, 500)
        results.append({"document": text, "uri": uri})

    return results

def get_webpage_text(url):
    """
    Retrieve and extract text content from a web page.
    
    Args:
        url (str): The URL of the web page.

    Returns:
        dict: A dictionary containing the extracted text and the URL.
    """
    source = get_web_page_selenium(url)
    if source:
        soup = BeautifulSoup(source, "html.parser")
        text = extract_text(soup, MAX_CHARACTERS)
    else:
        text = "Error: Unable to retrieve webpage text."

    return {"text": text, "url": url}
