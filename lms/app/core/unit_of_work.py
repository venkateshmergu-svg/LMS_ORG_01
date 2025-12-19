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
        # Context manager mode
        with UnitOfWork(session) as uow:
            # Use uow.session in repositories/engines
            # On normal exit: commits transaction
            # On exception: rolls back transaction
        
        # Explicit mode
        uow = UnitOfWork(session)
        uow.begin()
        try:
            # do work
            uow.commit()
        except:
            uow.rollback()
    """
    
    def __init__(self, session: Session) -> None:
        """Initialize UnitOfWork with a session.
        
        Args:
            session: SQLAlchemy Session instance
        """
        self.session = session
        self._transaction: Any = None
        self._completed = False
    
    def begin(self) -> None:
        """Begin a transaction explicitly.
        
        Can be called outside of context manager for explicit control.
        """
        if not self._transaction:
            self._transaction = self.session.begin()
    
    def commit(self) -> None:
        """Commit the current transaction explicitly.
        
        Guard against double-commit with _completed flag.
        """
        if self._completed:
            return
        
        if self._transaction:
            self._transaction.commit()
            self._completed = True
    
    def rollback(self) -> None:
        """Rollback the current transaction explicitly.
        
        Guard against double-rollback with _completed flag.
        """
        if self._completed:
            return
        
        if self._transaction:
            self._transaction.rollback()
            self._completed = True
    
    def __enter__(self) -> UnitOfWork:
        """Begin transaction in context manager mode.
        
        Returns:
            Self, for use in with statements
        """
        self.begin()
        return self
    
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Commit on success, rollback on exception, always close session.
        
        Args:
            exc_type: Exception type if exception occurred
            exc_val: Exception value if exception occurred
            exc_tb: Exception traceback if exception occurred
        """
        try:
            if exc_type is None:
                # Success: commit the transaction
                self.commit()
            else:
                # Exception: rollback the transaction
                self.rollback()
        finally:
            # Always close the session
            if self.session.is_active:
                self.session.close()
