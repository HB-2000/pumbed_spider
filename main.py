from os.path import exists

from lxml import html
from time import sleep
import random
import json

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options

from webdriver_manager.chrome import ChromeDriverManager

xpaths = {
    "links":
        '//*[@id="search-results"]/section/div/div/article/div/div/a/@href',

    'citation_title': '/html/head/meta[@name="citation_title"]/@content',
    'citation_authors': '/html/head/meta[@name="citation_authors"]/@content',
    'citation_date': '/html/head/meta[@name="citation_date"]/@content',
    'citation_publisher': '/html/head/meta[@name="citation_publisher"]/@content',
    'citation_journal_title': '/html/head/meta[@name="citation_journal_title"]/@content',
    'citation_pmid': '/html/head/meta[@name="citation_pmid"]/@content',
    'citation_doi': '/html/head/meta[@name="citation_doi"]/@content',
    'citation_issn': '/html/head/meta[@name="citation_issn"]/@content',
    'keywords': '/html/body/div[5]/main/div[2]/p/text()',
    'abstract': '//*[@id="eng-abstract"]/p/text()',

}
home_link = "https://pubmed.ncbi.nlm.nih.gov"

MAX_PAGE = 1000


def get_element_data(tree, xpath):
    elements = tree.xpath(xpath)
    if len(elements) == 0:
        return ''
    elements = "".join(elements)
    return elements.strip()


def get_page_data(page_link, browser):
    browser.get(page_link)

    tree = html.fromstring(browser.page_source)

    citation_title = get_element_data(tree, xpaths["citation_title"])
    citation_authors = get_element_data(tree, xpaths["citation_authors"])
    citation_date = get_element_data(tree, xpaths["citation_date"])
    citation_publisher = get_element_data(tree, xpaths["citation_publisher"])
    citation_journal_title = get_element_data(tree, xpaths["citation_journal_title"])
    citation_pmid = get_element_data(tree, xpaths["citation_pmid"])
    citation_doi = get_element_data(tree, xpaths["citation_doi"])
    citation_issn = get_element_data(tree, xpaths["citation_issn"])
    keywords = get_element_data(tree, xpaths["keywords"])
    abstract = get_element_data(tree, xpaths["abstract"])

    article = {
        "citation_title": f"{citation_title}",
        "citation_authors": f"{citation_authors}",
        "citation_date": f"{citation_date}",
        "citation_publisher": f"{citation_publisher}",
        "citation_journal_title": f"{citation_journal_title}",
        "citation_pmid": f"{citation_pmid}",
        "citation_doi": f"{citation_doi}",
        "citation_issn": f"{citation_issn}",
        "keywords": f"{keywords}",
        "abstract": f"{abstract}",

    }

    return article


def delay(min_sec, max_sec=None):
    if max_sec is None:
        max_sec = min_sec
    sleep(random.randint(min_sec, max_sec + 1))


def get_page_links(link, browser):
    browser.get(link)
    # request = requests.get(link)
    tree = html.fromstring(browser.page_source)
    links_elements = tree.xpath(xpaths['links'])
    links_elements = list(map(lambda x: home_link + x, links_elements))
    return links_elements


def get_browser_options():
    options = Options()
    options.add_argument("start-maximized")
    options.add_argument("disable-infobars")
    options.add_argument("--disable-extensions")
    return options


def main():
    options = get_browser_options()
    prefs = {"profile.managed_default_content_settings.images": 2}
    options.add_experimental_option("prefs", prefs)

    browser = webdriver.Chrome(options=options, service=ChromeService(ChromeDriverManager().install()))

    term = "brain"
    link = f"https://pubmed.ncbi.nlm.nih.gov/?term={term}"

    for i in range(1, MAX_PAGE + 1):
        next_page = link + f"&page={i}"
        page_links = get_page_links(next_page, browser)
        if not page_links:
            break

        for page_link in page_links:
            file_name = f"{page_link.split('/')[3]}.json"
            if not exists(file_name):
                data = get_page_data(page_link, browser)
                with open(file_name, "w") as outfile:
                    json.dump(data, outfile)
        delay(1, 2)


if __name__ == '__main__':
    main()
