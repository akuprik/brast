
from requests import request

from b_constants import API_PATH
from b_db import CktsBotDB
from logs import Logger

log = Logger(log_name='ckts_api')

def get_pult(pult):
    """
    запросить данные о пульте в ЦКС
    """
    response = request('get', f'{API_PATH}pulttest.asp', params={'pult': pult})
    if response.status_code == 200:
        return response.json()
    log.warning(f'get_pult: status_code={response.status_code} pult={pult}')
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

def get_tlgs(telegaid, telegafio, pults: list, filters: list):
    """
    Запросим телеграммы для клиента
    :param telegaid:
    :param telegafio:
    :param pults:
    :param filters:
    :return:
    """
    data = {'telegaid': telegaid,
            'pults': ','.join(pults),
            'telegafio': telegafio,
            'filters': ','.join(filters),
            }
    print(data)
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    result = request(method='post',
                     url=f'{API_PATH}gettlg.asp',
                     headers=headers, data=data)

    if result.status_code == 200:
        return result.json()

    log.warning(f'gettlg.asp: status_code={result.status_code} data={data}')
    return {'tlg_list': {}}
