import os
import re

from telebot import TeleBot

import logs
from b_help import help_list
from b_db import CktsBotDB
from ckts_api import test_pult_in_cks
from b_client import Filter

POLLING_INTERVAL = 1
LOG_LEVEL = logs.DEBUG

TEMPLATE_PULT = '(TLG\d{3})'
TEMPLATE_ID = '(\d*)'
TEMPLATE_VALID = '/(VALID|UNVALID|DELCLIENT|CLIENT) (\d*)'
TEMPLATE_FILTER = '/FILTER A:(\w*) T:(.*)'
TEMPLATE_UNFILTER = '/UNFILTER (\d*)'
TEMPLATE_COMMAND ='/(\w*)'
TEMPLATE_SND = '/snd c:(\d*) t:(.*)'
TEMPLATE_ROLE = '/ROLE C:(\d*) R:(\d*)'

log = logs.Logger(log_name='b_telega', log_level=LOG_LEVEL)


class TBot(TeleBot):
    def send_message(self, chat_id, text, disable_web_page_preview=None,
                     reply_to_message_id=None, reply_markup=None,
                     parse_mode=None, disable_notification=None, timeout=None,
                     confirm_client=True,
                     ):
        log.debug(f'send_messsage: {text}')
        if confirm_client:
            db = CktsBotDB()
            db.confirm_client(chat_id)
        try:
            return super().send_message(
                chat_id, text, disable_web_page_preview,
                reply_to_message_id, reply_markup,
                parse_mode, disable_notification, timeout
                )

        except Exception as e:
            log.error(f'{e}')
        return None

    def is_admin(self, telega_id):
        db = CktsBotDB()
        return db.client_is_admin(telega_id)

    def get_fio_from_message(self, message):
        return f'{message.chat.first_name} {message.chat.last_name}'

    def get_fio_from_telega_chat(self, chat_id):
        """
        Запрашивает в телеге данные о пльзователе,
        и возвращает строку Имя Фамилия
        """
        try:
            response = self.get_chat(chat_id)
            return f"{response.first_name} {response.last_name}"
        except Exception as e:
            log.error(
                f'Ошибка получения данных о пользователе {chat_id}\n{e}')
        return 'Имя Фамилия'

    def handler_start(self, message):
        msg = f'Привет {message.chat.first_name} ' \
              f'{message.chat.last_name}, запустились!\n' \
              f'Это система БРАСТ. Попробуй /help'
        return msg

    def handler_help(self, message):
        msg = (f'{message.chat.first_name} '
               f'{message.chat.last_name}!\n{help_list["begin_message"]}\n'
               )
        if self.is_admin(message.chat.id):
            msg += help_list['admin_commands']
        return msg

    def get_pult_from_message(self, message, command):
        try:
            pult = re.findall(f"/{command.upper()} {TEMPLATE_PULT}",
                              message.text.upper())[0]
        except Exception as e:
            log.warning(f'Ошибка определения пульта\n{message.json}\n{str(e)}')
            return (None,
                    f"Укажите правильно пульт\n"
                    f"/{command} TLGXXX , где XXX номер Вашего пульта"
                    )
        return (pult, None)

    def handler_reg(self, message):
        pult, msg = self.get_pult_from_message(message, 'reg')
        if not pult:
            return msg
        try:
            pult_decription = test_pult_in_cks(pult)
            if len(pult) == 0:
                return f"Пульт {pult} в ЦКС не описан."
            db = CktsBotDB()
            client = db.get_create_client(message.chat.id)  # получим клиента
            log.debug(f"handler_reg: client = {client}")
            client_pult = db.register_pult(client, pult)  # создадим регистрацию
            if client_pult.valid == 0:  # отправим сообщение админам
                admin_list = db.get_admins()
                for admin in admin_list:
                    msg = (
                            f'Надо подтвердить регистрацию для:\n' 
                            f'{self.get_fio_from_message(message)}\n'
                            f"{pult_decription.get('client_name')}\n"
                            f"пульт {client_pult.str_for_client()}\n"
                            f'{help_list.get("admin_commands")}'
                          )
                    self.send_message(admin.telega_id, msg)
            return (f"регистрация пульта {pult} "
                    f"для получения телеграмм\n"
                    f"{self.get_fio_from_message(message)}\n"
                    f"client_id = {client_pult.client_id}\n"
                    f"telegram_id = {client.telega_id}\n"
                    f"pult = {client_pult.str_for_client()}\n"
                    )
        except Exception as e:
            log.warning(f"Ошибка при регистрации пульта\n"
                        f"{str(e)}\n"
                        f"{message.json}")
            return 'Ошибка при регистрации'

    def handler_unreg(self, message):
        """
        Удаление регистрации пульта у клиента
        """
        pult, msg = self.get_pult_from_message(message, 'unreg')
        if not pult:
            return msg
        db = CktsBotDB()
        client = db.get_create_client(message.chat.id)  # получим клиента
        log.debug(f"handler_unreg: client = {client}")
        if client:
            if db.unregister_pult(client, pult) > 0:
                return (f'регистрация для {self.get_fio_from_message(message)}:' 
                        f'\n{client.telega_id} - {pult}\n'
                        f'ОТМЕНЕНА'
                        )
        return 'Ошибка при отмене регистрации'

    def handler_reglist(self, message):
        """
        Формирует список регистраций клиенту
        """
        msg = f'Список регистраций для {self.get_fio_from_message(message)}:\n'
        lst = 'пуст'
        db = CktsBotDB()
        client = db.get_telega_client(message.chat.id)
        log.debug(f"handler_reglisit: client = {client}")
        if client:
            reglist = db.get_register_list(client)
            if len(reglist) > 0:
                lst = ''
                for reg in reglist:
                    lst += f'{reg.str_for_client()}\n'
        return f'{msg}{lst}'

    def handler_unreglist(self, message):
        """
        Формирует список не подтвержденных регистраций
        для администратора
        """
        lst = ''
        if self.is_admin(message.chat.id):
            db = CktsBotDB()
            unreg_list = db.get_regs_not_valid()
            for reg in unreg_list:
                s = (f'{reg.id}/'
                     f'{self.get_fio_from_telega_chat(reg.telega_id)}/'
                     f'{reg.str_for_admin()} \n'
                     )
                if lst == '':
                    lst = s
                else:
                    lst += s
            return lst if lst != '' else 'пусто\n'
        return 'Нет доступа'

    def handler_reglistall(self, message):
        """
        Формирует список всех регистраций
        для администратора
        """
        lst = ''
        if self.is_admin(message.chat.id):
            db = CktsBotDB()
            unreg_list = db.get_regs_all ()
            for reg in unreg_list:
                s = (f'{reg.id}/'
                     f'{self.get_fio_from_telega_chat(reg.telega_id)}/'
                     f'{reg.str_for_admin()} \n'
                     )
                if lst == '':
                    lst = s
                else:
                    lst += s
            return lst if lst != '' else 'пусто\n'
        return 'Нет доступа'


    def handler_clients(self, message):
        """
        список клиентов админу
        """
        lst = ''
        if self.is_admin(message.chat.id):
            db = CktsBotDB()
            clients = db.get_clients()
            log.debug(f"handler_clients: {clients}")
            if clients:
                for client in clients:
                    lst += (f'{self.get_fio_from_telega_chat(client.telega_id)}'
                            f' {client}\n'
                            )
            return lst if lst != '' else 'Список клиентов пуст'
        return "Нет доступа"

    def handler_delclient(self, message):
        if self.is_admin(message.chat.id):
            cmd, client_id = '', ''
            try:
                cmd, client_id = re.findall(TEMPLATE_VALID,
                                         message.text.upper(),
                                         )[0]
            except Exception as e:
                log.info(f"handler_del_client: ошибка команды {message.text}\n"
                         f" {str(e)}")

            if not (cmd != '' and client_id != ''):
                return (f'Ошибка формата\n'
                        f'{help_list.get("admin_commands")}'
                        )
            db = CktsBotDB()
            if db.delete_client(client_id):
                return f"Клиент client_id:{client_id} УДАЛЕН"
            return f'Ошибка удаления клиента client_id:{client_id}'
        else:
            return "Нет доступа"

    def handler_set_valid(self, message):
        """
        Подтверждает/отменяет регистрацию
        """
        cmd, reg_id = ('', '')
        try:
            cmd, reg_id = re.findall(TEMPLATE_VALID, message.text.upper())[0]
        except Exception as e:
            log.info(f"handler_set_valid: {str(e)} "
                     f"Не верный формат команды. {message.text}")

        if not (cmd != '' and reg_id != ''):
            return (f'Ошибка формата\n'
                    f'{help_list.get("admin_commands")}'
                    )
        if self.is_admin(message.chat.id):
            db = CktsBotDB()
            reg = db.set_valid_reg(reg_id, cmd == 'VALID')
            return (f'{reg.id}/'
                    f'{self.get_fio_from_telega_chat(reg.telega_id)}/'
                    f'{reg.str_for_client()}'
                    ) if reg else 'Ошибка регистрации'
        return 'Нет доступа'

    def handler_valid(self, message):
        return self.handler_set_valid(message)

    def handler_unvalid(self, message):
        return self.handler_set_valid(message)


    def handler_filterlist(self, message):
        """
        Возвращает список фльтров клиента
        """
        filters = ''
        db = CktsBotDB()
        client = db.get_telega_client(message.chat.id)
        if client:
            filter_list = db.get_filters_for_client(client.client_id)
            for filter in filter_list:
                filters += f'{filter}\n'
        return (filters
                if filters != ''
                else ('Список пуст, для получения всех телеграмм:\n'
                      '/filter a: t:\n' 
                      'или определите фильтер:\n'
                      ' a:<маска адреса отправителя> например a:УУВВ\n' 
                      ' t:<фрагмент текста> например t:ЮТ444\n'
                      )
                )

    def handler_filter(self, message):
        """
        Добавляет фильтр
        """
        try:
            #print(TEMPLATE_FILTER)
            #print(message.text.upper())
            #print(re.findall(TEMPLATE_FILTER, message.text.upper()))
            filter_address, filter_text = re.findall(TEMPLATE_FILTER,
                                                     message.text.upper(),
                                                     )[0]
        except Exception as e:
            log.info(f"handler_filter: Неверный формат\n"
                     f"{str(e)}\n"
                     f"{message.json}")
            return 'Не верно указаны параметры'

        db = CktsBotDB()
        client = db.get_telega_client(message.chat.id)
        if client:
            filter = Filter(0, client.client_id, filter_address, filter_text)
            filter = db.create_edit_filter(filter)
            if filter:
                return f'Добавлен фильтер\n{filter}\n' \
                       f'для получения списка /filterlist'
        return 'Ошибка добаления фильтра'

    def handler_unfilter(self, message):
        try:
            #print(TEMPLATE_UNFILTER)
            #print(message.text.upper())
            filter_id = re.findall(TEMPLATE_UNFILTER, message.text.upper())[0]
        except:
            return 'Не верный формат\nПопробуй /help'
        if filter_id != '':
            db = CktsBotDB()
            filter = db.get_filter_by_id(filter_id)
            client = db.get_telega_client(message.chat.id)
            if filter:
                if filter.client_id == client.client_id:
                    db.delete_filter(filter)
                    return str(
                        f"Удален фильтр:\n{filter}\n"
                        f"Для просмотра списка фильтров /filterlist"
                    )
        return 'Не верный ID'

    def handler_details(self, message):
        file = f"./details/{re.findall(TEMPLATE_COMMAND, message.text)[0]}.txt"
        if os.path.exists(file):
            f = open(file, 'r')
            msg = f.read()
            f.close()
        else:
            msg = 'Информация пока не подготовлена'
            log.warning(f"handler_details: файл не найден {file}")
        return msg

    def handler_snd(self, message):
        try:
            client_id, text = re.findall(TEMPLATE_SND,
                                         message.text,
                                        )[0]
        except Exception as e:
            log.info(f"handler_snd: Неверный формат\n"
                     f"{str(e)}\n"
                     f"{message.json}")
            return 'Неверно указаны параметры'

        db = CktsBotDB()
        client = db.get_client_by_id(client_id)
        if client:
            self.send_message(client.telega_id, f"ОТ АДМИНА:\n{text}",
                              confirm_client=False)
            return f"Отправлено {client.telega_id}"
        return f"Клиент {client_id} не найден."

    def handler_fltall(self, message):
        """
        Возвращает для администратора список фильтров для всех клиентов
        """
        if self.is_admin(message.chat.id):
            filters = ''
            db = CktsBotDB()
            filter_list = db.get_filters_for_client()
            for filter in filter_list:
                filters += f'{filter}\n'
            return (filters
                    if filters != ''
                    else 'Список пуст')
        else:
            return "Нет доступа"

    def handler_client(self, message):
        """
        Возвращает данные по клиенту
        """
        if self.is_admin(message.chat.id):
            cmd, client_id = ('', '')
            try:
                cmd, client_id = re.findall(TEMPLATE_VALID, message.text.upper())[
                    0]
            except Exception as e:
                log.info(f"handler_client: {str(e)} "
                         f"Не верный формат команды. {message.text}")

            if not (cmd != '' and client_id != ''):
                return (f'Ошибка формата\n'
                        f'{help_list.get("admin_commands")}'
                        )
            db = CktsBotDB()
            client = db.get_client_by_id(client_id)
            if client is None:
                return f"client_id = {client_id} не найден"
            msg = (f'{self.get_fio_from_telega_chat(client.telega_id)}'
                   f' {client}\n'
                   )
            regs = db.get_register_list(client)
            msg += 'Регистрации:\n'
            for reg in regs:
                msg += f"{reg.str_for_admin()}\n"
            filters = db.get_filters_for_client(client.client_id)
            msg += "Фильтры:\n"
            for filter in filters:
                msg += f'{filter}\n'

            return msg
        else:
            return "Нет доступа"

    def handler_role(self, message):
        """
        изменяет роль клиенту клиенту
        """
        if self.is_admin(message.chat.id):
            client_id, role = ('', '')
            try:
                client_id, role = re.findall(TEMPLATE_ROLE,
                                             message.text.upper())[0]
            except Exception as e:
                log.info(f"handler_client: {str(e)} "
                         f"Не верный формат команды. {message.text}")

            if not (str(client_id) != '' and str(role) != ''):
                return (f'Ошибка формата\n'
                        f'{help_list.get("admin_commands")}'
                        )
            db = CktsBotDB()
            client = db.get_client_by_id(client_id)
            if client is None:
                return f"client_id = {client_id} не найден"
            if role not in ['1', '2']:
                return f"Роль должна быть {[1, 2]}"
            msg = f"Установили роль {role}" if db.set_role(client_id,
                                                           role) else f"Ошибка"
            return msg
        else:
            return "Нет доступа"
