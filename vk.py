import requests
import json
import webbrowser

# Настройки OAuth 2.0 для получения access_token
APP_ID = '52468739'  # ID приложения ВКонтакте
REDIRECT_URI = 'https://dev.vk.com/ru/api-console-auth'
OAUTH_URL = f'https://oauth.vk.com/authorize?client_id={APP_ID}&display=page&redirect_uri={REDIRECT_URI}&scope=friends,status&response_type=token&revoke=1&v=5.199'


def get_friends(user_id, access_token):
    url = "https://api.vk.com/method/friends.get"
    params = {
        "user_id": user_id,
        "order": "name",
        "count": 5000,
        "offset": 0,
        "fields": "sex,bdate,city,country,photo_50,photo_100,photo_200_orig,status",
        "access_token": access_token,
        "v": "5.199"
    }
    response = requests.get(url, params=params)

    try:
        data = response.json()
    except requests.exceptions.JSONDecodeError:
        print("Ошибка при декодировании JSON. Проверьте корректность запроса.")
        return []

    if 'error' in data:
        error = data['error']
        print(f"Ошибка API: {error.get('error_msg', 'Неизвестная ошибка')}")
        return []

    friends = data.get("response", {}).get("items", [])

    friends_list = []
    for friend in friends:
        friend_data = {
            "id": friend.get("id"),
            "first_name": friend.get("first_name"),
            "last_name": friend.get("last_name"),
            "nickname": friend.get("nickname"),
            "sex": "male" if friend.get("sex") == 2 else "female" if friend.get("sex") == 1 else "unknown",
            "bdate": friend.get("bdate"),
            "photo_50": friend.get("photo_50"),
            "photo_100": friend.get("photo_100"),
            "photo_200_orig": friend.get("photo_200_orig"),
            "country": friend.get("country"),
            "city": friend.get("city", {}).get("title", "unknown"),
            "status": friend.get("status")
        }
        friends_list.append(friend_data)

    return friends_list


def find_friend_among_friends(friend_list, first_name, last_name):
    for friend in friend_list:
        if (friend["first_name"].lower() == first_name.lower() and
                friend["last_name"].lower() == last_name.lower()):
            return friend
    return None


def get_friends_of_friend(user_id, first_name, last_name, access_token):
    friends = get_friends(user_id, access_token)

    if not friends:
        print("Список друзей пуст или произошла ошибка при получении.")
        return []

    friend = find_friend_among_friends(friends, first_name, last_name)

    if friend:
        print(f"Найден друг: {friend['first_name']} {friend['last_name']} (ID: {friend['id']})")
        # Получаем друзей найденного друга
        friends_of_friend = get_friends(friend["id"], access_token)
        return friends_of_friend
    else:
        print(f"Друг {first_name} {last_name} не найден.")
        return []


def save_friends_to_json(friends, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(friends, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    print("Открытие браузера для авторизации...")
    webbrowser.open(OAUTH_URL)

    access_token = input("Введите ваш access_token, скопированный из URL после авторизации: ")

    if access_token:
        user_id = "612770812"

        # Получение и запись списка друзей в json
        friends = get_friends(user_id, access_token)
        if friends:
            save_friends_to_json(friends, 'friends.json')

        # Член группы
        friend_name_1 = "Дмитрий"
        friend_last_name_1 = "Мельников"
        friends_of_friend_1 = get_friends_of_friend(user_id, friend_name_1, friend_last_name_1, access_token)
        if friends_of_friend_1:
            save_friends_to_json(friends_of_friend_1, "friends_of_friend_1.json")

        # Член группы 
        friend_name_2 = "Мансур"
        friend_last_name_2 = "Эркинов"
        friends_of_friend_2 = get_friends_of_friend(user_id, friend_name_2, friend_last_name_2, access_token)
        if friends_of_friend_2:
            save_friends_to_json(friends_of_friend_2, "friends_of_friend_2.json")
    else:
        print("Авторизация не выполнена, токен не получен.")

