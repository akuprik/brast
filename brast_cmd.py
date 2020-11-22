from pprint import pprint
import os
import re

import logs
import b_telega
from b_constants import TELEGA_TOKEN


log = logs.Logger(log_level=logs.DEBUG)

bot = b_telega.TBot(TELEGA_TOKEN)


@bot.message_handler(commands=['start', 'help',
                               'reg', 'unreg', 'reglist',
                               'unreglist', 'clients', 'delclient',
                               'reglistall', 'valid', 'unvalid',
                               'snd',
                               'filter', 'unfilter', 'filterlist',
                               ])
def h_command(message):
    try:
        cmd = re.findall('/(\w*)', message.text.lower())[0]
    except:
        bot.send_message(message.chat.id, 'не верный формат, попробуй /help',
                         confirm_client=False)
        return
    msg = getattr(bot, f"handler_{cmd}")(message)
    bot.send_message(message.chat.id, msg)


@bot.message_handler(commands=['details',
                               'filters',
                               'registrations',
                               'filters'
                               ])
def h_details_all(message):
    msg = bot.handler_details(message)
    bot.send_message(message.chat.id, msg)

@bot.message_handler()
def h_all(message):
    #pprint(message.json)
    log.debug(message.json)
    bot.send_message(message.chat.id,
                     f'Неопознанная команда {message.text}\nпопробуй /help')


def main():
    log.info(f"Start bot {__file__.upper()}")
    bot.polling(b_telega.POLLING_INTERVAL)
    log.info(f'Finish bot {__file__.upper()}')


if __name__ == '__main__':
    t = os.popen('ps  -C "python" -o pid,command').read().split('\n')
    isDone = False
    for x in t:
        if x.find('brast_cmd.py') > 0:
            if int(x.split()[0]) != int(os.getpid()):
                isDone = True
                log.error('brast_cmd.py уже запущен ранее' )
    if not isDone:
        main()
