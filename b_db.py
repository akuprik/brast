import sys
import datetime

import sqlite3 as sqlt

import logs
from MyRecordSet import MyRecordSet
import b_client

log_level = logs.DEBUG

log = logs.Logger(log_name='b_db', log_level=log_level)

DB_FILE_NAME = 'ckts_bot_db'


class CktsBotDB:
    def __init__(self):
        self.con = sqlt.connect(DB_FILE_NAME)
        self.cur = self.con.cursor()

    def get_telega_client(self, telega_id):
        self.cur.execute(f"select * from v_clients "
                         f"where telega_id = '{telega_id}'")
        ms = MyRecordSet(self.cur.fetchall(), self.cur.description)
        if len(ms._rows) > 0:
            return b_client.TelegaClient(ms._rows[0][0],
                                         ms._rows[0][1],
                                         ms._rows[0][2],
                                         ms._rows[0][3],
                                         ms._rows[0][4],
                                         ms._rows[0][5],
                                         )
        return None

    def create_edit_client(self, aclient):
        self.cur.execute('select * from clients where id_client = ?',
                         [aclient.client_id])
        ms = MyRecordSet(self.cur.fetchall(), self.cur.description)
        if len(ms._rows) > 0:
            try:
                self.cur.execute(
                    f"update clients set client_type={aclient.client_type}, "
                    f"telega_id='{aclient.telega_id}', "
                    f"last_date='{aclient.lastdate}',"
                    f"sent_inform={aclient.sent_info}"
                    f'where id_client = {aclient.client_id}',
                    )
            except Exception as e:
                se = sys.exc_info()
                log.error(
                    f'Ошибка при изменении клиента в БД \n '
                    f'{str(aclient)} \n'
                    f'{se[1]}\n{se[2].tb_frame.f_code}'
                    )
                return None
            return aclient
        else:
            try:
                self.cur.execute(f"insert into clients "
                                 f"(client_type, telega_id, "
                                 f"lastdate, sent_inform) "
                                 f"values ({aclient.client_type},"
                                 f" '{aclient.telega_id}', "
                                 f"'{aclient.lastdate}',"
                                 f"{aclient.sent_info})"
                                 )
                self.con.commit()
            except Exception as e:
                se = sys.exc_info()
                log.error(
                    f'Ошибка при создании клиента в БД \n '
                    f'{aclient} \n'
                    f'{se[1]}\n{se[2].tb_frame.f_code}'
                    )
                return None
        return self.get_telega_client(aclient.telega_id)

    def register_pult(self, client, pult):
        # проверим есть ли такая пара
        self.cur.execute(f"select * from client_pult "
                         f"where client_id = {client.client_id}"
                         f" and pult = '{pult}'")
        ms = MyRecordSet(self.cur.fetchall(), self.cur.description)
        if len(ms._rows) > 0:
             return b_client.ClientPult(ms._rows[0][0], ms._rows[0][1],
                                           ms._rows[0][2], ms._rows[0][3],
                                           )

        # Создает новую пару
        try:
            self.cur.execute(f"insert into client_pult "
                             f"(client_id, pult) "
                             f"values ({client.client_id}, "
                             f"'{pult}')"
                             )
            self.con.commit()
        except Exception as e:
            se = sys.exc_info()
            log.error(
                f'Ошибка при регистрации пульта  в БД \n '
                f'client_id = {client.client_id} \n'
                f'pult = {pult} \n'
                f'{se[1]}\n{se[2].tb_frame.f_code}'
            )
            return None
        # вернем зарегистрированную пару
        self.cur.execute(f"select * from v_client_pult "
                         f"where client_id ={client.client_id} "
                         f" and pult = '{pult}'")
        ms = MyRecordSet(self.cur.fetchall(), self.cur.description)
        if len(ms._rows) > 0:
                 return b_client.ClientPult(ms._rows[0][0], ms._rows[0][1],
                                            ms._rows[0][2], ms._rows[0][3],
                                            ms._rows[0][4],
                                            )
        return None

    def unregister_pult(self, client, pult):
        try:
            self.cur.execute(f"delete from client_pult "
                             f"where client_id = {client.client_id}"
                             f" and pult = '{pult}'")
            self.con.commit()
        except Exception as e:
            se = sys.exc_info()
            log.error(
                f'Ошибка при отмене регистрации пульта  в БД \n '
                f'client_id = {client.client_id} \n'
                f'pult = {pult} \n'
                f'{se[1]}\n{se[2].tb_frame.f_code}'
            )
            return 0
        return 1

    def get_register_list(self, client):
        reg_list = []
        self.cur.execute(f"select * from v_client_pult "
                         f"where client_id ={client.client_id}")
        ms = MyRecordSet(self.cur.fetchall(), self.cur.description)
        for row in ms._rows:
            #print(row)
            reg_list += [b_client.ClientPult(row[0], row[1], row[2],
                                             row[3], row[4])]
        return reg_list

    def get_admins(self):
        admin_list = []
        self.cur.execute(f"select * from v_clients where client_type = 1")
        ms = MyRecordSet(self.cur.fetchall(), self.cur.description)
        for row in ms._rows:
            admin_list += [b_client.TelegaClient(row[0], row[1],
                                                 row[2], row[3],
                                                 row[4], row[5],
                                                 )]
        return admin_list

    def get_regs_not_valid(self):
        reg_list = []
        self.cur.execute(f"select id, client_id, pult, "
                         f"valid, telega_id  "
                         f"from v_client_pult "
                         f"where valid = 0")
        ms = MyRecordSet(self.cur.fetchall(), self.cur.description)
        for row in ms._rows:
            reg_list += [b_client.ClientPult(row[0], row[1], row[2],
                                                row[3], row[4])]
        return reg_list

    def client_is_admin(self, telega_id):
        client = self.get_telega_client(telega_id)
        if client:
            return client.client_type == 1
        return False

    def get_reg_by_id(self, reg_id):
        """
        Возвращает регистрацию по ID
        """
        self.cur.execute(f"select * from v_client_pult where id ={reg_id} ")
        ms = MyRecordSet(self.cur.fetchall(), self.cur.description)
        if len(ms._rows) > 0:
             return b_client.ClientPult(
                 ms._rows[0][0],
                 ms._rows[0][1],
                 ms._rows[0][2],
                 ms._rows[0][3],
                 ms._rows[0][4],
             )
        return None

    def set_valid_reg(self, reg_id, valid=True):
        try:
            self.cur.execute(f"update client_pult "
                             f" set valid = {1 if valid else 0} "
                             f" where id = {reg_id} "
                             )
            self.con.commit()
            return self.get_reg_by_id(reg_id)
        except Exception as e:
            se = sys.exc_info()
            log.error(
                f'Ошибка при валидации регистрации \n '
                f'id = {reg_id} \n'
                f'{se[1]}\n{se[2].tb_frame.f_code}'
            )
        return None

    def get_clients(self):
        clients = []
        self.cur.execute(f"select * from v_clients")
        ms = MyRecordSet(self.cur.fetchall(), self.cur.description)
        if len(ms._rows) > 0:
             for row in ms._rows:
                clients += [
                    b_client.TelegaClient(
                        row[0],
                        row[1],
                        row[2],
                        row[3],
                        row[4],
                        row[5],
                    )
                    ]
        return clients

    def save_pult_description(self, pult_description):
        try:
            self.cur.execute(f"insert into pults "
                             f"(pult_id, pult_addr, pult_descr) "
                             f"values({pult_description.get('id_client')}, "
                             f"'{pult_description.get('pult')}', "
                             f"'{pult_description.get('client_name')}')"
                             )
            self.con.commit()
        except Exception as e:
            if str(e) == 'UNIQUE constraint failed: pults.pult_id':
                self.con.rollback()
                self.cur.execute(
                    f"update pults "
                    f"set pult_addr = '{pult_description.get('pult')}', "
                    f"pult_descr = '{pult_description.get('client_name')}' "
                    f"where pult_id = {pult_description.get('id_client')}"
                    )
                self.con.commit()
            else:
                se = sys.exc_info()
                log.error(
                    f"Ошибка при сохранении данных о пульте "
                    f"{pult_description.get('pult')} \n "
                    f"{pult_description} \n"
                    f'{se[1]}\n{se[2].tb_frame.f_code}\n'
                )
        return None

    def delete_filter(self, filter_obj):
        try:
            self.cur.execute(f"delete from filters where id_filter = "
                             f"{filter_obj.id_filter}")
            self.con.commit()
        except Exception as e:
            self.con.rollback()
            log.error(f'Ошибка при удалении фильтра {filter_obj}\n'
                      f'{str(e)}\n'
                      f'{sys.exc_info()[2].tb_frame.f_code}')

    def get_filter_by_params(self, client_id, filter_address, filter_text):
        self.cur.execute(f"select * from filters where client_id =  {client_id} "
                         f" and filter_address = '{filter_address}' "
                         f" and filter_text = '{filter_text}'"
                         )
        ms = MyRecordSet(self.cur.fetchall(), self.cur.description)
        if len(ms._rows) > 0:
            return b_client.Filter(ms._rows[0][0], ms._rows[0][1],
                                      ms._rows[0][2], ms._rows[0][3])

        return None

    def create_edit_filter(self, filter_obj):
        # попробуем найти с таким ID
        self.cur.execute(f"select * from filters "
                         f"where id_filter =  {filter_obj.id_filter}")
        ms = MyRecordSet(self.cur.fetchall(), self.cur.description)
        if len(ms._rows) > 0:  # с таким id есть
            # попробуем найти с такими параметрами
            found_filter = self.get_filter_by_params(
                filter_obj.client_id,
                filter_obj.filter_address,
                filter_obj.filter_text)
            if found_filter:  # такой нашелся
                if found_filter.id_filter != filter_obj.id_filter:
                    # если это другой то удалим найденный
                    self.delete_filter(filter_obj)
                return found_filter
            try:
                # такой же не нашли, правим найденный
                self.cur.execute(f"update filters set "
                                 f"client_id = {filter_obj.client_id}, "
                                 f"filter_address='{filter_obj.filter_address}'"
                                 f", filter_text = '{filter_obj.filter_text}' "
                                 f" where id_filter = {filter_obj.id_filter}")
                self.con.commit()
                return filter_obj
            except Exception as e:
                self.con.rollback()
                log.error(f'Ошибка обновнления фильтра {filter_obj}\n'
                          f'{str(e)}\n'
                          f'{sys.exc_info()[2].tb_frame.f_code}')
                return filter_obj

        # не нашли с таким id, создаем новый
        sql_str = str(
                f'insert into filters (client_id, '
                f'filter_address, filter_text) '
                f'values ({filter_obj.client_id}, '
                f"'{filter_obj.filter_address}', "
                f"'{filter_obj.filter_text}')"
                )

        try:
            self.cur.execute(sql_str)
            self.con.commit()
            # вернем созданный фильтр
            return self.get_filter_by_params(
                filter_obj.client_id,
                filter_obj.filter_address,
                filter_obj.filter_text
                )
        except Exception as e:
            log.error(f'Ошибка создания фильтра {filter_obj}\n'
                      f'{sql_str}\n'
                      f'{str(e)}\n'
                      f'{sys.exc_info()[2].tb_frame.f_code}')
            filter_obj = None
        return filter_obj

    def get_filters_for_client(self, client_id):
        filter_list = []
        self.cur.execute(f"select * from filters where client_id = {client_id}")
        ms = MyRecordSet(self.cur.fetchall(), self.cur.description)
        if len(ms._rows) > 0:  # с таким client_id есть
            for row in ms._rows:
                filter_list += [b_client.Filter(row[0], row[1],
                                                   row[2], row[3])]
        return filter_list

    def get_filter_by_id(self, filter_id):
        self.cur.execute(f"select * from filters where id_filter = {filter_id}")
        ms = MyRecordSet(self.cur.fetchall(), self.cur.description)
        if len(ms._rows) > 0:  # с таким id есть
            return b_client.Filter(ms._rows[0][0], ms._rows[0][1],
                                      ms._rows[0][2], ms._rows[0][3])
        return None

    def get_create_client(self, telega_id):
        """
        Получение клиента, если нет, то создает нового
        """
        client = self.get_telega_client(telega_id)
        if client:
            return client
        return self.create_edit_client(b_client.TelegaClient(0, 2,
                                                                telega_id))

    def confirm_client(self, client):
        """
        Подтверждает рабочее состяние клиента
        """
        log.debug(f'confirm_client: телега клиент {client}')
        sql_str = str(
                f"update clients "
                f"set lastdate = '{datetime.date.today()}',"
                f"sent_inform = 0 "
                f"where telega_id = {client}"
                )
        try:
            self.cur.execute(sql_str)
            self.con.commit()
        except Exception as e:
            log.error(f'confirm_client: Ошибка сброса даты клиента {client}\n'
                      f'{sql_str}\n'
                      f'{str(e)}\n'
                      f'{sys.exc_info()[2].tb_frame.f_code}')

    def delete_client(self, client):
        """
        удаляет из БД клиента, его регистрации и фильтры
        """
        result = True
        log.warning(f"delete_client: {client}")
        sql_str = str(
                f"delete from clients "
                f"where id_client = {client}"
                )
        try:
            log.debug(f"delete_client: удаление из таблицы clients")
            self.cur.execute(sql_str)
        except Exception as e:
            self.con.rollback()
            result = False
            log.error(f'delete_client:: Ошибка удаления из clients \n{client}\n'
                      f'{sql_str}\n'
                      f'{str(e)}\n'
                      f'{sys.exc_info()[2].tb_frame.f_code}')

        sql_str = str(
                f"delete from client_pult "
                f"where client_id = {client}"
                )
        try:
            log.debug(f"delete_client: удаление из таблицы client_pult")
            self.cur.execute(sql_str)
        except Exception as e:
            result = False
            self.con.rollback()
            log.error(f'delete_client:: Ошибка удаления из client_pult \n{client}\n'
                      f'{sql_str}\n'
                      f'{str(e)}\n'
                      f'{sys.exc_info()[2].tb_frame.f_code}')

        sql_str = str(
                f"delete from filters "
                f"where client_id = {client}"
                )
        try:
            log.debug(f"delete_client: удаление из таблицы filters")
            self.cur.execute(sql_str)
        except Exception as e:
            result = False
            self.con.rollback()
            log.error(f'delete_client:: Ошибка удаления из filters \n{client}\n'
                      f'{sql_str}\n'
                      f'{str(e)}\n'
                      f'{sys.exc_info()[2].tb_frame.f_code}')
        if result:
            self.con.commit()
        return result
