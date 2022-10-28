from flask_login import UserMixin
from sqlalchemy.orm import object_session, reconstructor
from werkzeug.security import check_password_hash

from db import db


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
    rate = db.Column(db.Numeric(asdecimal=False), nullable=False, default=1)

    bundle_list = db.relationship(
        'Bundle', 
        back_populates='pairs_list_raw',
        secondary=pair_bundle)

    def method(self):
        pass

    def __repr__(self) -> str:
        return f'<{self.pair}>'


class Bundle(db.Model):
    __tablename__ = 'bundle'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    pairs_order = db.Column(db.String, nullable=False)
    pairs_list_raw = db.relationship(
        'CurrencyPair', 
        back_populates='bundle_list',
        secondary=pair_bundle
    )


    def __init__(self, *args, **kwargs) -> None:
        self._pairs_list = None
        self.start_sum = 15

    @reconstructor
    def init_on_load(self, *args, **kwargs):
        self._pairs_list = None
        self.start_sum = 15


    def _get_pair(self, pair_id):
        for pair in self.pairs_list_raw:
            if pair.id == pair_id:
                return pair
        raise ValueError(f'Не найдена пара с айди {pair_id} для сортировки')

    @property
    def pairs_list(self):
        if self._pairs_list:
            return self._pairs_list

        print('Сортируем пары')
        p_order = list(map(int, self.pairs_order.split(',')))
        sorted_list = list()
        for pair_id in p_order:
            pair = self._get_pair(pair_id)
            sorted_list.append(pair)

        self._pairs_list = sorted_list
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
            raise ValueError(f'Невозможно вычислить валюту входа и выхода')

        return main_currency_set.pop()

    def get_method(self, from_curr: str, pair: str):
        if from_curr == pair.split('/')[-1]:
            return 'division'
        elif from_curr == pair.split('/')[0]:
            return 'multiplication'
        raise ValueError(f'Невозможно вычислить метод: from_curr={from_curr}; pair={pair}')

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
            start_sum = self.in_usdt(self.main_currency, self.start_sum)
            end_sum = self.in_usdt(self.main_currency, self.calc_end_result())
            return round(end_sum / start_sum * 100 - 100, 2)

        return round(self.calc_end_result() / self.start_sum * 100 - 100, 2)
        
    def calc_end_result(self):
        """
        Вычисляем конечный результат после прохода 
        всех пар в связке. Результат в основной валюте
        """
        from_curr = self.main_currency

        result = self.start_sum
        for pair in self.pairs_list:
            method = self.get_method(from_curr, pair.pair)
            if method == 'division':
                result /= pair.rate
                from_curr = pair.pair.split('/')[0]

            elif method == 'multiplication':
                result *= pair.rate
                from_curr = pair.pair.split('/')[-1]

        return result










    def __repr__(self) -> str:
        return super().__repr__()
