#!/usr/bin/env python
import os
import platform
import random
import shlex
import string
import subprocess
import sys
from pathlib import Path

YELLOW = "\033[33m"
RESET = "\033[0m"


def log(message: str) -> None:
    print(f"{YELLOW}{message}{RESET}")


def run_command(command: str, env: dict | None = None, use_bash: bool = False) -> None:
    log(f"{command}")
    subprocess.run(
        command,
        shell=True,
        check=True,
        env=env,
        executable="/bin/bash" if use_bash else None,
    )


def run_in_venv(command: str, env: dict | None = None) -> None:
    if IS_WINDOWS:
        activate = VENV_DIR / "Scripts" / "activate.bat"
        full_command = f'call "{activate}" && {command}'
        run_command(full_command, env=env)
    else:
        activate = VENV_DIR / "bin" / "activate"
        full_command = f'. "{activate}" && {command}'
        run_command(full_command, env=env, use_bash=True)


ROOT_DIR = Path(__file__).resolve().parent
VENV_DIR = ROOT_DIR / "venv"
IS_WINDOWS = platform.system().lower().startswith("win")


def main() -> None:
    os.chdir(ROOT_DIR)
    log("Старт инициализации окружения.")

    if not VENV_DIR.exists():
        log("Создаю виртуальное окружение...")
        subprocess.run([sys.executable, "-m", "venv", str(VENV_DIR)], check=True)
    else:
        log("Виртуальное окружение уже существует.")

    log("Активирую venv и устанавливаю зависимости...")
    run_in_venv(f'python -m pip install -r "{ROOT_DIR / "requirements.txt"}"')

    log("Применяю миграции...")
    run_in_venv("python manage.py migrate --skip-checks")

    log("Загружаю данные аллергенов...")
    run_in_venv("python manage.py loaddata allergens.json --skip-checks")

    admin_password = "".join(
        random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(8)
    )
    log("Создаю суперпользователя...")

    env = os.environ.copy()
    env["ADMIN_PASSWORD"] = admin_password
    shell_script = (
        "import os; "
        "from django.contrib.auth import get_user_model; "
        "User = get_user_model(); "
        "email = 'admin@g.com'; "
        "password = os.environ['ADMIN_PASSWORD']; "
        "defaults = {'is_staff': True, 'is_superuser': True, 'role': 'admin_main'}; "
        "user, _ = User.objects.get_or_create(email=email, defaults=defaults); "
        "user.is_staff = True; user.is_superuser = True; user.role = 'admin_main'; "
        "user.set_password(password); "
        "user.save()"
    )

    if IS_WINDOWS:
        command = f'python manage.py shell -c "{shell_script}"'
    else:
        command = f"python manage.py shell -c {shlex.quote(shell_script)}"

    run_in_venv(command, env=env)

    log("Инициализация завершена!")
    log(f"Логин: admin@g.com")
    log(f"Пароль: {admin_password}")
    log("Запуск: python manage.py runserver")


if __name__ == "__main__":
    main()
