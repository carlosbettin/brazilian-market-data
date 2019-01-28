from bs4 import BeautifulSoup
from datetime import datetime
import logging
import re
import requests

IMA_COMPLETO_URL = 'http://www.anbima.com.br/ima/arqs/ima_completo.xml'

IMA_FIELD_MAP = {
    "Indice": {
        "T_Yield": "YLD",
        "T_Duration": "DUR",
        "T_Num_Indice": "COT",
        },
    "Carteira": {
        "C_Taxa": "YLD",
        "C_PU": "COT",
        "C_Duration": "DUR",
        "C_Prazo": "DU",
        "C_Convexidade": "CVX",
        },
    }


def _get_anbima_page(url):
    """Connect to the Anbima webpage and return a BeautifulSoup xml object.

    Parameters
    ----------
    url: str
        address of the webpage.

    Results
    -------
    xml_page: bs4.BeautifulSoup
        bs4.BeautifulSoup xml object of the page.

    """
    try:
        r = requests.get(url)
        xml_page = BeautifulSoup(r.content, features='xml')
        return xml_page
    except Exception:
        logging.exception('Problem requesting from Anbima')
        return


def _get_ima_completo_page():
    soup = _get_anbima_page(IMA_COMPLETO_URL)
    return soup


def get_ntnb_data():
    """
    Get a list of dictionaries with information from last available date for
    each component of the IMA-B index.

    """
    page = _get_ima_completo_page()
    # imab contains all NTN-Bs available at the moment.
    imab = page.find_all(re.compile('FAMILIA'))[5]
    # get the date in dd/mm/yyyy format.
    date_br = imab.find_all("TOTAIS")[0]["DT_REF"]
    # convert date_br to datetime.date() object.
    date = datetime.strptime(date_br, '%d/%m/%Y').date()
    # get a list of the ntnbs in the IMA-B index as xml object.
    imab_carteira = imab.find_all("CARTEIRA")
    # loop in each tag.
    data = []
    # imab_carteira[0]
    for tag in imab_carteira:
        tmp = {}
        imab_carteira[0]
        alias = "{tit} | {vdt}".format(tit=tag["C_Titulo"],
                                       vdt=tag["C_Data_Vencimento"])
        tmp.update({"name": alias})
        tmp.update({'date': date})
        tmp.update({'maturity date': tag["C_Data_Vencimento"]})
        for key, val in IMA_FIELD_MAP["Carteira"].items():
            if key == "C_Duration":
                ima_fld = float(tag[key].replace(",", "."))/252
            else:
                ima_fld = float(tag[key].replace(",", "."))

            tmp.update({val: ima_fld})

        data.append(tmp)

    return data


if __name__ == '__main__':
    get_ntnb_data()
