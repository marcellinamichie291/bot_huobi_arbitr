import datetime as dt

from sqlalchemy import Column, ForeignKey, Integer, Numeric, String, Table
from sqlalchemy.ext.declarative import declarative_base 
from sqlalchemy.orm import relationship


Base = declarative_base()


pair_bundle = Table(
    "pair_bundle",
    Base.metadata,
    Column("pair_id", Integer, ForeignKey("currency_pair.id")),
    Column("bundle_id", Integer, ForeignKey("bundle.id"))
)


class CurrencyPair(Base):
    __tablename__ = 'currency_pair'

    id = Column(Integer, primary_key=True)
    pair = Column(String, nullable=False, unique=True)
    ticker = Column(String)
    rate = Column(Numeric(asdecimal=False), nullable=False, default=1)
    reversed_pair_id = Column(Integer, ForeignKey('currency_pair.id'))
    status = Column(String, nullable=False, default='ok')

    bundle_list = relationship(
        'Bundle', 
        back_populates='pairs_list_raw',
        secondary=pair_bundle)

    reversed_pair = relationship(
        'CurrencyPair', 
        remote_side='CurrencyPair.id',
        backref='huobi_pair')

    def ppp(self):
        if self.status == 'invalid symbol':
            pass

    def __repr__(self) -> str:
        return f'<{self.pair}>'


class Bundle(Base):
    __tablename__ = 'bundle'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    pairs_order = Column(String, nullable=False)
    sum = Column(Numeric(asdecimal=False), nullable=False)
    pairs_list_raw = relationship(
        'CurrencyPair', 
        back_populates='bundle_list',
        secondary=pair_bundle
    )
