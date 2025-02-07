from stormlight import Task

# Define the API endpoints and requests to test
endpoints = [
    Task("GET", "/hello", headers={"Content-Type": "application/json"}),
    Task("POST", "/api/upload",data = {"name": "test", "price": 10}, headers={"Content-Type": "application/json"})
]
