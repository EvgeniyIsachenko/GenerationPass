import secrets, threading, sys, time, pyperclip, argparse, gc

class SecureGenerator:
    def __init__(self, length=24, delay=20, count=10):
        self.l, self.d, self.c = length, delay, count
        self.timer_lock = threading.Lock()
        self.pwds, self.masked = [], True
        self.remaining = -1
        self.active_val = None
        self.chars = "abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789"
        self.pool = self.chars + "!@$%^&*()-_=+[]{}<>?"

    def _wipe(self):
        for b in self.pwds:
            if isinstance(b, bytearray):
                for i in range(len(b)): b[i] = 0
        self.pwds.clear()
        self.active_val = None
        gc.collect()

    def _gen(self):
        p = [secrets.choice(self.chars)] + \
            [secrets.choice(self.pool) for _ in range(self.l - 2)] + \
            [secrets.choice(self.chars)]
        return bytearray("".join(p), 'utf-8')

    def _get_color(self, t):
        if t > self.d * 0.5: return "\033[1;32m"
        if t > self.d * 0.2: return "\033[1;33m"
        return "\033[1;31m"

    def _timer_thread(self):
        while True:
            time.sleep(1)
            with self.timer_lock:
                if self.remaining >= 0:
                    color = self._get_color(self.remaining)
                    if self.remaining > 0:
                        msg = f"{color}⏱ ОЧИСТКА БУФЕРА: {self.remaining}с\033[0m"
                        self.remaining -= 1
                    else:
                        msg = "\033[1;31m[!] БУФЕР ОБМЕНА ОЧИЩЕН\033[0m"
                        try:
                            if pyperclip.paste() == self.active_val:
                                pyperclip.copy("")
                        except: pass
                        self.active_val = None
                        self.remaining = -1
                    
                    sys.stdout.write(f"\033[s\033[6A\r\033[K{msg}\033[u")
                    sys.stdout.flush()

    def _draw(self):
        sys.stdout.write("\033[H\033[J")
        print(f"\033[1;36m🔒 Secure Gen 2026 | L:{self.l} | D:{self.d}s | Mask:{'ON' if self.masked else 'OFF'}\033[0m\n")
        for i, p in enumerate(self.pwds, 1):
            val = '•' * self.l if self.masked else p.decode('utf-8')
            print(f"\033[1;32m{i:2d}.\033[0m {val}")
        
        print("\r")      # Строка ТАЙМЕРА
        print("\n\r")    # Одна пустая строка зазора
        # Теперь "Меню:" выводится обычным белым цветом (\033[0m)
        print(f"\033[0mМеню:\033[0m")
        print(f" \033[93m[1-{self.c}]\033[0m Копировать  \033[93m[V]\033[0m Маска  \033[93m[R]\033[0m Обновить  \033[93m[Enter]\033[0m Выход")
        print("\n\r")    # Пустая строка для уведомления
        print(f"\033[96m>>> \033[0m", end="")
        sys.stdout.flush()

    def run(self):
        threading.Thread(target=self._timer_thread, daemon=True).start()
        try:
            while True:
                if not self.pwds: self.pwds = [self._gen() for _ in range(self.c)]
                self._draw()
                while True:
                    try: cmd = input().strip().lower()
                    except EOFError: self.exit()
                    sys.stdout.write("\033[A\033[K")
                    
                    if not cmd: self.exit()
                    if cmd == 'r': 
                        with self.timer_lock: self.remaining = -1
                        self._wipe(); break
                    if cmd == 'v': 
                        self.masked = not self.masked; self._draw(); continue
                    
                    if cmd.isdigit() and 1 <= (idx := int(cmd)) <= self.c:
                        s = self.pwds[idx-1].decode('utf-8')
                        pyperclip.copy(s)
                        with self.timer_lock:
                            self.active_val = s
                            self.remaining = self.d
                        msg = f"\033[1;32m✓ Пароль #{idx} в буфере\033[0m"
                    else:
                        msg = f"\033[1;31m❌ Ошибка: используйте команды из Меню\033[0m"
                    
                    sys.stdout.write(f"\033[s\033[1A\r\033[K{msg}\033[u\033[96m>>> \033[0m")
                    sys.stdout.flush()
        except KeyboardInterrupt: self.exit()

    def exit(self):
        self._wipe()
        try: pyperclip.copy("")
        except: pass
        sys.exit("\n\033[1;91m[!] Сессия закрыта. RAM очищена.\033[0m")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--length", type=int, default=24)
    parser.add_argument("-d", "--delay", type=int, default=20)
    parser.add_argument("-c", "--count", type=int, default=10)
    args = parser.parse_args()
    SecureGenerator(args.length, args.delay, args.count).run()
