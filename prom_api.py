import json
import http.client
import telebot
import schedule
from auth_data import token

# API Settigs
AUTH_TOKEN = '8ee819034a9e9ee1ac046021a4b7d46f5cacd687'  # Your authorization token
HOST = 'my.prom.ua'  # e.g.: my.prom.ua, my.tiu.ru, my.satu.kz, my.deal.by, my.prom.md


class HTTPError(Exception):
    pass


class EvoClientExample(object):

    def __init__(self, token):
        self.token = token

    def make_request(self, method, url, body=None):
        connection = http.client.HTTPSConnection(HOST)

        headers = {'Authorization': 'Bearer {}'.format(self.token),
                   'Content-type': 'application/json'}
        if body:
            body = json.dumps(body)

        connection.request(method, url, body=body, headers=headers)
        response = connection.getresponse()
        if response.status != 200:
            raise HTTPError('{}: {}'.format(response.status, response.reason))

        response_data = response.read()
        return json.loads(response_data.decode())

    def get_order_list(self):
        url = '/api/v1/orders/list'
        method = 'GET'

        return self.make_request(method, url)

    def get_order(self, order_id):
        url = '/api/v1/orders/{id}'
        method = 'GET'

        return self.make_request(method, url.format(id=order_id))

    def set_order_status(self, status, ids, cancellation_reason=None, cancellation_text=None):
        url = '/api/v1/orders/set_status'
        method = 'POST'

        body = {
            'status': status,
            'ids': ids
        }
        if cancellation_reason:
            body['cancellation_reason'] = cancellation_reason

        if cancellation_text:
            body['cancellation_text'] = cancellation_text

        return self.make_request(method, url, body)

    def set_import_file(self, string_binary):
        url = '/api/v1/products/import_file'
        method = 'POST'

        file = open("final.xml", "rb")
        string_binary = file.read()
        file.close()

        body = {
            "file": f'{string_binary}',
            "data": {
                "force_update": True,
                "only_available": True,
                "mark_missing_product_as": "none",
                "updated_fields": [
                    "price",
                    "presence"
                ]
            }
        }
        return self.make_request(method, url, body)


def main():

    # Initialize Client
    if not AUTH_TOKEN:
        raise Exception('Sorry, there\'s no any AUTH_TOKEN!')

    api_example = EvoClientExample(AUTH_TOKEN)

    # import_file_response = api_example.set_import_file("")
    order_list = api_example.get_order_list()
    if not order_list['orders']:
        raise Exception('Sorry, there\'s no any order!')
    else:
        for order in order_list['orders']:
            product_name = ''
            status = order['status_name']
            if status == 'Новый':
                print(order)
                name_phone = order['client_first_name'] + ' ' + order['client_last_name'] + '\n' + order['phone'] \
                             + '\n' + order['client_notes'] \
                             + '\ndelivery_address - ' + order.get('delivery_address') + '\n'
                for product in order['products']:
                    product_name = product_name + '\nname - ' + product['name'] \
                                   + '\nsku - ' + product['sku'] \
                                   + '\nid - ' + product['external_id'] \
                                   + '\nprice - ' + product['price'] \
                                   + '\npartner_link - ' + product.get('url_link', '""') + '\n' + product['url'] + '\n'
                print(str(name_phone + product_name))
                telegram_bot(str(name_phone + product_name))

    # # Order example data. Requred to be setup to get example work
    # order_id = order_list['orders'][0]['id']
    # order_ids = [order_id]
    # status = 'received'
    #
    # Setting order status
    # pprint.pprint(api_example.set_order_status(status=status, ids=order_ids))
    #
    # # # Getting order by id
    # pprint.pprint(api_example.get_order(order_id))


def telegram_bot(order):
    bot = telebot.TeleBot(token)
    file = open('bot_id.txt', 'r')
    list = file.read().split()

    for user_id in list:
        try:
            bot.send_message(
                user_id,
                order
            )

        except Exception as ex:
            print(ex)
            bot.send_message(
                user_id,
                "Error send order: " + order
            )

    bot.polling()


def go_run():
    # schedule.every(15).minutes.do(main)
    schedule.every(10).seconds.do(main)

    while True:
        schedule.run_pending()


if __name__ == '__main__':
    main()
