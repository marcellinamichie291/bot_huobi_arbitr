import os

from huobi.client.account import AccountClient
from huobi.constant import *

from huobi.utils import *

from config import HUOBI_API_KEY, HUOBI_SECRET_KEY


def get_account_id(account_type='spot'):
    account_client = AccountClient(api_key=HUOBI_API_KEY,
                                   secret_key=HUOBI_SECRET_KEY)

    accounts_list = account_client.get_accounts()
    for account in accounts_list:
        if account.type == account_type and account.state == 'working':
            return account.id
    return None




