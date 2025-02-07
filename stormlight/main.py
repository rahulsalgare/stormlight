import asyncio

from .parser import parse_script, parse_args
from .core import Runner
from .data_classes import Environment

def create_environment(config, tasks):
    env = Environment
    env.spawn_rate = config.spawn_rate
    env.host = config.host
    env.user_count = config.users
    env.duration = config.duration
    env.tasks = tasks
    return env


def main():
    tasks = parse_script("stormlight_file.py")

    config = parse_args()
    environment = create_environment(config, tasks)

    runner = Runner(environment)
    asyncio.run(runner.start())


if __name__ == '__main__':
    main()