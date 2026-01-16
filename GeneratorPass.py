import secrets, string, threading, time, os, sys

# Проверка зависимости перед запуском
try:
    import pyperclip
except ImportError:
    print("\033[91m[!] Ошибка: Установите библиотеку pyperclip: pip install pyperclip\033[0m")
    sys.exit(1)

class Colors:
    GREEN, YELLOW, RED, CYAN = '\033[92m', '\033[93m', '\033[91m', '\033[96m'
    BOLD, END = '\033[1m', '\033[0m'

class SecureGenerator:
    def __init__(self, count=10, delay=20, pwd_length=22):
        self.count = count
        self.delay = delay
        self.pwd_length = pwd_length
        self.passwords_ba = []
        self.last_timer = None # Для управления очередью очистки
        self.forbidden = set('#"\'\\/|}[{~`lI1O0')
        
        self.chars = {
            'up': [c for c in string.ascii_uppercase if c not in self.forbidden],
            'low': [c for c in string.ascii_lowercase if c not in self.forbidden],
            'dig': [c for c in string.digits if c not in self.forbidden],
            'sp': [c for c in string.punctuation if c not in self.forbidden]
        }
        self.all_allowed = sum(self.chars.values(), [])

    def secure_zero(self):
        for ba in self.passwords_ba:
            if ba:
                for i in range(len(ba)): ba[i] = 0
        self.passwords_ba.clear()

    def generate_one(self):
        # Гарантированный набор из 4 типов символов
        pwd = [secrets.choice(self.chars[k]) for k in self.chars]
        pwd += [secrets.choice(self.all_allowed) for _ in range(self.pwd_length - 4)]
        secrets.SystemRandom().shuffle(pwd)

        specials = set(string.punctuation)
        for i in [0, -1]:
            if pwd[i] in specials:
                for j in range(1, len(pwd)-1):
                    if pwd[j] not in specials:
                        pwd[i], pwd[j] = pwd[j], pwd[i]
                        break
        return bytearray("".join(pwd), 'ascii')

    def refresh(self):
        self.secure_zero()
        self.passwords_ba = [self.generate_one() for _ in range(self.count)]

    def clear_clipboard(self, p_str):
        """Метод очистки, вызываемый таймером"""
        try:
            if pyperclip.paste() == p_str:
                pyperclip.copy("")
                # Использование сохранения/восстановления позиции курсора
                sys.stdout.write(f"\033[s\r\033[K{Colors.RED}[!] Буфер очищен{Colors.END}\033[u")
                sys.stdout.flush()
        except: pass

    def exit_gracefully(self):
        if sys.platform == 'darwin':
            os.system('echo "" | pbcopy')
            try:
                import termios
                termios.tcflush(sys.stdin, termios.TCIFLUSH)
            except: pass
        self.secure_zero()
        print(f"\r{Colors.RED}[!] Данные стерты. Выход.{Colors.END}")
        os._exit(0)

    def run(self):
        while True:
            self.refresh()
            os.system('clear' if os.name == 'posix' else 'cls')
            print(f"{Colors.BOLD}{Colors.CYAN}🔒 Secure Gen 2026 | Длина: {self.pwd_length} 🔒{Colors.END}")

            for i, ba in enumerate(self.passwords_ba, 1):
                print(f"{Colors.GREEN}{i:2d}.{Colors.END} {ba.decode('ascii')}")

            print(f"\n{Colors.YELLOW}[R]{Colors.END} Обновить | {Colors.YELLOW}[1-{self.count}]{Colors.END} Копировать | {Colors.YELLOW}[Enter]{Colors.END} Выход")

            while True:
                try:
                    cmd = input(f"{Colors.CYAN}>>> {Colors.END}").strip().lower()
                except: self.exit_gracefully()

                if not cmd: self.exit_gracefully()
                if cmd == 'r': break

                if cmd.isdigit() and 1 <= int(cmd) <= self.count:
                    idx = int(cmd)
                    p_str = self.passwords_ba[idx - 1].decode('ascii')
                    
                    # Если был запущен прошлый таймер — отменяем его
                    if self.last_timer: self.last_timer.cancel()
                    
                    pyperclip.copy(p_str)
                    sys.stdout.write(f"\033[1A\033[K{Colors.GREEN}✓ #{idx} в буфере ({self.delay}с){Colors.END}\n")
                    
                    # Запуск нового таймера
                    self.last_timer = threading.Timer(self.delay, self.clear_clipboard, [p_str])
                    self.last_timer.start()
                else:
                    sys.stdout.write(f"{Colors.RED}Ошибка ввода!{Colors.END}\n")

if __name__ == "__main__":
    # Теперь можно легко менять настройки при создании объекта
    SecureGenerator(count=10, delay=20, pwd_length=24).run()
