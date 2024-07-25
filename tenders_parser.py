from bs4 import BeautifulSoup as bs
from requests import get
from fake_useragent import UserAgent
from json import dump
from urllib3.exceptions import InsecureRequestWarning
from urllib3 import disable_warnings

class Parser:

    def __init__(self):
        self.headers = []
        self.out_data = []
        self.user = UserAgent()

    def __create_hash_table(self, table_data): 
        data = {}
        for num in range(len(self.headers)):
            if num == 0 or num == 2 or num == 5:
                data[self.headers[num]] = table_data[num].text.strip()
            elif num == 1:
                data[self.headers[num]] = table_data[num].text.strip() + table_data[num].find('a').text.strip()
            elif num == 4:
                data[self.headers[num]] = table_data[num].find('span').text.strip()
        return data

    def create_headers(self, headers_parsed):
        for header in headers_parsed:
            self.headers.append(header.text.strip())

    def parse(self, link):
        disable_warnings(InsecureRequestWarning)
        headers = {"user-agent": self.user.random}
        resp = get(link, verify=False, headers=headers)
        if resp.status_code != 200:
            raise WebError(resp.status_code)
        else:
            page = bs(resp.text, "html.parser")
            table = page.find('table')
            headers_parsed = table.find('thead').find("tr").find_all('th')
            if not self.headers:
                self.create_headers(headers_parsed)
            rows = table.find('tbody').find_all('tr')
            if not rows:  # Stop if there are no rows found
                return None
            for row in rows:
                data = row.find_all('td')
                processed_data = self.__create_hash_table(data)
                self.out_data.append(processed_data)
            return self.out_data

class WebError(Exception):
    def __init__(self, code):
        super().__init__()
        self.code = code

    def __str__(self) -> str:
        return f'Ошибка соединения \n Код ошибки: {self.code}'

def main():
    parser = Parser()
    num = 1
    all_data = []
    while True:
        link = f'https://goszakupki.by/tenders/posted?page={num}'
        try:
            data = parser.parse(link)
        except WebError as e:
            print(e)
            break
        
        if not data:
            print(f"No more data found on page {num}. Stopping the scraper.")
            break
        
        all_data.extend(data)
        num += 1
        print(f'Scraped page number {num - 1}.')

    with open('tenders.json', 'w') as f:
        dump(all_data, f, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    main()
