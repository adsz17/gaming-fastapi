"""Simple Locust load test.

Run with:
    locust -f tools/load.py -u 100 -r 10 --host http://localhost:8000

This spawns 100 users gradually hitting the ``/health`` endpoint.
"""

from locust import HttpUser, between, task


class CrashUser(HttpUser):
    """User that repeatedly calls the health endpoint."""

    wait_time = between(1, 2)

    @task
    def health(self) -> None:
        self.client.get("/health")
