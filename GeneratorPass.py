import secrets, threading, sys, hashlib, pyperclip

class SecureGenerator:
<<<<<<< HEAD
    def __init__(self, length=24, delay=20, count=10):
        # Строгая валидация входных данных
        try:
            self.length = max(8, min(int(length), 128))
            self.delay = max(5, min(int(delay), 300))
            self.count = max(1, min(int(count), 50))
        except (ValueError, TypeError):
            sys.exit("\033[91m[!] Ошибка: Параметры должны быть числами.\033[0m")

        self.timer = None
        self.pwds = []
        self.hashes = {} 
        self.masked = True
        
        # Набор символов исключает похожие (l, I, 1, O, 0)
=======
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
>>>>>>> main
        chars = "abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789"
        self.pool = chars + "!@$%^&*()-_=+[]{}<>?"
        self.border = chars

    def _wipe(self):
<<<<<<< HEAD
        """Физическое затирание данных в RAM и очистка хэшей"""
=======
        """Безопасное затирание и очистка хэшей"""
>>>>>>> main
        for b in self.pwds:
            with memoryview(b) as m: m[:] = b'\x00' * len(b)
        self.pwds.clear()
        self.hashes.clear()

<<<<<<< HEAD
    def _gen(self, idx):
        """Генерация с защитой краев и созданием проверочного хэша"""
=======
    def _gen(self):
>>>>>>> main
        p = [secrets.choice(self.border)] + \
            [secrets.choice(self.pool) for _ in range(self.length - 2)] + \
            [secrets.choice(self.border)]
        pwd_str = "".join(p)
<<<<<<< HEAD
        # Хэш нужен для верификации буфера перед очисткой
        self.hashes[idx] = hashlib.sha256(pwd_str.encode()).hexdigest()
        return bytearray(pwd_str, 'ascii')

    def _clear_clip(self, expected_hash):
        """Безопасная очистка: только если в буфере всё еще наш пароль"""
        try:
            if hashlib.sha256(pyperclip.paste().encode()).hexdigest() == expected_hash:
                pyperclip.copy("")
                sys.stdout.write(f"\r\033[K\033[91m[!] Буфер очищен\033[0m\n\033[96m>>> \033[0m")
=======
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
>>>>>>> main
                sys.stdout.flush()
        except Exception:
            pass # Ошибка доступа к буферу не должна прерывать поток

    def _draw(self):
<<<<<<< HEAD
        """Отрисовка интерфейса через ANSI-последовательности"""
        sys.stdout.write("\033[H\033[J") # Очистка экрана без os.system
        header = f"🔒 Secure Gen 2026 | L:{self.length} T:{self.delay}s | Mask:{'ON' if self.masked else 'OFF'}"
        print(f"\033[1;36m{header}\033[0m")
=======
        # ANSI очистка: универсальна для macOS, Linux, Windows 10+
        sys.stdout.write("\033[H\033[J")
        header = f"🔒 Secure Gen 2026 | Mask: {'ON' if self.masked else 'OFF'}"
        print(f"\033[1;96m{header}\033[0m")
>>>>>>> main
        for i, p in enumerate(self.pwds, 1):
            val = "•" * self.length if self.masked else p.decode()
            print(f"\033[92m{i:2d}.\033[0m {val}")
        print(f"\n\033[93m[1-{self.count}]\033[0m Копировать | \033[93m[V]\033[0m Маска | \033[93m[R]\033[0m Обновить | \033[93m[Enter]\033[0m Выход")

    def run(self):
        try:
            while True:
                if not self.pwds:
<<<<<<< HEAD
                    self.pwds = [self._gen(i+1) for i in range(self.count)]
                self._draw()
                while True:
                    try:
                        cmd = input("\033[96m>>> \033[0m").strip().lower()
                    except EOFError: self.exit()
                    
                    if not cmd: self.exit()
                    if cmd == 'r': self._wipe(); break
                    if cmd == 'v': self.masked = not self.masked; self._draw(); continue
                    
                    if cmd.isdigit() and 1 <= (idx := int(cmd)) <= self.count:
                        p_str = self.pwds[idx-1].decode()
                        pyperclip.copy(p_str)
                        # Перезапуск единственного активного таймера
                        if self.timer: self.timer.cancel()
                        self.timer = threading.Timer(self.delay, self._clear_clip, [self.hashes[idx]])
                        self.timer.start()
                        print(f"\033[1A\033[K\033[92m✓ #{idx} скопирован ({self.delay}s)\033[0m")
=======
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
>>>>>>> main
                        continue
                    print(f"\033[1A\033[K\033[91m[!] Ошибка ввода\033[0m")
        except KeyboardInterrupt: self.exit()

    def exit(self):
        if self.timer: self.timer.cancel()
<<<<<<< HEAD
        try: pyperclip.copy("") # Финальная очистка буфера
        except: pass
        self._wipe()
        sys.exit("\n\033[1;91m[!] Данные удалены из RAM. Сессия закрыта.\033[0m")
=======
        try: pyperclip.copy("")
        except: pass
        self._wipe()
        sys.exit("\n\033[1;91m[!] Сессия завершена. Память очищена.\033[0m")
>>>>>>> main

if __name__ == "__main__":
    # Запуск: python3 script.py [длина] [таймер] [количество]
    a = sys.argv[1:]
    SecureGenerator(
        length=a[0] if len(a) > 0 else 24,
        delay=a[1] if len(a) > 1 else 20,
        count=a[2] if len(a) > 2 else 10
    ).run()
