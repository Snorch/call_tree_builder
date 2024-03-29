#!/usr/bin/python3
import pydot
import sys


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


'''
Removes characters unrelated to tree description generated by CCTree.
Also skips all lines without '+->' or '+-<', consider them comments.
'''
def cleanup_cctree_lines(lines):
    new_lines=[]
    for i, line in enumerate(lines):
        j = line.find('+-')
        if j == -1:
            continue

        # Remove accidental leading '!' and '#'
        if line[0] == '!' or line[0] == '#':
            line = line[1:]
            j=j-1

        # Remove accidental '@' before '+-<' and '+->'
        k = line[:j].find('@')
        if k != -1:
            line = line[:k] + line[k+1:]

        new_lines.append(line)

    return new_lines


'''
This is a node/edge labeling format:
  +-> node a
    +-> node b # comment for edge a->b
Or:
  +-< node a
    +-< node b # comment for edge b->a
Edge comment should be separated by '#'.
'''
def data_split(data):
    if '#' in data:
        tmp = data.split('#', 1)
    else:
        tmp = [data]

    return tmp[0].strip(), ''.join(tmp[1:]).strip()


def cctree_to_link_nodes_and_edges(path):
    with open(path) as fle:
        lines = cleanup_cctree_lines(fle.readlines())

        if not len(lines):
            eprint('Empty CCTree file')
            return [], []

        j = lines[0].find('+-')
        if j == -1 or j + 2 >= len(lines[0]):
            eprint('Bad format of CCTree file')
            return [], []

        offs = []
        for line in lines:
            off = line.find('+-')
            if off == -1:
                eprint('Bad format of CCTree file:', line)
                return [], []
            offs.append(off)

        nodes = set()
        for i, _ in enumerate(lines):
            node, _ = data_split(lines[i][offs[i]+4:].strip())
            nodes.add(node)

        links = []
        root = 0
        up = True
        for i, _ in enumerate(lines):
            found = False
            for j in range(i - 1, root-1, -1):
                if offs[j] >= offs[i]:
                    continue
                elif offs[j] + 2 != offs[i]:
                    eprint('Bad format of CCTree file:', ''.join(lines[j:i+1]))
                    return [], []
                else:
                    found = True
                    a, comment_a = data_split(lines[i][offs[i]+4:].strip())

                    b, _ = data_split(lines[j][offs[j]+4:].strip())
                    edge = []
                    if up:
                        edge=[a, b, comment_a]
                    else:
                        edge=[b, a, comment_a]

                    if edge not in links:
                        links.append(edge)
                    break;

            '''
            Next root node. This happens when we get to next CCTree output
            '''
            if not found:
                root = i
                if lines[i][offs[i] + 2] == '<':
                    up = True
                elif lines[i][offs[i] + 2] == '>':
                    up = False
                else:
                    eprint('Bad format of CCTree file:', lines[0])
                    return [], []

        return list(nodes), links


def nodes_and_edges_to_tree(nodes, links, dot_path):
    gr = pydot.Dot(graph_type='digraph')
    counter = 0
    nodemap = {}

    for node in nodes:
        if node in nodemap:
            continue
        nodemap[node] = str(counter)
        counter += 1

        nod = pydot.Node(nodemap[node], label=node)
        gr.add_node(nod)
    for link in links:
        edge = pydot.Edge(nodemap[link[0]], nodemap[link[1]], label=link[2])
        gr.add_edge(edge)
    gr.write(dot_path)


if __name__ == '__main__':
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        eprint("usage: %s <path/to/graph.cct> [<path/to/graph.dot>]\n" % (sys.argv[0]))
        exit(1)

    dot_path = '/dev/stdout'
    if len(sys.argv) == 3:
        dot_path = sys.argv[2]

    nodes, links = cctree_to_link_nodes_and_edges(sys.argv[1])

    nodes_and_edges_to_tree(nodes, links, dot_path)
