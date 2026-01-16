import secrets, threading, sys, hashlib, pyperclip

class SecureGenerator:
    def __init__(self, count=10, delay=20, length=24):
        # Валидация входных данных
        try:
            self.count = max(1, min(int(count), 50))
            self.delay = max(5, min(int(delay), 300))
            self.length = max(8, min(int(length), 128))
        except (ValueError, TypeError):
            sys.exit("\033[91m[!] Ошибка: Неверные параметры конфигурации.\033[0m")

        self.timer = None
        self.pwds = []
        self.hashes = {} # Хранение хэшей для верификации буфера
        self.masked = True
        
        # Набор символов без визуальных дублей
        chars = "abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789"
        self.pool = chars + "!@$%^&*()-_=+[]{}<>?"
        self.border = chars

    def _wipe(self):
        """Безопасное затирание и очистка хэшей"""
        for b in self.pwds:
            with memoryview(b) as m: m[:] = b'\x00' * len(b)
        self.pwds.clear()
        self.hashes.clear()

    def _gen(self):
        p = [secrets.choice(self.border)] + \
            [secrets.choice(self.pool) for _ in range(self.length - 2)] + \
            [secrets.choice(self.border)]
        pwd_str = "".join(p)
        # Сохраняем хэш для последующей проверки целостности буфера
        pwd_hash = hashlib.sha256(pwd_str.encode()).hexdigest()
        return bytearray(pwd_str, 'ascii'), pwd_hash

    def _clear_clip(self, expected_hash):
        """Очистка буфера на основе хэш-верификации"""
        try:
            current_content = pyperclip.paste()
            if hashlib.sha256(current_content.encode()).hexdigest() == expected_hash:
                pyperclip.copy("")
                sys.stdout.write(f"\r\033[K\033[91m[!] Буфер очищен (Hash Verified)\033[0m\n\033[96m>>> \033[0m")
                sys.stdout.flush()
        except Exception:
            pass # Ошибка доступа к буферу не должна прерывать поток

    def _draw(self):
        # ANSI очистка: универсальна для macOS, Linux, Windows 10+
        sys.stdout.write("\033[H\033[J")
        header = f"🔒 Secure Gen 2026 | L: {self.length} | Mask: {'ON' if self.masked else 'OFF'}"
        print(f"\033[1;96m{header}\033[0m")
        for i, p in enumerate(self.pwds, 1):
            val = "•" * self.length if self.masked else p.decode()
            print(f"\033[92m{i:2d}.\033[0m {val}")
        print(f"\n\033[93m[1-{self.count}]\033[0m Копировать | \033[93m[V]\033[0m Маска | \033[93m[R]\033[0m Обновить | \033[93m[Enter]\033[0m Выход")

    def run(self):
        try:
            while True:
                if not self.pwds:
                    for _ in range(self.count):
                        p_ba, p_hash = self._gen()
                        self.pwds.append(p_ba)
                        self.hashes[id(p_ba)] = p_hash
                
                self._draw()
                
                while True:
                    try:
                        raw_input = input("\033[96m>>> \033[0m").strip().lower()
                    except EOFError: self.exit()
                    
                    if not raw_input: self.exit()
                    if raw_input == 'r': self._wipe(); break
                    if raw_input == 'v': self.masked = not self.masked; self._draw(); continue
                    
                    if raw_input.isdigit():
                        idx = int(raw_input)
                        if 1 <= idx <= self.count:
                            target_ba = self.pwds[idx-1]
                            p_str = target_ba.decode()
                            p_hash = self.hashes[id(target_ba)]
                            
                            try:
                                pyperclip.copy(p_str)
                                if self.timer: self.timer.cancel()
                                self.timer = threading.Timer(self.delay, self._clear_clip, [p_hash])
                                self.timer.start()
                                print(f"\033[1A\033[K\033[92m✓ #{idx} хэширован и скопирован ({self.delay}s)\033[0m")
                            except Exception as e:
                                print(f"\033[91m[!] Ошибка буфера: {e}\033[0m")
                        continue
                    print(f"\033[1A\033[K\033[91m[!] Ошибка ввода\033[0m")
        except KeyboardInterrupt: self.exit()

    def exit(self):
        if self.timer: self.timer.cancel()
        try: pyperclip.copy("")
        except: pass
        self._wipe()
        sys.exit("\n\033[1;91m[!] Сессия завершена. Память очищена.\033[0m")

if __name__ == "__main__":
    SecureGenerator().run()
