import requests
import schedule
import xmltodict
import json
from datetime import datetime


class CreateOneFileForUploadToProm:

    def __init__(self, dict_with_links):
        self.dict_links = dict_with_links
        self.list_save_dict = []

    def run_convert(self):

        for name_file, value_link in self.dict_links.items():
            self.save_link_to_file_xml(name_file, value_link)

            self.list_save_dict.append(self.convert_file_xml_to_file_json(name_file))

        one_file_json = self.create_one_file_json()

        self.convert_json_to_xml(one_file_json)

    def save_link_to_file_xml(self, kay_name, value_link):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/50.0.2661.102 Safari/537.36',
            'Content-Type': 'application/xml'
        }

        file = 'links/' + str(kay_name) + '.xml'
        file_xml = open(file, 'wb')
        ufr = requests.get(value_link, headers=headers)
        file_xml.write(ufr.content)
        file_xml.close()

    def create_one_file_json(self):

        list_categories = []
        list_product = []

        for list_item in self.list_save_dict:
            for category in list_item['shop']['categories']['category']:
                list_categories.append(category)
            if not list_item['shop'].get('offers') == None:
                for offer in list_item['shop']['offers']['offer']:
                    if offer.get("@available") == 'true':
                        d = {'url_link': list_item['shop']['url_link']}
                        offer.update(d)
                        list_product.append(offer)
            elif not list_item['shop'].get('items') == None:
                for offer in list_item['shop']['items']['offer']:
                    if offer.get("@available") == 'true':
                        d = {'url_link': list_item['shop']['url_link']}
                        offer.update(d)
                        list_product.append(offer)
        now = datetime.now()
        dt_string = now.strftime("%d-%m-%Y %H:%M:%S")
        dict_default = {
            "yml_catalog": {
                "@date": dt_string,
                "shop": {
                    "name": "Atlantida",
                    "company": "Atlantida",
                    "url": "https://www.atlantida.com.ua/",
                    "currencies": {
                        "currency": {
                            "@id": "UAH",
                            "@rate": "1"
                        }
                    },
                    "categories": {
                        "category": list_categories
                    },
                    "offers": {
                        "offer": list_product
                    }
                }
            }
        }

        print(len(list_product))
        print(len(list_categories))

        file = 'json_default.json'
        file_json = open(file, 'w')
        json.dump(dict_default, file_json, indent=2, ensure_ascii=False)
        file_json.close()
        return file

    def convert_file_xml_to_file_json(self, name_file):
        f = open('links/' + name_file + '.xml')
        d = xmltodict.parse(f.read().encode('utf-8'))
        f.close()
        # tmp = d['yml_catalog']['shop']['offers']
        tmp = d['yml_catalog']
        file = 'links/' + str(name_file) + '.json'
        file_json = open(file, 'w')
        json.dump(tmp, file_json, indent=2, ensure_ascii=False)
        file_json.close()
        d = {'url_link': name_file}
        tmp['shop'].update(d)

        return tmp

    def convert_json_to_xml(self, file):

        file_json = open(file, 'r')
        sample_json = json.load(file_json)
        file_xml = open('final.xml', 'w')
        xml = xmltodict.unparse(sample_json, full_document=False)
        file_xml.write(xml)
        file_xml.close()


def main():
    dict_links = {
        'internet-magazin-cs3669299.prom.ua': 'https://internet-magazin-cs3669299.prom.ua/yandex_market.xml?hash_tag=1d4aa8511f07589cbd6a84d4ac643018'
                                              '&sales_notes=&product_ids=&label_ids=&exclude_fields=&html_description=1&yandex_cpa=&process_presence_sure='
                                              '&languages=ru&group_ids=104885799%2C104885800%2C104885803%2C104885805%2C104885806%2C104885807%2C104885808%2C104'
                                              '885810%2C104885811%2C104885809%2C104885812%2C104885813%2C104885814%2C104885815%2C104885816%2C104885817%2C1048858'
                                              '18%2C104885819&nested_group_ids=104885803%2C104885818',
        '7dreamsport.ua': 'https://7dreamsport.ua/universalxml/86750e5c-3729-4b8a-9f30-3468b108f1a8.xml',
        'websklad.biz.ua': 'https://www.websklad.biz.ua/wp-content/uploads/current-Vse-tovary-xml-prom.xml',
        'distributions.com.ua': 'https://distributions.com.ua/user_downloads/f3e7359aca5c2825c0e1cc0e3525360b/content-gen/content_prom_yml.xml'
    }

    run_convert = CreateOneFileForUploadToProm(dict_links)
    run_convert.run_convert()


def go_run():
    schedule.every(4).hours.do(main)

    while True:
        schedule.run_pending()


if __name__ == '__main__':
    go_run()
