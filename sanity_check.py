# coding: utf-8
import matplotlib.pyplot as plt
import networkx as nx

with open('data/warlight_rormap_adj_matrix', 'r') as f:
    adj_lines = f.readlines()
adj_lines = [ x for x in adj_lines if not x.startswith('#')]
adj_lines = [ x for x in adj_lines if x.strip() != '' ]
adjmat = { x.split(':')[0] : { 'value':0.0, 'adj_nodes': x.split(':')[1].strip().split(',') } for x in adj_lines }

not_founds = set()
for k, v in adjmat.items():
    for x in v['adj_nodes']:
        if x not in adjmat:
            print("{} not found! adjacent to {}".format(x,k))
            not_founds.add(x)

with open('data/warlight_rormap_bonus_groups', 'r') as f:
    bg_lines = f.readlines()
bg_lines = [ x for x in bg_lines if not x.startswith('#')]
bg_lines = [ x for x in bg_lines if x.strip() != '' ]
bg_data = { x.split(':')[0].split(',')[0] : { 'value':float(x.split(':')[0].split(',')[1]), 'nodes':x.split(':')[1].strip().split(',')} for x in bg_lines }

for bg, data in bg_data.items():
    for x in data['nodes']:
        if x not in adjmat:
            print("{} not found! belongs to {}".format(x,bg))
            not_founds.add(x)
            continue
        adjmat[x]['value'] += data['value']/len(data['nodes'])

# sort node scores
scores = [ (k,v['value']) for k,v in adjmat.items() ]
scores.sort(key=lambda x: x[1],reverse=True)
just_scores = [ x[1] for x in scores ]

# plot node scores
plt.plot(just_scores)
plt.ylabel('node scores')
plt.show()


# gen networkx graph
G = nx.Graph()
edge_list = []
for k, data in adjmat.items():
    for n in data['adj_nodes']:
        G.add_edge(k,n)
        edge_list.append((k,n))

graph_pos = nx.spectral_layout(G)
nx.draw_networkx_nodes(G,graph_pos, node_size=10, node_color='blue', alpha=0.3)
nx.draw_networkx_edges(G,graph_pos)
nx.draw_networkx_labels(G,graph_pos, font_size=8, font_family='sans-serif')
plt.show()

degree_centrality = nx.degree_centrality(G)
betweenness_centrality = nx.betweenness_centrality(G)

from lib.game import Game
from lib.player import Player
from lib.territory import Territory
from lib.bonusgroup import BonusGroup
from lib.moves import AttackMove, PlacementMove, TransferMove

g = Game(seed=42,adjmat=adjmat)
player_1 = Player('Player 1','orange')
player_2 = Player('Player 2','yellow')
from lib.strategy import Greedy
player_1.strategy = Greedy()
g.add_player(player_1)
g.add_player(player_2)

for t in adjmat:
    g.add_territory(Territory(t))

for t, data in adjmat.items():
    for n in data['adj_nodes']:
        g.territories[t].add_neighboor(g.territories[n])

for bg, data in bg_data.items():
    bg_obj = BonusGroup(bg,data['value'])
    for n in data['nodes']:
        bg_obj.add_territory(g.territories[n])
    g.add_bonus_group(bg_obj)

g.start_game(5)
player_1, player_2 = g.players.keys()

results = g.run_game()
p1troops = [ x['players']['Player 1']['num_troops'] for x in results ]
p2troops = [ x['players']['Player 2']['num_troops'] for x in results ]
plt.clf()
plt.plot(range(len(p1troops)),p1troops,color='blue')
plt.plot(range(len(p1troops)),p2troops,color='red')
plt.show()
