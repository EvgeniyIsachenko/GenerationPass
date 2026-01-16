import secrets
import string
import pyperclip
import threading
import time
import os
import sys
<<<<<<< HEAD
=======
import atexit
>>>>>>> main
import subprocess

class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

<<<<<<< HEAD
# Глобальные переменные
CLEANUP_DELAY = 20
COUNT = 10
passwords = []  # Храним строки, а не bytearray (проще для демонстрации)
cleanup_event = threading.Event()  # Сигнал для потоков очистки

def secure_zeroing(str_list):
    """Обнуление строк в памяти (упрощённо)"""
    for s in str_list:
        # В Python строки неизменяемы, поэтому просто очищаем список
        pass  # Реальная очистка требует ctypes/ctypes.memset
    str_list.clear()

def final_cleanup():
    """Финальная очистка перед выходом"""
    # 1. Очистить буфер обмена
    try:
        pyperclip.copy("")
    except:
        pass

    # 2. Очистить пароли
    secure_zeroing(passwords)

    # 3. Вывести сообщение
    sys.stdout.write(f"\n{Colors.RED}[!] Сессия закрыта. Данные удалены.{Colors.END}\n")
    sys.stdout.flush()

    # 4. Установить событие для всех потоков
    cleanup_event.set()

def generate_password(length=22):
    ambiguous = 'lI1O0'
    forbidden = set('#"\'\\/|}[{~`' + ambiguous)
    up = [c for c in string.ascii_uppercase if c not in forbidden]
    low = [c for c in string.ascii_lowercase if c not in forbidden]
    dig = [c for c in string.digits if c not in forbidden]
    sp = [c for c in string.punctuation if c not in forbidden]
    all_chars = up + low + dig + sp

    pwd = [
        secrets.choice(up),
        secrets.choice(low),
        secrets.choice(dig),
        secrets.choice(sp)
    ]
    pwd += [secrets.choice(all_chars) for _ in range(length - 4)]
    secrets.SystemRandom().shuffle(pwd)

    # Фикс краев: спецсимвол не на краях
    for i in [0, -1]:
        if pwd[i] in sp:
            for j in range(1, len(pwd) - 1):
                if pwd[j] not in sp:
                    pwd[i], pwd[j] = pwd[j], pwd[i]
                    break

    return "".join(pwd)

def clipboard_manager(delay, password_str, copy_id):
    """Поток для очистки буфера через delay секунд"""
    try:
        # Ждём либо таймаут, либо сигнал завершения
        if not cleanup_event.wait(timeout=delay):
            # Если не было сигнала завершения — очищаем буфер
            try:
                if pyperclip.paste() == password_str:
                    pyperclip.copy("")
                    sys.stdout.write(
                        f"\r{Colors.RED}[!] Буфер очищен{Colors.END}        \n"
                    )
                    sys.stdout.flush()
            except:
                pass
    except:
        pass

def main():
    global passwords

    try:
        while True:
            # 1. Очищаем старые данные
            secure_zeroing(passwords)
            passwords.clear()

            # 2. Генерируем новые пароли
            passwords = [generate_password() for _ in range(COUNT)]

            # 3. Отображаем интерфейс
            os.system('clear' if os.name == 'posix' else 'cls')
            print(f"{Colors.BOLD}{Colors.CYAN}🔒 Secure Gen 2026 | MAC-FIX 🔒{Colors.END}")

            for i, pwd in enumerate(passwords, 1):
                print(f"{Colors.GREEN}{i:2d}.{Colors.END} {pwd}")

            print(f"\n{Colors.YELLOW}[R]{Colors.END} Обновить | "
                  f"{Colors.YELLOW}[1-{COUNT}]{Colors.END} Копировать | "
                  f"{Colors.YELLOW}[Enter]{Colors.END} Выход")

            # 4. Обрабатываем ввод
            try:
                user_input = input(f"{Colors.CYAN}>>> {Colors.END}").strip().lower()
            except (KeyboardInterrupt, EOFError):
                final_cleanup()
                return

            if not user_input:  # Нажатие Enter — выход
                final_cleanup()
                return

            if user_input == 'r':  # Обновить пароли
                continue

            if user_input.isdigit():
                idx = int(user_input)
                if 1 <= idx <= COUNT:
                    selected = passwords[idx - 1]
                    pyperclip.copy(selected)
                    print(f"{Colors.GREEN}✓ #{idx} в буфере!{Colors.END}")

                    # Запускаем поток очистки с уникальным ID
                    threading.Thread(
                        target=clipboard_manager,
                        args=(CLEANUP_DELAY, selected, idx),
                        daemon=True
                    ).start()
                    continue

            print(f"{Colors.RED}Ошибка! Выберите 1-{COUNT}, R или Enter.{Colors.END}")

    finally:
        # Гарантированная очистка при выходе из main()
        final_cleanup()
