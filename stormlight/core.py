import time
import random
import asyncio
import aiohttp

from .data_classes import Task, Environment
from .metrics import Metrics, display_metrics

class User:
    host: str
    tasks: list[Task] = []

    async def send_request(self, session, task):
        url = f"{self.host}{task.path}"
        start_time = time.time()
        async with session.request(task.method, url, json=task.data) as response:
            latency = (time.time() - start_time) * 1000  # convert to ms
            return {
                "method": task.method,
                "endpoint": task.path,
                "response_time": latency
            }

    async def run(self, end_time, metrics):
        async with aiohttp.ClientSession() as session:
            while time.time() < end_time:
                task = random.choice(self.tasks)
                try:
                    result = await self.send_request(session, task)
                    metrics.log_request(**result)
                except Exception:
                    metrics.log_error(task.method, task.path)

class Runner:
    def __init__(self, environment: Environment):
        self.metrics = Metrics()
        self.environment = environment
        User.tasks = self.environment.tasks
        User.host = self.environment.host

    async def spawn_user(self, end_time):
        user = User()
        await user.run(end_time, self.metrics)

    async def spawn_users(self, end_time):
        async with asyncio.TaskGroup() as tg:
            for _ in range(self.environment.user_count):
                tg.create_task(self.spawn_user(end_time))
                await asyncio.sleep(1 / self.environment.spawn_rate)

    async def start(self):
        end_time = time.time() + self.environment.duration
        async with asyncio.TaskGroup() as tg:
            tg.create_task(self.spawn_users(end_time))
            tg.create_task(display_metrics(self.metrics, end_time))

if __name__ == '__main__':
    tasks = [
        Task("GET", "/hello", {"Content-Type": "application/json"}),
        Task("POST", "/api/upload", data={"name": "test", "price": 10},
             headers={"Content-Type": "application/json"})
    ]

    environment = Environment(
        host="http://127.0.0.1:8000",
        tasks=tasks,
        user_count=10,
        spawn_rate=5,
        duration=10,
    )
    runner = Runner(environment)
    asyncio.run(runner.start())
