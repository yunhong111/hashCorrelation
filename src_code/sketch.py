from countminsketch import CountMinSketch

def node_countminsketch():
    sketch = CountMinSketch(6000, 10)  
    return sketch

def host_init(host_nodes):
    host_sketches = {}
    for host_node in host_nodes:
        host_sketches[host_node] = node_countminsketch()
    return host_sketches

def node_sketch_init():
    global host_nodes, nodes
    
    node_sketches = {}
    for node in nodes:
        node_sketches[node] = node_countminsketch()
    return node_sketches

def sort_sketch(sketch):
    sketch_elt_list = []
    for table in sketch.tables:
        for mi in xrange(0, sketch.m):
            sketch_elt_list.append(table[mi])
    sketch_elt_list.sort(reverse=True)
    return sketch_elt_list
    
def clear_sketch(sketch):
    for table in sketch.tables:
        for mi in xrange(0, sketch.m):
            table[mi] = 0
    return sketch
