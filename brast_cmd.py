from pprint import pprint
import logs
import b_telega
from b_constants import TELEGA_TOKEN


log = logs.Logger(log_level=logs.DEBUG)

bot = b_telega.TBot(TELEGA_TOKEN)


@bot.message_handler(commands=['start'])
def h_start(message):
    msg = bot.handler_start(message)
    bot.send_message(message.chat.id, msg)


@bot.message_handler(commands=['help'])
def h_help(message):
    msg = bot.handler_help(message)
    bot.send_message(message.chat.id, msg)


@bot.message_handler(commands=['reg'])
def h_reg(message):
    msg = bot.handler_reg(message)
    bot.send_message(message.chat.id, msg)


@bot.message_handler(commands=['unreg'])
def h_unreg(message):
    msg = bot.handler_unreg(message)
    bot.send_message(message.chat.id, msg)


@bot.message_handler(commands=['reglist'])
def h_reglist(message):
    msg = bot.handler_reglist(message)
    bot.send_message(message.chat.id, msg)


@bot.message_handler(commands=['unreglist'])
def h_unreglist(message):
    msg = bot.handler_unreglist(message)
    bot.send_message(message.chat.id, msg)


@bot.message_handler(commands=['clients'])
def h_clients(message):
    msg = bot.handler_clients(message)
    bot.send_message(message.chat.id, msg)

@bot.message_handler(commands=['delclient'])
def h_clients(message):
    msg = bot.handler_delclient(message)
    bot.send_message(message.chat.id, msg)


@bot.message_handler(commands=['valid', 'unvalid'])
def h_set_valid(message):
    msg = bot.handler_set_valid(message)
    bot.send_message(message.chat.id, msg)


@bot.message_handler(commands=['filterlist'])
def h_flterlist(message):
    msg = bot.handler_filterlist(message)
    bot.send_message(message.chat.id, msg)


@bot.message_handler(commands=['filter'])
def h_flter(message):
    msg = bot.handler_filter(message)
    bot.send_message(message.chat.id, msg)


@bot.message_handler(commands=['unfilter'])
def h_filter(message):
    msg = bot.handler_unfilter(message)
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
    pprint(message.json)
    log.debug(message.json)
    bot.send_message(message.chat.id,
                     f'Неопознаная команда {message.text}\nпопробуй /help')


def main():
    log.info(f"Start bot {__file__.upper()}")
    bot.polling(b_telega.POLLING_INTERVAL)
    log.info(f'Finish bot {__file__.upper()}')


if __name__ == '__main__':
    main()
