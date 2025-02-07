import os
import argparse


def parse_script(script_path):
    if not os.path.exists(script_path):
        raise FileNotFoundError(f"Script file not found: {script_path}")

    global_vars = {}
    with open(script_path, "r") as file:
        exec(file.read(), global_vars)

    if "endpoints" not in global_vars:
        raise ValueError("The script must define an 'endpoints' variable.")

    return global_vars["endpoints"]

def parse_args():
    parser = argparse.ArgumentParser(description="Configure the load test parameters.")

    parser.add_argument("--users", type=int, required=True, help="Number of users to simulate.")
    parser.add_argument("--spawn-rate", type=float, required=True, help="Users spawned per second.")
    parser.add_argument("--host", type=str, required=True, help="Host/IP address.")
    parser.add_argument("--duration", type=int, required=True, help="Duration in seconds for which the test will run.")

    args = parser.parse_args()
    return args
