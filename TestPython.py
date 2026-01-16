import random
import string
import pyperclip

def generate_custom_password():
    """Генерация пароля из 22 символов (6 спец.симв., 8 букв, 8 цифр)
    с гарантией, что пароль не начинается и не заканчивается спецсимволом"""

    # Убираем нежелательные символы
    forbidden_chars = ['#', '"', "'", '\\', '/', '|', '}', '{', '[', ']', '~', '`']
    special_chars = [c for c in string.punctuation if c not in forbidden_chars]

    # Генерируем компоненты пароля
    uppercase = random.choices(string.ascii_uppercase, k=4)
    lowercase = random.choices(string.ascii_lowercase, k=4)
    digits = random.choices(string.digits.replace('0', ''), k=8)
    symbols = random.choices(special_chars, k=6)

    # Собираем и перемешиваем
    password = uppercase + lowercase + digits + symbols
    random.shuffle(password)

    # Проверяем первый и последний символы
    if password[0] in special_chars:
        # Ищем букву или цифру для замены
        for i, char in enumerate(password):
            if char not in special_chars:
                password[0], password[i] = password[i], password[0]
                break

    if password[-1] in special_chars:
        # Ищем букву или цифру для замены
        for i, char in enumerate(password):
            if char not in special_chars:
                password[-1], password[i] = password[i], password[-1]
                break

    return ''.join(password)


def main():
    print("\n🔒 Генератор надёжных паролей 🔒")
    print("Сгенерировано 10 паролей:")

    passwords = [generate_custom_password() for _ in range(10)]

    for i, pwd in enumerate(passwords, 1):
        print(f"{i:2d}. {pwd}")

    while True:
        choice = input("\nВыберите номер пароля (1-10) или нажмите Enter для выхода: ").strip()

        if not choice:
            print("Выход...")
            break

        try:
            choice = int(choice)
            if 1 <= choice <= 10:
                selected = passwords[choice - 1]
                pyperclip.copy(selected)
                print(f"✓ Скопировано: {selected}")
            else:
                print("Ошибка! Число должно быть от 1 до 10")
        except ValueError:
            print("Ошибка! Введите число от 1 до 10")


if __name__ == "__main__":
    main()
