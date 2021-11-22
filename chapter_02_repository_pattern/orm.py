from sqlalchemy import Column, ForeignKey, Integer, String, MetaData, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, mapper

# ORM은 Domain Model을 Import 한다. (또는 도메인 모델에 '의존' 하거나 '안다')
#  반대로 도메인 모델이 ORM을 Import 하지않는다.
import model

Base = declarative_base()

metadata = MetaData()
# SQLAlchemy가 제공하는 추상화로 DB의 Table과 Column을 정의
order_lines = Table(
    'order_lines', metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("sku", String(255)),
    Column("qty", Integer, nullable=False),
    Column("orderid", String(255)),
)


# Domain Model Instance를 DB에 저장하거나 DB에서 불러올 수 있다.
#  하지만 start_mappers를 호출하지 않으면 Domain Model Class는 DB를 인식하지 못한다.
def start_mappers():
    # mapper 함수를 호출할 때 사용자가 정의한 여러 테이블에 Domain Class를 연결한다.
    lines_mapper = mapper(model.OrderLine, order_lines)


class Order(Base):
    id = Column(Integer, primary_key=True)


class OrderLine(Base):
    id = Column(Integer, primary_key=True)
    sku = Column(String(250))
    qty = Integer(String(250))
    order_id = Column(Integer, ForeignKey('order.id'))
    order = relationship(Order)


class Allocation(Base):
    ...
