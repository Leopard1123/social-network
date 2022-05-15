import itertools
import networkx
import requests
import pyorient
import json
from networkx.algorithms import community
import community
import scipy as sp
import time
import networkx as nx
import matplotlib.pyplot as plt
"""
    Блок для работы с базой данных OrientDB
"""
client = pyorient.OrientDB("localhost", 2424)
client.set_session_token(True)
session_id = client.connect("root", "root")
client.db_open("final", "root", "root")

def get_friends_closed(user_id) -> None:
    """
    :param user_id: id цели, информацию о которой нужно получить.
    :return: возвращает response - ответ.
    """

    req = requests.get(f"https://api.vk.com/method/execute.getFriends?oid={user_id},offset={50},mass={200},overlap={200}", params={
        'access_token': 'ff6590ba6c041d98125cbdb85627d91700767e1a7b113efb4cf7be39082fc8e3f6476cc8e5fd1aab9809a',
        'v': 5.131,
    }).json()
    time.sleep(0.3)
    with open("friends.json", "w") as f:
        f.write(json.dumps(req, indent=1, sort_keys=True))
    f.close()
    return req


def dictionary(user_id) -> dict:
    """
    Функция формирует словарь вида {'id цели' : [список id её друзей]}
    :param user_id: id цели.
    :return: словарь вида {'id цели' : [список id её друзей]}
    """
    arr = []
    answer = get_friends_closed(user_id)
    if not len(answer['response']):
        return
    lenhOfAnswer = len(answer['response'][0])
    for i in range(lenhOfAnswer):
        k = answer['response'][0][i]
        try:
            arr.append(k['id'])
        except:
            pass
    dict = {f"{user_id}": arr}
    return dict

def diff(user_id, deep) -> networkx.Graph:
    """
    Функция формирует граф дружеских взаоимосвязей пользователя.
    :param user_id: id цели.
    :param deep: Глубина поиска друзей.
    :return: граф дружеских взаимосвязей порльзователя.
    """
    firstStep = {}
    result = {}
    user_list = []
    user_list.append(user_id)
    for i in range(deep):
        for j in user_list:
            try:
                firstStep[j] = getFriends(j)
            except:
                pass
        A = set(firstStep.keys())
        values = list(firstStep.values())
        #print(values)
        allIds = []
        for lst in values:
            allIds.extend(lst)

        user_list = allIds
    allIds = list(set(allIds))
    for i in allIds:
        try:
            result[i] = getFriends(i)
        except:
            pass
    friends_ids = (list(result.keys()))
    g = nx.Graph(direceted=False)
    for i in result:
        g.add_node(i)
        record = client.command(f"CREATE CLASS friendsOf{i} IF NOT EXISTS EXTENDS V")
        for j in result[i]:
            record = client.command(f"CREATE VERTEX friendsOf{i} set name='{j}'")
            if i != j and i in friends_ids and j in friends_ids:
                g.add_edge(i, j)
    return g

def luvan(g) -> None:
    """
    Функция отрисовывает граф, кластеризированный методом Лувена.
    :param g: граф дружеских взаимосвязей пользователя.
    """
    partition = community.best_partition(g)
    pos = nx.spring_layout(g)
    plt.figure(figsize=(8, 8))
    plt.axis('off')
    nx.draw(g, pos, node_size=5,  cmap=plt.cm.RdYlBu, node_color=list(partition.values()))
    plt.show()





def getFriends(user_id) -> list:
    """
        Функция форумирует список друзей пользователя с id user_id.
        :param user_id: id цели.
    """
    return sum(list(dictionary(user_id).values()), [])






def girvan_newman(g):
    """
        Функция отрисовывает граф, кластеризированный алгоритмом Гирвана-Ньюмана.
        :param g: граф дружеских взаимосвязей пользователя.
    """
    comp = nx.algorithms.community.girvan_newman(g)
    k = 6
    limited = itertools.takewhile(lambda c: len(c) <= k, comp)
    communities = list(limited)[-1]
    community_dict = {}
    community_num = 0
    for community in communities:
        for character in community:
            community_dict[character] = community_num
            community_num += 1
            nx.set_node_attributes(g, community_dict, 'community')
    betweenness_dict = nx.betweenness_centrality(g)
    nx.set_node_attributes(g, betweenness_dict, 'betweenness')
    color = 0
    color_map = ['red', 'blue', 'yellow', 'purple', 'black', 'green']
    for community in communities:
        nx.draw_networkx_nodes(g, pos=nx.spring_layout(g, iterations=200), nodelist=community, node_size=25,
                node_color=color_map[color])
        color += 1
    plt.show()


girvan_newman(diff(559892106,1))