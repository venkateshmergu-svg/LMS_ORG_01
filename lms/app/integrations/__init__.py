"""Integration layer.

Ports/adapters that connect LMS with external systems.
All integrations are:
- Idempotent
- Retry-safe
- Auditable

Architectural constraints:
- Engines DO NOT import integration code
- Integrations call repositories via a shared session (Unit of Work)
- No direct DB access outside repositories
- No commits inside integrations (Unit of Work handles transactions)
"""

__all__ = []
