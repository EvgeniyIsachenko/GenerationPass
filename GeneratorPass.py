import secrets, threading, sys, time, pyperclip

class SecureGenerator:
    def __init__(self, length=24, delay=20, count=10):
        try:
            self.l, self.d, self.c = int(length), int(delay), int(count)
        except: self.l, self.d, self.c = 24, 20, 10
        
        self.timer_lock = threading.Lock()
        self.pwds, self.masked = [], True
        self.remaining = 0
        self.active_val = ""
        self.chars = "abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789"
        self.pool = self.chars + "!@$%^&*()-_=+[]{}<>?"

    def _wipe(self):
        """Затирание данных в RAM"""
        for b in self.pwds:
            with memoryview(b) as m: m[:] = b'\x00' * len(b)
        self.pwds.clear()

    def _gen(self):
        """Криптостойкая генерация"""
        p = [secrets.choice(self.chars)] + \
            [secrets.choice(self.pool) for _ in range(self.l - 2)] + \
            [secrets.choice(self.chars)]
        return bytearray("".join(p), 'utf-8')

    def _get_color(self, t):
        if t > self.d * 0.5: return "\033[1;32m"
        if t > self.d * 0.2: return "\033[1;33m"
        return "\033[1;31m"

    def _timer_thread(self):
        """Независимый поток таймера"""
        while True:
            time.sleep(1)
            with self.timer_lock:
                row = self.c + 3 
                if self.remaining > 0:
                    self.remaining -= 1
                    color = self._get_color(self.remaining)
                    if self.remaining > 0:
                        sys.stdout.write(f"\033[s\033[{row};0H\033[K{color}⏱ ОЧИСТКА БУФЕРА: {self.remaining}с\033[0m\033[u")
                    else:
                        if pyperclip.paste() == self.active_val:
                            pyperclip.copy("")
                        sys.stdout.write(f"\033[s\033[{row};0H\033[K\033[1;31m[!] БУФЕР ОБМЕНА ОЧИЩЕН\033[0m\033[u")
                        self.active_val = ""
                    sys.stdout.flush()

    def _draw(self):
        """Отрисовка основного интерфейса"""
        sys.stdout.write("\033[H\033[J")
        print(f"\033[1;36m🔒 Secure Gen | L:{self.l} D:{self.d}s | Mask:{'ON' if self.masked else 'OFF'}\033[0m")
        for i, p in enumerate(self.pwds, 1):
            val = '•'*self.l if self.masked else p.decode('utf-8')
            print(f"\033[92m{i:2d}.\033[0m {val}")
        
        print("\n\n") # Зазор под таймер
        print(f"\033[93m[1-{self.c}]\033[0m Копировать | \033[93m[V]\033[0m Маска | \033[93m[R]\033[0m Обновить | \033[93m[Enter]\033[0m Выход")
        print("\n\n\033[96m>>> \033[0m", end="") # Две пустые строки: одна для отступа, одна для уведомления
        sys.stdout.flush()

    def run(self):
        threading.Thread(target=self._timer_thread, daemon=True).start()
        try:
            while True:
                if not self.pwds: self.pwds = [self._gen() for _ in range(self.c)]
                self._draw()
                while True:
                    cmd = input().strip().lower()
                    if not cmd: self.exit()
                    
                    # Стираем ввод пользователя
                    sys.stdout.write("\033[A\033[K")
                    
                    if cmd == 'r': 
                        with self.timer_lock: self.remaining = 0
                        self._wipe(); break
                    if cmd == 'v': 
                        self.masked = not self.masked; self._draw(); continue
                    
                    if cmd.isdigit() and 1 <= (idx := int(cmd)) <= self.c:
                        s = self.pwds[idx-1].decode('utf-8')
                        pyperclip.copy(s)
                        with self.timer_lock:
                            self.active_val = s
                            self.remaining = self.d
                        # \033[2A поднимает на 2 строки: 
                        # строка 1 (под меню) - пустая
                        # строка 2 (над >>>) - уведомление
                        sys.stdout.write(f"\r\033[1A\033[K\033[1;32m✓ Пароль #{idx} скопирован в буфер\033[0m\n\033[96m>>> \033[0m")
                        sys.stdout.flush()
                        continue
                    
                    sys.stdout.write("\033[96m>>> \033[0m")
                    sys.stdout.flush()
        except (KeyboardInterrupt, EOFError): self.exit()

    def exit(self):
        with self.timer_lock: self.remaining = 0
        try: pyperclip.copy("")
        except: pass
        self._wipe()
        sys.exit("\n\033[1;91m[!] Сессия закрыта. RAM очищена.\033[0m")

if __name__ == "__main__":
    SecureGenerator(*sys.argv[1:4]).run()
