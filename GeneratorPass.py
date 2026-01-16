import secrets, string, pyperclip, threading, time, os, sys  # Импорт системных модулей


class Colors:
    """Класс для хранения ANSI-кодов цветов терминала."""
    GREEN, YELLOW, RED, CYAN = '\033[92m', '\033[93m', '\033[91m', '\033[96m'
    BOLD, END = '\033[1m', '\033[0m'


class SecureGenerator:
    """Основной класс генератора паролей."""

    def __init__(self, count=10, delay=20):
        self.count = count  # Количество генерируемых паролей за раз
        self.delay = delay  # Задержка перед очисткой буфера обмена
        self.passwords_ba = []  # Список для хранения паролей в виде bytearray (для очистки памяти)
        self.last_id = 0  # ID последней операции копирования для предотвращения Race Condition
        self.forbidden = set('#"\'\\/|}[{~`lI1O0')  # Набор исключаемых символов (плохо читаемые)

        # Предварительная подготовка наборов символов
        self.chars = {
            'up': [c for c in string.ascii_uppercase if c not in self.forbidden],
            'low': [c for c in string.ascii_lowercase if c not in self.forbidden],
            'dig': [c for c in string.digits if c not in self.forbidden],
            'sp': [c for c in string.punctuation if c not in self.forbidden]
        }
        # Общий список всех разрешенных символов
        self.all_allowed = self.chars['up'] + self.chars['low'] + self.chars['dig'] + self.chars['sp']

    def secure_zero(self):
        """Метод физического затирания данных в оперативной памяти."""
        for ba in self.passwords_ba:
            if ba:
                for i in range(len(ba)): ba[i] = 0  # Записываем нули в каждый байт массива
        self.passwords_ba.clear()  # Очищаем сам список

    def generate_one(self, length=22):
        """Создает один криптостойкий пароль."""
        # Гарантируем наличие минимум одного символа из каждого набора
        pwd = [secrets.choice(self.chars[k]) for k in self.chars]
        # Добираем оставшуюся длину случайными символами
        pwd += [secrets.choice(self.all_allowed) for _ in range(length - 4)]
        secrets.SystemRandom().shuffle(pwd)  # Перемешиваем символы

        specials = set(string.punctuation)  # Набор спецсимволов для проверки краев
        for i in [0, -1]:  # Проверка первого и последнего символов
            if pwd[i] in specials:
                for j in range(1, len(pwd) - 1):
                    if pwd[j] not in specials:
                        pwd[i], pwd[j] = pwd[j], pwd[i]  # Меняем местами, если на краю спецсимвол
                        break
        return bytearray("".join(pwd), 'ascii')  # Возвращаем bytearray (изменяемый массив байтов)

    def refresh(self):
        """Обновляет текущий список паролей."""
        self.secure_zero()  # Сначала затираем старые пароли
        self.passwords_ba = [self.generate_one() for _ in range(self.count)]  # Генерируем новые

    def clipboard_timer(self, p_str, c_id):
        """Фоновый поток для очистки буфера обмена через заданное время."""
        time.sleep(self.delay)  # Ждем указанное количество секунд
        # Очищаем буфер только если это была последняя копия
        if self.last_id == c_id and pyperclip.paste() == p_str:
            pyperclip.copy("")  # Очищаем буфер обмена
            sys.stdout.write(f"\r\x1b[2K{Colors.RED}[!] Буфер очищен{Colors.END}\n{Colors.CYAN}>>> {Colors.END}")
            sys.stdout.flush()

    def exit_gracefully(self):
        """Метод безопасного завершения работы скрипта."""
        if sys.platform == 'darwin':  # Если запуск на macOS
            os.system('echo "" | pbcopy')  # Очищаем буфер через системную команду pbcopy
            try:
                import termios  # Импорт модуля для работы с терминалом Unix
                termios.tcflush(sys.stdin, termios.TCIFLUSH)  # Сбрасываем очередь ввода (удаляем 'r')
            except:
                pass
        self.secure_zero()  # Затираем пароли в ОЗУ перед выходом
        print(f"\r{Colors.RED}[!] Данные стерты. Выход.{Colors.END}")
        os._exit(0)  # Мгновенный выход из процесса на уровне ОС

    def run(self):
        """Основной цикл работы программы."""
        while True:
            self.refresh()  # Генерируем пароли
            os.system('clear' if os.name == 'posix' else 'cls')  # Чистим экран терминала
            print(f"{Colors.BOLD}{Colors.CYAN}🔒 Secure Gen | Jan 2026 | MAC-SAFE 🔒{Colors.END}")

            for i, ba in enumerate(self.passwords_ba, 1):
                # Декодируем байты в строку только для вывода на экран
                print(f"{Colors.GREEN}{i:2d}.{Colors.END} {ba.decode('ascii')}")

            print(
                f"\n{Colors.YELLOW}[R]{Colors.END} Обновить | {Colors.YELLOW}[1-10]{Colors.END} Копировать | {Colors.YELLOW}[Enter]{Colors.END} Выход")

            while True:
                try:
                    cmd = input(f"{Colors.CYAN}>>> {Colors.END}").strip().lower()
                except:
                    self.exit_gracefully()  # Выход при Ctrl+C

                if not cmd: self.exit_gracefully()  # Выход при пустом Enter
                if cmd == 'r': break  # Переход к обновлению

                if cmd.isdigit() and 1 <= int(cmd) <= self.count:
                    idx = int(cmd)
                    p_str = self.passwords_ba[idx - 1].decode('ascii')
                    self.last_id += 1
                    pyperclip.copy(p_str)
                    # Стираем предыдущую строку ввода и пишем статус
                    sys.stdout.write(f"\x1b[1A\x1b[2K{Colors.GREEN}✓ #{idx} скопирован{Colors.END}\n")
                    threading.Thread(target=self.clipboard_timer, args=(p_str, self.last_id), daemon=True).start()
                else:
                    sys.stdout.write(f"{Colors.RED}Ошибка!{Colors.END}\n")


if __name__ == "__main__":
    SecureGenerator().run()
