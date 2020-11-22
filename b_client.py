import datetime

class TelegaClient:
    def __init__(self, id, client_type,
                 telega_id, client_type_nic=None,
                 lastdate=None, sent_info=0):
        self.client_id = id
        self.client_type = client_type if client_type else 2
        self.telega_id = str(telega_id)
        self.client_type_nic = client_type_nic
        self.lastdate = (lastdate
                         if lastdate is not None
                         else str(datetime.date.today()))

        self.sent_info = sent_info

    def __str__(self):
        return (f'id:{self.client_id} '
                f'role:{self.client_type_nic} '
                f't_id:{self.telega_id} '
                f'ld:{self.lastdate} '
                f'si:{self.sent_info}')


class ClientPult:
    def __init__(self, id, client_id, pult, valid,
                 telega_id=None, pult_decription=''):
        self.id = id if id else 0
        self.client_id = client_id
        self.pult = pult
        self.valid = valid
        self.telega_id = telega_id
        self.pult_description = pult_decription

    def valid_str(self):
        if self.valid != 0:
            return 'подтверждена'
        return 'ждет подтверждения'

    def str_for_client(self):
        return f'{self.pult} {self.valid_str()}'

    def str_for_admin(self):
        return (f'{self.pult}/{self.pult_description}/{self.valid_str()} '
                )

    def __str__(self):
        return f'{self.id} {self.client_id} {self.pult} {self.valid}'


class Filter:
    def __init__(self, id_filter, client_id, filter_address, filter_text):
        self.id_filter = id_filter
        self.client_id = client_id
        self.filter_address = filter_address.upper()[:8]
        self.filter_text = filter_text.upper()[:32]

    def __str__(self):
        return (f'id:{self.id_filter} /'
                f' cl:{self.client_id} /'
                f' a:{self.filter_address} /'
                f' t:{self.filter_text}'
                )

class Tlg:
    def __init__(self, tlg : dict):
        self.tlg_id = tlg.get('ID_TLG')
        self.time = tlg.get('RecTime')
        self.priority = tlg.get('PrCode')
        self.dst_addr = tlg.get('DstAddrStr')
        self.snd_num = tlg.get('SndNum')
        self.snd_addr = tlg.get('SndAddr')
        self.text = tlg.get('Txt').replace('###', '\n')

    def __str__(self):
        return (f"id:{self.tlg_id} time:{self.time}\n"
                f"{self.priority} {self.dst_addr}\n"
                f"{self.snd_num} {self.snd_addr}\n"
                f"{self.text}")