=======
last_copy_id = 0
passwords_ba = []
CLEANUP_DELAY = 20
COUNT = 10

def secure_zeroing(ba_list):
    for ba in ba_list:
        if ba:
            for i in range(len(ba)):
                ba[i] = 0
    ba_list.clear()

def final_cleanup_and_kill():
    """Максимально жесткая очистка и выход."""
    # 1. Стираем буфер обмена (нативная команда macOS)
    if sys.platform == 'darwin':
        os.system('echo "" | pbcopy')
    
    # 2. Стираем пароли в ОЗУ
    global passwords_ba
    secure_zeroing(passwords_ba)
    
    # 3. Очищаем буфер терминала через stty
    if sys.platform == 'darwin':
        subprocess.run(['stty', 'echo', 'icanon'], capture_output=True)
    
    sys.stdout.write(f"\r{Colors.RED}[!] Сессия закрыта. Данные удалены.{Colors.END}\n")
    sys.stdout.flush()
    
    # Используем исключение для гарантированного выхода из main()
    raise SystemExit("Завершение работы")

def generate_secure_bytearray(length=22):
    ambiguous = 'lI1O0'
    forbidden = set('#"\'\\/|}[{~`' + ambiguous)
    l_up = [c for c in string.ascii_uppercase if c not in forbidden]
    l_low = [c for c in string.ascii_lowercase if c not in forbidden]
    dig = [c for c in string.digits if c not in forbidden]
    sp = [c for c in string.punctuation if c not in forbidden]
    all_a = l_up + l_low + dig + sp
    
    pwd = [secrets.choice(l_up), secrets.choice(l_low), secrets.choice(dig), secrets.choice(sp)]
    pwd += [secrets.choice(all_a) for _ in range(length - 4)]
    secrets.SystemRandom().shuffle(pwd)
    
    for i in [0, -1]:
        if pwd[i] in sp:
            for j in range(1, len(pwd)-1):
                if pwd[j] not in sp:
                    pwd[i], pwd[j] = pwd[j], pwd[i]
                    break
    ba = bytearray("".join(pwd), 'ascii')
    return ba

def clipboard_manager(delay, password_str, current_id):
    global last_copy_id
    time.sleep(delay)
    try:
        if last_copy_id == current_id and pyperclip.paste() == password_str:
            pyperclip.copy("")
            sys.stdout.write(f"\x1b[s\r\x1b[2K{Colors.RED}[!] Буфер очищен{Colors.END}\x1b[u")
            sys.stdout.flush()
    except: pass

def main():
    global last_copy_id, passwords_ba
    
    try:
        while True:
            secure_zeroing(passwords_ba)
            os.system('clear' if os.name == 'posix' else 'cls')
            print(f"{Colors.BOLD}{Colors.CYAN}🔒 Secure Gen 2026 | MAC-FIX 🔒{Colors.END}")
            
            for _ in range(COUNT):
                passwords_ba.append(generate_secure_bytearray())

            for i, ba in enumerate(passwords_ba, 1):
                print(f"{Colors.GREEN}{i:2d}.{Colors.END} {ba.decode('ascii')}")

            print(f"\n{Colors.YELLOW}[R]{Colors.END} Обновить | {Colors.YELLOW}[1-10]{Colors.END} Копировать | {Colors.YELLOW}[Enter]{Colors.END} Выход")
            
            while True:
                try:
                    user_input = input(f"{Colors.CYAN}>>> {Colors.END}").strip().lower()
                except (KeyboardInterrupt, EOFError):
                    final_cleanup_and_kill()

                if not user_input:
                    final_cleanup_and_kill()
                
                if user_input == 'r':
                    break  # Уходим на новый круг генерации
                
                if user_input.isdigit():
                    idx = int(user_input)
                    if 1 <= idx <= COUNT:
                        sel_str = passwords_ba[idx-1].decode('ascii')
                        last_copy_id += 1
                        pyperclip.copy(sel_str)
                        print(f"{Colors.GREEN}✓ #{idx} в буфере!{Colors.END}")
                        threading.Thread(target=clipboard_manager, args=(CLEANUP_DELAY, sel_str, last_copy_id), daemon=True).start()
                        continue
                
                print(f"{Colors.RED}Ошибка!{Colors.END}")
    except SystemExit:
        # Гарантированно завершаем main()
        return
>>>>>>> main

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
<<<<<<< HEAD
        final_cleanup()
    except SystemExit:
        pass
    finally:
        # Финальный выход
        sys.exit(0)
=======
        print(f"\n{Colors.RED}Программа закрыта.{Colors.END}")
>>>>>>> main
