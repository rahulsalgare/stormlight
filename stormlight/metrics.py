import asyncio
import time
from collections import defaultdict

from tabulate import tabulate


headers = [ "Method", "Endpoint", "RPS", "Median (ms)", "Average (ms)", "Min (ms)", "Max (ms)",
    "Failed Requests", "Total Requests"]


class EntriesDict(dict):
    def __init__(self, request_metrics):
        self.request_metrics = request_metrics

    def __missing__(self, key):
        self[key] = MetricsEntry(self.request_metrics, key[0], key[1])
        return self[key]


class Metrics:
    def __init__(self):
        # stores request details of individual tasks in a dictionary
        self.entries: dict[tuple[str, str], MetricsEntry] = EntriesDict(self)
        # stores aggregated request details of all the requests
        self.total = MetricsEntry(self, None, None)

    @property
    def start_time(self):
        return self.total.start_time

    @property
    def last_request_timestamp(self):
        return self.total.last_request_timestamp

    def log_request(self, method: str, endpoint: str, response_time: int):
        self.total.log(response_time)
        self.entries[(endpoint, method)].log(response_time)

    def log_error(self, method, endpoint):
        self.total.log_error()
        self.entries[(endpoint, method)].log_error()


class MetricsEntry:
    def __init__(self, metrics: Metrics, endpoint, method):
        self.metrics = metrics
        self.endpoint = endpoint
        self.method = method
        self.num_requests: int = 0
        self.num_failures: int = 0
        self.total_response_time = 0
        self.max_response_time: int = 0
        self.min_response_time: int | None = None
        self.response_times: dict[int, int] = defaultdict(int)
        self.start_time = time.time()
        self.last_request_timestamp: float | None = None

    def log(self, response_time):
        current_time = time.time()
        self.num_requests += 1
        self._log_response_time(response_time)
        self._log_request_time(current_time)

    def log_error(self) -> None:
        self.num_failures += 1

    @property
    def avg_response_time(self) -> float:
        try:
            return round(float(self.total_response_time) / self.num_requests, 2)
        except ZeroDivisionError:
            return 0.0

    @property
    def rps(self):
        if not self.metrics.last_request_timestamp or not self.metrics.start_time:
            return 0.0
        try:
            return round(self.num_requests / (self.metrics.last_request_timestamp - self.metrics.start_time), 2)
        except ZeroDivisionError:
            return 0.0

    def get_percentile(self, percentile):
        sorted_times = sorted(self.response_times.keys())
        threshold = self.num_requests * (percentile / 100)
        cumulative_count = 0

        for response_time in sorted_times:
            cumulative_count += self.response_times[response_time]
            if cumulative_count >= threshold:
                return response_time  # Return response time at percentile

    def _log_request_time(self, current_time: float) -> None:
        self.last_request_timestamp = current_time

    def _log_response_time(self, response_time):
        self.total_response_time += response_time

        if self.min_response_time is None:
            self.min_response_time = response_time
        else:
            self.min_response_time = round(min(self.min_response_time, response_time), 2)
        self.max_response_time = round(max(self.max_response_time, response_time), 2)

        self.response_times[round(response_time)] += 1


def get_metrics_summary(metrics: Metrics):
    """
    Get metrics data stored in Metrics object and arrange it in table format

    :param metrics:
    :return: metrics table
    """
    table_data = []
    for endpoint in sorted(metrics.entries.keys()):
        method = endpoint[1]
        path = endpoint[0]
        rps =  metrics.entries[endpoint].rps
        median = metrics.entries[endpoint].get_percentile(50)
        average = metrics.entries[endpoint].avg_response_time
        max_response_time = metrics.entries[endpoint].max_response_time
        min_response_time = metrics.entries[endpoint].min_response_time
        # ninetieth_percentile = metrics.entries[endpoint].get_percentile(90)
        failed_requests = metrics.entries[endpoint].num_failures
        total_requests = metrics.entries[endpoint].num_requests
        table_data.append([method, path, rps, median, average, min_response_time,
                           max_response_time, failed_requests, total_requests])

    table_data.append(['-'*15 for i in range(9)])
    total_rps = metrics.total.rps
    total_median = metrics.total.get_percentile(50)
    total_avg = metrics.total.avg_response_time
    total_min = metrics.total.min_response_time
    total_max = metrics.total.max_response_time
    total_failed = metrics.total.num_failures
    total_requests = metrics.total.num_requests
    table_data.append(['total', '', total_rps, total_median, total_avg, total_min, total_max,
                       total_failed, total_requests])

    return tabulate(table_data, headers=headers)


async def display_metrics(metrics, end_time):
    """
    Display metrics in real time on terminal. This will run for the whole duration of a load test.
    Metrics will be displayed every two seconds on terminal

    :param metrics: Metrics object
    :param end_time: end time of load test
    :return:
    """
    while time.time() < end_time:
        metrics_table = get_metrics_summary(metrics)
        print(metrics_table, '\n\n')
        await asyncio.sleep(2)
