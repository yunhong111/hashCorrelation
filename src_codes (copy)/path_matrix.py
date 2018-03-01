
def path_matrix(paths, nodes):
    # paths: dict{dict}
    # nodes: list[str]
    # Return matrix: len(paths)*len(nodes)
    
    matrix = []
    for path in paths:
        tmp = [0] * len(nodes)
        seq = 1
        for p in paths[path]:
            pos = nodes.index(p)
            tmp[pos] = seq
            seq += 1
        matrix.append(tmp)
    return matrix
