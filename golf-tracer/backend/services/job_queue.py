"""In-process asyncio job queue.

Interface is designed to be swappable with Celery: the only external
contract is `enqueue(job_id)`. Worker coroutines consume from the queue
and call `pipeline_service.run(job_id)`.
"""
from __future__ import annotations

import asyncio
import logging
from typing import Callable, Coroutine, Optional

log = logging.getLogger(__name__)


class JobQueue:
    def __init__(self, max_concurrent: int = 2) -> None:
        self._queue: asyncio.Queue[str] = asyncio.Queue()
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self._handler: Optional[Callable[[str], Coroutine]] = None
        self._running = False
        self._workers: list[asyncio.Task] = []

    def set_handler(self, handler: Callable[[str], Coroutine]) -> None:
        self._handler = handler

    async def enqueue(self, job_id: str) -> None:
        await self._queue.put(job_id)
        log.info(f"[Queue] Enqueued job {job_id}")

    async def start(self, num_workers: int = 2) -> None:
        self._running = True
        for _ in range(num_workers):
            task = asyncio.create_task(self._worker())
            self._workers.append(task)
        log.info(f"[Queue] Started {num_workers} workers")

    async def stop(self) -> None:
        self._running = False
        for w in self._workers:
            w.cancel()
        self._workers.clear()

    async def _worker(self) -> None:
        while self._running:
            try:
                job_id = await asyncio.wait_for(self._queue.get(), timeout=1.0)
            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                return

            async with self._semaphore:
                if self._handler:
                    try:
                        await self._handler(job_id)
                    except Exception:
                        log.exception(f"[Queue] Worker error processing job {job_id}")
                self._queue.task_done()


queue = JobQueue()
