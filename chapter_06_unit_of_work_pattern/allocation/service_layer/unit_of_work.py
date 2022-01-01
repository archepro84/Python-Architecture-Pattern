from __future__ import annotations
import abc
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

from allocation import config
from allocation.adapters import repository


class AbstractUnitOfWork(abc.ABC):
    batches: repository.AbstractRepository  # UoW는 .batches라는속성을 제공한다. 이 속성은 배치 저장소에 접근할 수 있게 해준다.

    def __enter__(self) -> AbstractUnitOfWork:  # ConectManager의 시작
        return self

    def __exit__(self, *args):  # ConectManager의 종료
        self.rollback()

    @abc.abstractmethod
    def commit(self):  # 준비가 되면 이 메서드를 호출해서 작업을 Commit 한다.
        raise NotImplementedError

    # commit을 하지 않거나 예외를 발생시켜서 Conext Manager를 빠져나가면 Rollback을 수행한다.
    #  commit()이 이미 호출된 경우에는 Rollback을 해도 아무런 일도 발생하지 않는다.
    @abc.abstractmethod
    def rollback(self):
        raise NotImplementedError


# Postgres와 연결하는 Default Session Factory를 정의한다.
#  하지만 이를 통합 테스트에서 오버라이드해서 SQLite를 사용할 수 있게 허용한다.
DEFAULT_SESSION_FACTORY = sessionmaker(
    bind=create_engine(
        config.get_postgres_uri(),
    )
)


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(self, session_factory=DEFAULT_SESSION_FACTORY):
        self.session_factory = session_factory

    def __enter__(self):
        self.session = self.session_factory()  # DB Session을 시작하고 Session을 사용할 실제 저장소를 인스턴스화 한다.
        self.batches = repository.SqlAlchemyRepository(self.session)
        return super().__enter__()

    def __exit__(self, *args):
        super().__exit__(*args)
        self.session.close()  # Conext Manager에서 나올 때 Session을 닫는다.

    def commit(self):  # Db Session에서 사용할 구체적인 commit() 메서드
        self.session.commit()

    def rollback(self):  # Db Session에서 사용할 구체적인 rollback() 메서드
        self.session.rollback()
