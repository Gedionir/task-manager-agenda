import json

def save_tasks(tasks, filename="tasks.json"):
    with open(filename, "w") as f:
        json.dump([{"title": t.title, "done": t.done} for t in tasks], f)

def load_tasks(filename="tasks.json"):
    try:
        with open(filename, "r") as f:
            data = json.load(f)
            return [Task(d["title"], d["done"]) for d in data]
    except FileNotFoundError:
        return []