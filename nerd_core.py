import graph_tool as gt
from graph_tool.all import *

f = open("resources/z340.txt",mode='r')

cipher_text = f.read().replace("\n","")

print(cipher_text)
vertices = set()
for c in cipher_text:
    vertices.add(c)

vertex_list = list(set(vertices))
vertex_list.sort()

g = Graph(directed=False)

g.add_vertex(len(vertex_list))
for i in range(1,len(cipher_text)):
    v_ind_1 = vertex_list.index(cipher_text[i-1])
    v_ind_2 = vertex_list.index(cipher_text[i])
    e = g.edge(v_ind_1,v_ind_2)
    if e is None:
        g.add_edge(v_ind_1,v_ind_2)

vprop_name = g.new_vertex_property("string")
for i,v in enumerate(vertex_list):
    vprop_name[i] = v

pos = graph_tool.draw.fruchterman_reingold_layout(g,n_iter=1000)
#state = gt.minimize_nested_blockmodel_dl(g, deg_corr=True)

cliques = list(gt.topology.max_cliques(g))
for c in cliques:
    print(c)
largest_clique = []
for c in cliques:
    if len(c) > len(largest_clique):
        largest_clique = c

vprop_clique = g.new_vertex_property("bool")
for i,v in enumerate(vertex_list):
    if i in largest_clique:
        vprop_clique[i] = True
    else:
        vprop_clique[i] = False

#ind_set = gt.topology.max_independent_vertex_set(g,high_deg=True)

input()

graph_draw(g,vertex_text=vprop_name,pos=pos,vertex_fill_color=vprop_clique)

