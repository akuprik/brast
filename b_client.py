
class TelegaClient:
    def __init__(self, id, client_type, telega_id, client_type_nic=None):
        self.client_id = id
        self.client_type = client_type if client_type else 2
        self.telega_id = str(telega_id)
        self.client_type_nic = client_type_nic

    def __str__(self):
        return (f'id:{self.client_id} '
                f'role:{self.client_type_nic} '
                f't_id:{self.telega_id}'
                )


class ClientPult:
    def __init__(self, id, client_id, pult, valid,
                 telega_id=None, valid_date=None, sent_confirm=None):
        self.id = id if id else 0
        self.client_id = client_id
        self.pult = pult
        self.valid = valid
        self.telega_id = telega_id
        self.valid_date = valid_date
        self.sent_confirm = sent_confirm

    def valid_str(self):
        if self.valid != 0:
            return 'подтверждена'
        return 'ждет подтверждения'

    def str_for_client(self):
        return f'{self.pult} {self.valid_str()}'

    def str_for_admin(self):
        return (f'{self.pult} {self.valid_str()} '
                f'{self.valid_date} {self.sent_confirm}'
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
