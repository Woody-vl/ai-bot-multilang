import os
import ast
import importlib.util
import sys

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
        func_names = {node.name for node in tree.body if isinstance(node, ast.FunctionDef)}

        if path == "database.py":
            for func in ["init_db", "get_message_count", "increment_message_count"]:
                if func not in func_names:
                    errors.append(f"database.py: missing function {func}")

        if path == "payments.py":
            if "generate_purchase_button" not in func_names:
                errors.append("payments.py: missing function generate_purchase_button")

        if path == "utils.py":
            if "get_localized_strings" not in func_names:
                errors.append("utils.py: missing function get_localized_strings")

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
                if isinstance(node, ast.FunctionDef):
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
