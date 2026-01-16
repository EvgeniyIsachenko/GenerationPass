import secrets, threading, sys

# Проверка наличия библиотеки pyperclip
try:
    import pyperclip
except ImportError:
    sys.exit("\033[91m[!] Ошибка: Библиотека 'pyperclip' не найдена.\n[i] Установите её командой: pip install pyperclip\033[0m")

class SecureGenerator:
    def __init__(self, length=24, delay=20, count=10):
        try:
            self.l, self.d, self.c = int(length), int(delay), int(count)
        except: 
            # Значения по умолчанию, если аргументы переданы неверно
            self.l, self.d, self.c = 24, 20, 10
        
        self.timer, self.pwds, self.masked = None, [], True
        self.chars = "abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789"
        self.pool = self.chars + "!@$%^&*()-_=+[]{}<>?"

    def _wipe(self):
        """Физическое затирание данных в RAM"""
        for b in self.pwds:
            with memoryview(b) as m: m[:] = b'\x00' * len(b)
        self.pwds.clear()

    def _gen(self):
        p = [secrets.choice(self.chars)] + \
            [secrets.choice(self.pool) for _ in range(self.l - 2)] + \
            [secrets.choice(self.chars)]
        return bytearray("".join(p), 'ascii')

    def _clear(self, val):
        if pyperclip.paste() == val:
            pyperclip.copy("")
            sys.stdout.write(f"\r\033[K\033[91m[!] Буфер очищен\033[0m\n\033[96m>>> \033[0m")
            sys.stdout.flush()

    def _draw(self):
        sys.stdout.write("\033[H\033[J")
        print(f"\033[1;36m🔒 Secure 2026 | L:{self.l} D:{self.d}s | Mask:{'ON' if self.masked else 'OFF'}\033[0m")
        for i, p in enumerate(self.pwds, 1):
            print(f"\033[92m{i:2d}.\033[0m {'•'*self.l if self.masked else p.decode()}")
        print(f"\n\033[93m[1-{self.c}]\033[0m Копи | \033[93m[V]\033[0m Маска | \033[93m[R]\033[0m Обновить | \033[93m[Enter]\033[0m Выход")

    def run(self):
        try:
            while True:
                if not self.pwds: self.pwds = [self._gen() for _ in range(self.c)]
                self._draw()
                while True:
                    try:
                        cmd = input("\033[96m>>> \033[0m").strip().lower()
                    except EOFError: self.exit()
                    
                    if not cmd: self.exit()
                    if cmd == 'r': self._wipe(); break
                    if cmd == 'v': self.masked = not self.masked; self._draw(); continue
                    if cmd.isdigit() and 1 <= (idx := int(cmd)) <= self.c:
                        s = self.pwds[idx-1].decode()
                        pyperclip.copy(s)
                        if self.timer: self.timer.cancel()
                        self.timer = threading.Timer(self.d, self._clear, [s])
                        self.timer.start()
                        print(f"\033[1A\033[K\033[92m✓ #{idx} скопирован ({self.d}s)\033[0m")
        except KeyboardInterrupt: self.exit()

    def exit(self):
        if self.timer: self.timer.cancel()
        try: pyperclip.copy("")
        except: pass
        self._wipe()
        sys.exit("\n\033[91m[!] Данные затерты. Сессия закрыта.\033[0m")

if __name__ == "__main__":
    # Обработка аргументов командной строки
    args = sys.argv[1:]
    # Распаковываем аргументы, если они есть, иначе используем значения по умолчанию
    gen = SecureGenerator(*args[:3]) if args else SecureGenerator()
    gen.run()
