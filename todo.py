import json
from pathlib import Path

TODO_FILE = Path("todos.json")

def load_todos() -> list[dict]:
    if TODO_FILE.exists():
        return json.loads(TODO_FILE.read_text())
    return []


def save_todos(todos: list[dict]) -> None:
    TODO_FILE.write_text(json.dumps(todos, indent=2))


def add_todo(title: str) -> None:
    todos = load_todos()
    todos.append({"id": len(todos) + 1, "title": title, "done": False})
    save_todos(todos)
    print(f"Added: {title}")


def list_todos() -> None:
    todos = load_todos()
    if not todos:
        print("No todos yet.")
        return
    for todo in todos:
        status = "x" if todo["done"] else " "
        print(f"  [{status}] {todo['id']}. {todo['title']}")


def complete_todo(todo_id: int) -> None:
    todos = load_todos()
    for todo in todos:
        if todo["id"] == todo_id:
            todo["done"] = True
            save_todos(todos)
            print(f"Completed: {todo['title']}")
            return
    print(f"No todo with id {todo_id}.")


def delete_todo(todo_id: int) -> None:
    todos = load_todos()
    updated = [t for t in todos if t["id"] != todo_id]
    if len(updated) == len(todos):
        print(f"No todo with id {todo_id}.")
        return
    save_todos(updated)
    print(f"Deleted todo {todo_id}.")


def print_help() -> None:
    print("Commands: add <title> | list | done <id> | delete <id> | quit")


def main() -> None:
    print("Todo List — type 'help' for commands\n")
    while True:
        raw = input("> ").strip()
        if not raw:
            continue
        parts = raw.split(maxsplit=1)
        cmd = parts[0].lower()
        arg = parts[1] if len(parts) > 1 else ""

        if cmd in ("quit", "exit"):
            break
        elif cmd == "add":
            if arg:
                add_todo(arg)
            else:
                print("Usage: add <title>")
        elif cmd == "list":
            list_todos()
        elif cmd == "done":
            if arg.isdigit():
                complete_todo(int(arg))
            else:
                print("Usage: done <id>")
        elif cmd == "delete":
            if arg.isdigit():
                delete_todo(int(arg))
            else:
                print("Usage: delete <id>")
        elif cmd == "help":
            print_help()
        else:
            print(f"Unknown command: {cmd}")
            print_help()


if __name__ == "__main__":
    main()
