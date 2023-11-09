from time import sleep

import requests # библиотека для https запросов
from bs4 import BeautifulSoup # библиотека BS для парсинга Html
import re # регулярные выражения
import sqlite3 # библиотека бд

# ссылка на сайт с которого будем парсить чаты телеграм
BASE_URL = "https://tgram.me/supergroups?page={}"

# Количество страниц, которое  будем перебирать на сайте
NUM_PAGES = 4 # вообще страниц 487, просто долго ждать придется результата

# путь к файлу, куда будем записывать ссылки
OUTPUT_FILE = "telegram_links.txt"

# путь к бд, куда будем записывать ссылки
DATABASE_FILE = "telegram_links.db"

def create_database(): # создаем бд
    conn = sqlite3.connect(DATABASE_FILE) # устанавливаем коннект с бд
    cursor = conn.cursor() # курсор для выполнения запросов
    # создаем таблицу если она не существует, записываем текст ссылки и время
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS links (
            link TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit() #сохраняем бд
    conn.close() #закрываем бд

def extract_links(url, output_file, conn):
    response = requests.get(url) # отправляем get запрос на url
    soup = BeautifulSoup(response.text, "html.parser") # создаем объект для BS(для парсинга)
    text = soup.get_text() # получаем текст HTML
    # регулярное выражение для поиска ссылки начинающейся с t.me
    telegram_links = re.findall(r'https://t\.me/\S+', text)

    # пока файл открыт, обходим все ссылки,
    # печатаем и записываем каждую в файл с новой строки
    with open(output_file, 'a') as file:
        for link in telegram_links:
            print(link)
            file.write(link + '\n')

    # аналогично для бд
    cursor = conn.cursor()
    for link in telegram_links:
        cursor.execute('''
            INSERT INTO links (link) VALUES (?)
        ''', (link,))
        print(f"Добавлена ссылка: {link}")

    conn.commit() # сохраняем изменения

# основная функция
def main():
    create_database() # создаем бз

    conn = sqlite3.connect(DATABASE_FILE)# подключения к бд
    # Очищаем содержимое файла перед началом записи
    with open(OUTPUT_FILE, 'w') as file:
        file.write('')

    # Перебираем все страницы с 1 по NUM_PAGES
    for page_number in range(1, NUM_PAGES + 1):
        # устанавливаем задержку в две секунды между действиями, чтобы не получить блок
        sleep(2)
        page_url = BASE_URL.format(page_number) # формируем url страницы
        print(f"Поиск на странице {page_number}...")
        extract_links(page_url, OUTPUT_FILE, conn) # извлекаем ссылку с текущей страницы

    # Закрытие подключения к базе данных
    conn.close()

    print(f"ссылки сохранены в файл: {OUTPUT_FILE}")
    print(f"ссылки сохранены в базу данных: {DATABASE_FILE}")

if __name__ == "__main__":
    main()
