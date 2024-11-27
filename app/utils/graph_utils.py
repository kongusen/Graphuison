import networkx as nx

# 假设这段代码包含构建和操作图所需的函数
def get_nx_graph(triples, concept_2_id, relation_2_id):
    # 实现用于构建图的逻辑
    G = nx.DiGraph()
    for s, p, o in triples:
        G.add_edge(concept_2_id[s], concept_2_id[o], relation=relation_2_id[p])
    return G

# 其他与图相关的实用函数，如 verbalization 函数