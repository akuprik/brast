from requests import request

from b_constants import API_PATH
from b_db import CktsBotDB


def get_pult(pult):
    """
    запросить данные о пульте в ЦКС
    """
    response = request('get', f'{API_PATH}pulttest.asp', params={'pult': pult})
    if response.status_code == 200:
        res = response.json()
        cn = res.get('client_name').encode('cp1252').decode('cp1251')
        res['client_name'] = cn
        return res
    return {}


def test_pult_in_cks(pult):
    """
    Проверим в наличие такого пульта в ЦКС
    """
    result = get_pult(pult)
    if len(result) > 0:
        db = CktsBotDB()
        db.save_pult_description(result)
    return result
