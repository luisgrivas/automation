import hashlib
import os
import requests
from bs4 import BeautifulSoup


def get_pdf_links(url: str) -> list:
    r = requests.get(url)
    links = []
    if r.ok:
        soup = BeautifulSoup(r.content, 'html.parser')
        for a in soup.find_all('a'):
            if a.get('href').lower().endswith('pdf'):
                links.append(a)
    return links


def filter_pdf_list(pdf_list: list) -> list:
    filtered_list = []
    for link in pdf_list:
        file_name, link_text = link.get('href'), link.text
        if 'convocatoria' in file_name.lower() or 'convocatoria' in link_text.lower():
            filtered_list.append(file_name)
    return filtered_list


def get_pdf_content(pdf_link: str) -> bytes:
    r = requests.get(pdf_link)
    if r.ok and 'pdf' in r.headers.get('content-type', ''):
        return r.content
    else:
        return bytes()


def check_pdf_updates(pdf_content_list: list, md5_list: list) -> bool:
    if len(pdf_content_list) != len(md5_list):
        return True
    pdf_md5_list = [
        hashlib.md5(pdf_content).hexdigest() for pdf_content in pdf_content_list
    ]
    return set(pdf_md5_list) != set(md5_list)


def main(url: str, file_name: str):
    links = get_pdf_links(url)
    filtered_links = filter_pdf_list(links)
    pdf_content_list = []
    for link in filtered_links:
        if pdf_content := get_pdf_content(link):
            pdf_content_list.append(pdf_content)
    if not os.path.exists(file_name):
        md5_list = [
            hashlib.md5(pdf_content).hexdigest() for pdf_content in pdf_content_list
        ]
        f = open(file_name, 'w')
        for md5_str in md5_list:
            f.write(f'{md5_str}\n')
        f.close()
        return False
    else:
        md5_list = []
        f = open(file_name, 'r')
        for line in f.readlines():
            md5_list.append(line.strip())
        f.close()
        return check_pdf_updates(pdf_content_list, md5_list)


if __name__ == '__main__':
    import os
    from dotenv import load_dotenv

    load_dotenv()
    url = os.getenv('UNAM_URL')
    assert url is not None
    print(main(url, 'md5_list.txt'))
