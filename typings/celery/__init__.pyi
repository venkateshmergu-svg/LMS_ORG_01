from __future__ import annotations

from typing import Any, Callable

class Celery:
    conf: Any

    def __init__(
        self,
        main: str,
        broker: str | None = ...,
        backend: str | None = ...,
        **kwargs: Any,
    ) -> None: ...

    def task(self, *args: Any, **kwargs: Any) -> Callable[[Callable[..., Any]], Callable[..., Any]]: ...

    def autodiscover_tasks(self, packages: Any, related_name: str | None = ..., force: bool = ...) -> None: ...
