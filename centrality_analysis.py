import networkx as nx
import json
import matplotlib.pyplot as plt
import requests
from io import BytesIO
from PIL import Image


def load_json(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_image(url):
    try:
        response = requests.get(url)
        img = Image.open(BytesIO(response.content))
        return img
    except:
        return None


friends = load_json('friends.json')
friends_of_friend_1 = load_json('friends_of_friend_1.json')
friends_of_friend_2 = load_json('friends_of_friend_2.json')

G = nx.Graph()

# Добавление узлов и связей между пользователем и его друзьями
user_id = "612770812"
G.add_node(user_id, label="You")

for friend in friends:
    G.add_node(friend['id'], photo=friend.get('photo_50'))
    G.add_edge(user_id, friend['id'])


def add_friendship_edges(friends_of_friend, user_id, G):
    for friend in friends_of_friend:
        G.add_node(friend['id'], photo=friend.get('photo_50'))
        G.add_edge(user_id, friend['id'])

        for f in friends_of_friend:
            if f['id'] != friend['id']:
                G.add_edge(friend['id'], f['id'])


add_friendship_edges(friends_of_friend_1, user_id, G)
add_friendship_edges(friends_of_friend_2, user_id, G)

pos = nx.spring_layout(G)  # Позиции узлов для отображения графа

plt.figure(figsize=(12, 12))
ax = plt.gca()

for node in G.nodes():
    if 'photo' in G.nodes[node]:
        img_url = G.nodes[node]['photo']
        img = load_image(img_url)
        if img:
            x, y = pos[node]
            img = img.resize((50, 50))
            ax.imshow(img, extent=(x - 0.025, x + 0.025, y - 0.025, y + 0.025), zorder=2)

nx.draw_networkx_edges(G, pos, alpha=0.5, ax=ax)

ax.set_axis_off()
plt.show()

# Центральности:
betweenness_centrality = nx.betweenness_centrality(G)
print("Центральность по посредничеству:", betweenness_centrality)

closeness_centrality = nx.closeness_centrality(G)
print("Центральность по близости:", closeness_centrality)

eigenvector_centrality = nx.eigenvector_centrality(G)
print("Центральность собственного вектора:", eigenvector_centrality)


def save_centralities_to_file(filename, betweenness, closeness, eigenvector):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("Центральность по посредничеству:\n")
        for node, value in betweenness.items():
            f.write(f"{node}: {value}\n")

        f.write("\nЦентральность по близости:\n")
        for node, value in closeness.items():
            f.write(f"{node}: {value}\n")

        f.write("\nЦентральность собственного вектора:\n")
        for node, value in eigenvector.items():
            f.write(f"{node}: {value}\n")


save_centralities_to_file('centralities_from_json.txt', betweenness_centrality, closeness_centrality,
                          eigenvector_centrality)
