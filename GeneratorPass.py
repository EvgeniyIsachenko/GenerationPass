import secrets
import string
import pyperclip
import threading
import time

def generate_custom_password():
    forbidden = set('#"\'\\/|}[{~`')
    special_chars = "".join(c for c in string.punctuation if c not in forbidden)
    
    letters = [secrets.choice(string.ascii_uppercase) for _ in range(4)] + \
              [secrets.choice(string.ascii_lowercase) for _ in range(4)]
    digits = [secrets.choice(string.digits.replace('0', '')) for _ in range(8)]
    symbols = [secrets.choice(special_chars) for _ in range(6)]
    
    pool_non_special = letters + digits
    secrets.SystemRandom().shuffle(pool_non_special)
    
    prefix = pool_non_special.pop()
    suffix = pool_non_special.pop()
    
    middle_part = pool_non_special + symbols
    secrets.SystemRandom().shuffle(middle_part)
    
    return f"{prefix}{''.join(middle_part)}{suffix}"

def clear_clipboard_timer(delay, password_to_clear):
    """Очищает буфер обмена через N секунд, если там все еще этот пароль"""
    time.sleep(delay)
    # Проверяем, что в буфере всё еще тот же пароль (чтобы не стереть новый скопированный)
    if pyperclip.paste() == password_to_clear:
        pyperclip.copy("")
        print("\n[!] Буфер обмена очищен в целях безопасности.")

def main():
    print("\n🔒 Генератор паролей с автоочисткой буфера 🔒")
    COUNT = 10
    CLEANUP_DELAY = 20 # Секунд до очистки
    
    passwords = [generate_custom_password() for _ in range(COUNT)]

    for i, pwd in enumerate(passwords, 1):
        print(f"{i:2d}. {pwd}")

    while True:
        choice = input(f"\nВыбор (1-{COUNT}) или Enter для выхода: ").strip()
        
        if not choice:
            break

        if choice.isdigit():
            idx = int(choice)
            if 1 <= idx <= COUNT:
                selected = passwords[idx - 1]
                pyperclip.copy(selected)
                print(f"✓ Скопировано! Буфер будет очищен через {CLEANUP_DELAY} сек.")
                
                # Запуск фонового потока для очистки
                threading.Thread(
                    target=clear_clipboard_timer, 
                    args=(CLEANUP_DELAY, selected), 
                    daemon=True
                ).start()
                continue
        
        print(f"Ошибка! Введите число от 1 до {COUNT}")

if __name__ == "__main__":
    main()
