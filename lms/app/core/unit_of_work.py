"""Unit of Work pattern for transaction management.

Manages a SQLAlchemy session and transaction lifecycle for a single request.
- Starts a transaction on __enter__
- Commits on successful completion (__exit__ with no exception)
- Rolls back on any exception
- Always closes the session
- Does NOT swallow exceptions

Ensures atomicity: either all domain changes + audit logs persist, or none do.
"""
from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session


class UnitOfWork:
    """
    Unit of Work context manager for transactional request handling.
    
    Usage:
        with UnitOfWork(session) as uow:
            # Use uow.session in repositories/engines
            # On normal exit: commits transaction
            # On exception: rolls back transaction
    """
    
    def __init__(self, session: Session) -> None:
        """Initialize UnitOfWork with a session.
        
        Args:
            session: SQLAlchemy Session instance
        """
        self.session = session
        self._transaction: Any = None
    
    def __enter__(self) -> UnitOfWork:
        """Begin transaction.
        
        Returns:
            Self, for use in with statements
        """
        self._transaction = self.session.begin()
        return self
    
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Commit on success, rollback on exception, always close session.
        
        Args:
            exc_type: Exception type if an exception occurred, else None
            exc_val: Exception instance if an exception occurred, else None
            exc_tb: Traceback if an exception occurred, else None
        
        Returns:
            None to NOT suppress exceptions (let them propagate)
        """
        try:
            if exc_type is not None:
                # Exception occurred; rollback transaction
                self._transaction.rollback()
            else:
                # No exception; commit transaction
                self._transaction.commit()
        finally:
            # Always close the session, regardless of commit/rollback outcome
            self.session.close()
