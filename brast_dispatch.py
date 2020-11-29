"""
согласно подписок получает сообщения от ЦКС сервера и рассылает клиентам телеги
"""
import os
from time import sleep
from datetime import date, timedelta

import logs
from ckts_api import get_tlgs
from b_client import Tlg
from b_db import CktsBotDB
from b_telega import TBot
from b_constants import (TELEGA_TOKEN, TIMEOUT_DISPATH, TIMEUOT_SLEEP,
                         DAYS_FOR_CONFIRM, DAYS_FOR_DELETE)
from b_help import help_list

log_level = logs.WARNING

log = logs.Logger(log_level=log_level)


def dispatch_tlg(db, bot):
    """
    Рассылка АФТН сообщений и удаление клиента если просрочена активность
    """
    flag = False
    clients = db.get_clients()
    for client in clients:
        if (client.lastdate >=
                str(date.today() - timedelta(days=DAYS_FOR_DELETE))
                or client.sent_info == 0):
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
                    bot.send_message(chat_id=client.telega_id,
                                     text=str(tlg),
                                     confirm_client=False)
                    flag = True
        else:
            log.warning(f"Удаление просроченного клиента {client}")
            db.delete_client(client.client_id)
    return flag


def send_inform_for_confirm(db, bot):
    """
    Разослать клиентам информацию о подтверждении активности
    """
    clients = db.get_clients_for_inform(days=DAYS_FOR_CONFIRM)
    for client in clients:
        bot.send_message(client.telega_id, help_list.get('confirm_message'),
                         confirm_client=False)
        db.set_sent_confirm(client)






def main():
    db = CktsBotDB()
    bot = TBot(TELEGA_TOKEN)
    while True:
        send_inform_for_confirm(db, bot)
        if dispatch_tlg(db, bot):
            sleep(TIMEOUT_DISPATH)
        else:
            sleep(TIMEUOT_SLEEP)



if __name__ == '__main__':
    t = os.popen('ps  -C "python3" -o pid,command').read().split('\n')
    isDone = False
    for x in t:
        if x.find('brast_dispatch.py') > 0:
            if int(x.split()[0]) != int(os.getpid()):
                isDone = True
                log.info('brast_dispatch.py уже запущен ранее')
    if not isDone:
        main()
