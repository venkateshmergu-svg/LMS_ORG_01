from __future__ import annotations

import pytest

from lms.app.core.unit_of_work import UnitOfWork


class FakeTransaction:
    def __init__(self):
        self.committed = False
        self.rolled_back = False

    def commit(self):
        self.committed = True

    def rollback(self):
        self.rolled_back = True


class FakeSession:
    def __init__(self):
        self._tx = FakeTransaction()
        self.closed = False
        self.begin_calls = 0
        self.is_active = True

    def begin(self):
        self.begin_calls += 1
        return self._tx

    def close(self):
        self.closed = True
        self.is_active = False


def test_uow_commit_on_success():
    session = FakeSession()
    uow = UnitOfWork(session)  # type: ignore

    with uow:
        # do some work
        pass

    assert session.begin_calls == 1
    assert session._tx.committed is True
    assert session._tx.rolled_back is False
    assert session.closed is True


def test_uow_rollback_on_exception():
    session = FakeSession()
    uow = UnitOfWork(session)  # type: ignore

    class boom(Exception):
        pass

    with pytest.raises(boom):
        with uow:
            raise boom()

    assert session.begin_calls == 1
    assert session._tx.committed is False
    assert session._tx.rolled_back is True
    assert session.closed is True


def test_uow_explicit_begin_commit():
    session = FakeSession()
    uow = UnitOfWork(session)  # type: ignore

    uow.begin()
    uow.commit()

    assert session.begin_calls == 1
    assert session._tx.committed is True
    assert session._tx.rolled_back is False
    assert session.closed is False  # explicit usage doesn't auto-close


def test_uow_explicit_begin_rollback():
    session = FakeSession()
    uow = UnitOfWork(session)  # type: ignore

    uow.begin()
    uow.rollback()

    assert session.begin_calls == 1
    assert session._tx.committed is False
    assert session._tx.rolled_back is True
    assert session.closed is False
