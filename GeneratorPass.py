import secrets  # Криптографически безопасный генератор
import string
import pyperclip

def generate_custom_password():
    # Настройки
    forbidden = set('#"\'\\/|}[{~`')
    special_chars = "".join(c for c in string.punctuation if c not in forbidden)
    
    # 1. Формируем группы (используем secrets для безопасности)
    letters = [secrets.choice(string.ascii_uppercase) for _ in range(4)] + \
              [secrets.choice(string.ascii_lowercase) for _ in range(4)]
    digits = [secrets.choice(string.digits.replace('0', '')) for _ in range(8)]
    symbols = [secrets.choice(special_chars) for _ in range(6)]
    
    # Объединяем всё, кроме двух символов, которые точно пойдут на края
    # Чтобы края были случайными, сначала перемешаем все буквы и цифры
    pool_non_special = letters + digits
    secrets.SystemRandom().shuffle(pool_non_special)
    
    # Забираем два гарантированных не-спецсимвола для краев
    prefix = pool_non_special.pop()
    suffix = pool_non_special.pop()
    
    # Остальное (14 не-спецсимволов + 6 спецсимволов) перемешиваем для середины
    middle_part = pool_non_special + symbols
    secrets.SystemRandom().shuffle(middle_part)
    
    # Собираем итоговую строку
    return f"{prefix}{''.join(middle_part)}{suffix}"

def main():
    print("\n🔒 Генератор криптостойких паролей 🔒")
    COUNT = 10
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
                print(f"✓ Скопировано в буфер!")
                continue
        
        print(f"Ошибка! Введите число от 1 до {COUNT}")

if __name__ == "__main__":
    main()
