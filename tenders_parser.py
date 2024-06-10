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
        assert len(self.headers) == len(table_data)
        data = {}
        for num in len(self.headers):
            match num:
                case 0 | 2 | 4 | 5:
                    data[self.headers[num]] = table_data[num].text
                case 1:
                    data[self.headers[num]] = table_data[num].text + table_data[num].find('a').text
                case 4:
                    data[self.headers[num]] = table_data[num].find('span').text
        return data

    def create_headers(self, headers_parsed):
        for n, header in enumerate(headers_parsed):
            if n == 1:
                self.headers.append(header.text)
            else:
                self.headers.append(header.find('a').text)

    def parse(self, link):
        disable_warnings(InsecureRequestWarning)
        headers = {"useragent": self.user.random}
        resp = get(link, verify=False, headers=headers)
        if resp.status_code != 200:
            return 0
        else:
            page = bs(resp.text)
            table = page.find('table')
            headers_parsed = map(lambda x: x[1].find('a').text if x[0] != 1 else x.text, map(list(), enumerate()))
            self.create_headers(headers_parsed)
            rows = table.find('tbody').find_all('tr')
            for row in rows:
                data = row.find_all('td')
                processed_data = self.__create_hash_table(data)
                self.out_data.append(processed_data)
            return self.out_data


def main():
    parser = Parser()
    num = 1
    while True:
        link = f'https://goszakupki.by/tenders/posted?page={num}'
        out_data = []
        data = parser.parse(link)
        if data != 0:
            out_data.extend(data)
            with open('tenders.json', 'w') as f:
                dump(out_data, f)
        num += 1


if __name__ == '__main__':
    main()
