import os
import ast
import importlib.util
import sys

STUBS = {
    "database.py": {
        "get_message_count": (
            "async def get_message_count(user_id: int) -> int:\n"
            "    user = get_user(user_id)\n"
            "    return user.get('message_count', 0) if user else 0\n"
        ),
        "increment_message_count": (
            "async def increment_message_count(user_id: int) -> None:\n"
            "    increment_messages(user_id)\n"
        ),
    },
    "payments.py": {
        "generate_purchase_button": (
            "async def generate_purchase_button(user_id: int):\n"
            "    from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup\n"
            "    url = get_payment_url(user_id)\n"
            "    button = InlineKeyboardButton(text='Buy', url=url)\n"
            "    return InlineKeyboardMarkup(inline_keyboard=[[button]])\n"
        ),
    },
    "utils.py": {
        "get_localized_strings": (
            "async def get_localized_strings(lang_code: str):\n"
            "    return get_locale_strings(lang_code)\n"
        ),
    },
}

def ensure_stub(path: str, func_name: str) -> None:
    """Append stub implementation for the given function."""
    code = STUBS.get(path, {}).get(func_name)
    if not code:
        return
    with open(path, "a", encoding="utf-8") as f:
        f.write("\n\n" + code + "\n")

GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"

PY_FILES = [
    "bot.py",
    "database.py",
    "handlers.py",
    "payments.py",
    "utils.py",
]

errors = []

def is_std_lib(module_name: str) -> bool:
    if module_name in sys.builtin_module_names:
        return True
    if hasattr(sys, "stdlib_module_names") and module_name in sys.stdlib_module_names:  # type: ignore[attr-defined]
        return True
    spec = importlib.util.find_spec(module_name)
    if spec and spec.origin:
        path = spec.origin
        if "site-packages" in path or "dist-packages" in path:
            return False
        return True
    return False

def check_syntax() -> None:
    for path in PY_FILES:
        try:
            with open(path, "r", encoding="utf-8") as f:
                ast.parse(f.read(), filename=path)
        except SyntaxError as e:
            errors.append(f"{path}: Syntax error - {e}")


def check_required_functions() -> None:
    for path in PY_FILES:
        with open(path, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=path)
        funcs = {
            node.name: node
            for node in tree.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        }

        if path in STUBS:
            for func_name in STUBS[path]:
                node = funcs.get(func_name)
                if node is None or not isinstance(node, ast.AsyncFunctionDef):
                    errors.append(f"{path}: missing async function {func_name}")
                    ensure_stub(path, func_name)

        if path == "database.py" and "init_db" not in funcs:
            errors.append("database.py: missing function init_db")

        if path == "handlers.py":
            has_router = any(
                isinstance(node, (ast.Assign, ast.AnnAssign))
                and any(getattr(t, "id", None) == "router" for t in (node.targets if isinstance(node, ast.Assign) else [node.target]))
                for node in tree.body
            )
            if not has_router:
                errors.append("handlers.py: missing router variable")

            has_start = False
            has_message = False
            for node in tree.body:
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    for deco in node.decorator_list:
                        if isinstance(deco, ast.Call) and isinstance(deco.func, ast.Attribute):
                            if isinstance(deco.func.value, ast.Name) and deco.func.value.id == "router" and deco.func.attr == "message":
                                if deco.args:
                                    arg = deco.args[0]
                                    if (
                                        isinstance(arg, ast.Call)
                                        and isinstance(arg.func, ast.Name)
                                        and arg.func.id == "CommandStart"
                                    ) or (isinstance(arg, ast.Name) and arg.id == "CommandStart"):
                                        has_start = True
                                else:
                                    has_message = True
            if not has_start:
                errors.append("handlers.py: missing CommandStart handler")
            if not has_message:
                errors.append("handlers.py: missing default message handler")


def check_env_vars() -> None:
    required = [
        "ACTIVE_TOKEN",
        "OPENAI_API_KEY",
        "TOKEN_TURKEY",
        "TOKEN_INDONESIA",
        "TOKEN_ARABIC",
        "TOKEN_VIETNAM",
        "TOKEN_BRAZIL",
    ]
    for var in required:
        if not os.getenv(var):
            errors.append(f"Environment variable {var} is not set")


def check_requirements() -> None:
    required_modules = []
    with open("requirements.txt", "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                required_modules.append(line.split("==")[0])

    imported = set()
    for path in PY_FILES:
        with open(path, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=path)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imported.add(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imported.add(node.module.split(".")[0])

    third_party = {m for m in imported if not is_std_lib(m)}
    for mod in sorted(third_party):
        if mod == "dotenv" and "python-dotenv" in required_modules:
            continue
        if mod not in required_modules:
            errors.append(f"requirements.txt missing module: {mod}")

    explicit = {"aiogram", "openai", "python-dotenv"}
    if "sqlite3" in imported or "aiosqlite" in imported:
        explicit.add("aiosqlite")
    for mod in sorted(explicit):
        if mod not in required_modules:
            errors.append(f"requirements.txt missing module: {mod}")


def main() -> None:
    check_syntax()
    check_required_functions()
    check_env_vars()
    check_requirements()

    if errors:
        print(f"{RED}❌ Обнаружены проблемы:{RESET}")
        for err in errors:
            print(f" - {err}")
    else:
        print(f"{GREEN}✅ Всё корректно{RESET}")


if __name__ == "__main__":
    main()
