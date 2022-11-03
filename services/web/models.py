import logging

from flask_login import UserMixin
from sqlalchemy.orm import object_session, reconstructor
from werkzeug.security import check_password_hash

from db import db


logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s',
    level=logging.INFO,
    filename='log.log'
    )


pair_bundle = db.Table(
    "pair_bundle",
    db.Column("pair_id", db.Integer, db.ForeignKey("currency_pair.id")),
    db.Column("bundle_id", db.Integer, db.ForeignKey("bundle.id"))
)


class AdminModel(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return f'<Admin {self.id} - {self.username}>'


class CurrencyPair(db.Model):
    __tablename__ = 'currency_pair'

    id = db.Column(db.Integer, primary_key=True)
    pair = db.Column(db.String, nullable=False, unique=True)
    ticker = db.Column(db.String)
    rate = db.Column(db.Numeric(asdecimal=False), nullable=False, default=1)
    reversed_pair_id = db.Column(db.Integer, db.ForeignKey('currency_pair.id'))
    status = db.Column(db.String, nullable=False, default='ok')

    bundle_list = db.relationship(
        'Bundle', 
        back_populates='pairs_list_raw',
        secondary=pair_bundle)

    reversed_pair = db.relationship(
        'CurrencyPair', 
        remote_side='CurrencyPair.id',
        backref='huobi_pair')




    def ppp(self):
        if self.status == 'invalid symbol':
            pass



    def __repr__(self) -> str:
        return f'<{self.pair}>'


class Bundle(db.Model):
    __tablename__ = 'bundle'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    pairs_order = db.Column(db.String, nullable=False)
    sum = db.Column(db.Numeric(asdecimal=False), nullable=False)
    status = db.Column(db.String, nullable=False, default='ok')
    pairs_list_raw = db.relationship(
        'CurrencyPair', 
        back_populates='bundle_list',
        secondary=pair_bundle
    )

    def _get_pair(self, pair_id):
        for pair in self.pairs_list_raw:
            if pair.id == pair_id:
                return pair
        raise ValueError(f'Не найдена пара с айди {pair_id} для сортировки')

    @property
    def pairs_list(self):
        """
        Сортируем пары, чтобы были в том 
        порядке, как их задали в админке
        """
        p_order = list(map(int, self.pairs_order.split(',')))
        sorted_list = list()
        for pair_id in p_order:
            pair = self._get_pair(pair_id)
            sorted_list.append(pair)

        return sorted_list

    @property
    def main_currency(self) -> str:
        """
        Вычисляем валюту, которая идёт на вход, и которая выходит
        """
        curr_list = [pair.pair for pair in self.pairs_list]
        start_set = set(curr_list[0].split('/'))
        end_set = set(curr_list[-1].split('/'))
        main_currency_set = start_set & end_set

        if not main_currency_set:
            raise ValueError('Невозможно вычислить валюту входа и выхода')

        return main_currency_set.pop()

    def get_method(self, from_curr: str, pair: str):
        if from_curr == pair.split('/')[-1]:
            return 'division'
        elif from_curr == pair.split('/')[0]:
            return 'multiplication'

        return f'Error: Неверно задана цепочка пар: {from_curr} > {pair}'

    def in_usdt(self, currency_name, sum):
        """
        Переводит криптовалюту в USDT
        """
        if currency_name == 'USDT':
            return sum

        pair = f'{currency_name}/USDT'
        rate = (
            object_session(self).query(CurrencyPair)
            .filter_by(pair=pair)
            .first()
        )
        if not rate:
            raise ValueError(f'Не задан курс для пары {pair} (для вычисления эквивалента в USDT)')

        return round(rate.rate * sum, 8)

    def spread(self, usdt=False):
        """
        Вычисляем спред в основной валюте или в USDT
        """
        if usdt:
            start_sum = self.in_usdt(self.main_currency, self.sum)
            end_sum = self.in_usdt(self.main_currency, self.calc_end_result())
            return round(end_sum / start_sum * 100 - 100, 2)

        end_result = self.calc_end_result()
        logging.info(f'Вычисляем СПРЕД: {end_result} / {self.sum} * 100 - 100')

        spread = round(end_result / self.sum * 100 - 100, 2)
        logging.info(f'СПРЕД: {spread}')
        return spread

    def calc_end_result(self):
        """
        Вычисляем конечный результат после прохода 
        всех пар в связке. Результат в основной валюте
        """
        from_curr = self.main_currency

        result = self.sum
        for pair in self.pairs_list:
            method = self.get_method(from_curr, pair.pair)
            if method == 'division':
                to_curr = pair.pair.split('/')[0]

                logging.info(f'Переводим {from_curr} в {to_curr}')
                logging.info(f'result = {result} / {pair.rate}')

                result /= pair.rate

                logging.info(f'result: {result}')
                from_curr = to_curr

            elif method == 'multiplication':
                to_curr = pair.pair.split('/')[-1]

                logging.info(f'Переводим {from_curr} в {to_curr}')
                logging.info(f'result = {result} * {pair.rate}')

                result *= pair.rate

                logging.info(f'result: {result}')
                from_curr = to_curr

            elif 'Error' in method:
                raise ValueError(method)

        return result

    def __repr__(self) -> str:
        return f'<{self.name}>'


class Settings(db.Model):
    __tablename__ = 'settings'

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String, nullable=False)
    value = db.Column(db.String)
