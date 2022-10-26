from flask_login import UserMixin
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
    rate = db.Column(db.Numeric, nullable=False, default=1)

    bundle_list = db.relationship(
        'Bundle', 
        back_populates='currencies_list',
        secondary=pair_bundle)

    def method(self):
        pass

    def __repr__(self) -> str:
        return f'<{self.pair}>'


class Bundle(db.Model):
    __tablename__ = 'bundle'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    currencies_list = db.relationship(
        'CurrencyPair', 
        back_populates='bundle_list',
        secondary=pair_bundle
    )

    def __repr__(self) -> str:
        return super().__repr__()