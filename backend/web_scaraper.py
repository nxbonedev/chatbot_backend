from bs4 import BeautifulSoup
import requests

@staticmethod
def cleanhtml(html:str)->str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script","style","nav","footer","header"]):
        tag.decompose()

    return soup.get_text(
        separator="\n",
        strip=True
    )