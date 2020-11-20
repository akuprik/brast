"""
согласно подписок получает сообщения от ЦКС сервера и рассылает клиентам телеги
"""
from ckts_api import get_tlgs
from b_client import Tlg
from b_db import CktsBotDB
from b_telega import TBot
from b_constants import TELEGA_TOKEN


def main():
    db = CktsBotDB()
    bot = TBot(TELEGA_TOKEN)
    clients = db.get_clients()
    for client in clients:
        regs = db.get_register_list(client)
        pults = []
        telegafio = bot.get_fio_from_telega_chat(client.telega_id)
        for reg in regs:
            if reg.valid > 0:
                pults.append(reg.pult)

        filters = []
        flt_list = db.get_filters_for_client(client.client_id)
        for filter in flt_list:
            filters.append(f"{filter.filter_address}:{filter.filter_text}")

        if len(pults) > 0 and len(filters) > 0:
            result = get_tlgs(client.telega_id,
                              telegafio,
                              pults,
                              filters,
                              ).get('tlg_list')
            for item in result.values():
                tlg = Tlg(item)
                bot.send_message(client.telega_id, str(tlg))
                print(tlg)




if __name__ == '__main__':
    main()
