import json
import os
from difflib import SequenceMatcher


def read_database():
    try:
        with open('games.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            print("Connected to JSON database successfully.")
            return data
    except FileNotFoundError:
        print("JSON database file not found.")
        return None
    except json.JSONDecodeError:
        print("Error decoding JSON data.")
        return None

def find_games_by_name(game_name, database):
    results = {}
    search_query = game_name.lower().replace(" ", "")  # Удаление пробелов для более гибкого сравнения
    for game_id, game_data in database.items():
        name = game_data["name"].lower().replace(" ", "")
        # Нечеткое сравнение с использованием SequenceMatcher
        ratio = SequenceMatcher(None, search_query, name).ratio()
        if ratio > 0.7:
            if game_id not in results:  # Добавляем только если игра еще не в списке
                total_reviews = game_data["positive"] + game_data["negative"]
                results[game_id] = (game_data, total_reviews)
        # Точное сравнение с использованием оператора 'in'
        if search_query in name:
            if game_id not in results:
                total_reviews = game_data["positive"] + game_data["negative"]
                results[game_id] = (game_data, total_reviews)

    # Сортировка результатов по количеству отзывов
    sorted_results = sorted(results.values(), key=lambda x: x[1], reverse=True)
    return sorted_results[:10]

def find_games_by_category(category, database):
    results = []
    for game_id, game_data in database.items():
        # Проверяем, что теги существуют и это словарь
        if isinstance(game_data.get("tags"), dict):
            # Сортируем теги по популярности (значениям словаря) и берем первые три
            sorted_tags = sorted(game_data["tags"].items(), key=lambda x: x[1], reverse=True)[:3]
            # Преобразуем список кортежей обратно в список тегов
            top_tags = [tag for tag, popularity in sorted_tags]
            # Проверяем, содержит ли список топовых тегов искомую категорию
            if any(category.lower() in tag.lower() for tag in top_tags):
                total_reviews = game_data["positive"] + game_data["negative"]
                results.append((game_data, total_reviews))
    results.sort(key=lambda x: x[1], reverse=True)
    return results[:20]


def format_game_list(games):
    message = ""
    for i, (game_data, total_reviews) in enumerate(games, start=1):
        if total_reviews > 0:
            positive_percentage = (game_data["positive"] / total_reviews) * 100
        else:
            positive_percentage = 0
        message += (f"{i}. {game_data['name']} (Reviews: {total_reviews})\n"
                    f"\tPositive: {positive_percentage:.2f}%\n")
    return message

WISHLIST_DIR = 'Wishlists'

if not os.path.exists(WISHLIST_DIR):
    os.makedirs(WISHLIST_DIR)

def get_wishlist_path(user_id):
    return os.path.join(WISHLIST_DIR, f'{user_id}_wishlist.json')

def read_wishlist(user_id):
    filename = get_wishlist_path(user_id)
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def save_wishlist(user_id, wishlist):
    filename = get_wishlist_path(user_id)
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(wishlist, file, indent=4)  # Форматирование с отступами

def add_game_to_wishlist(user_id, game):
    wishlist = read_wishlist(user_id)
    if game not in wishlist:
        wishlist.append(game)
        save_wishlist(user_id, wishlist)
    return wishlist

def remove_game_from_wishlist(user_id, game_name):
    wishlist = read_wishlist(user_id)
    new_wishlist = [game for game in wishlist if game['name'] != game_name]
    save_wishlist(user_id, new_wishlist)
    return new_wishlist