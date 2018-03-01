class singleNode(object):
    def __init__(self, val):
        self.val = val
        self.pre = None
        self.next = None
        
def makelist(points):
    d = {}
    p = None
    
    count = 0
    while(count < 2):
        count += 1
        for point in points:
            if point[0] not in d:
                snode0 = singleNode(point[0])
                d[point[0]] = snode0
            else:
                snode0 = d[point[0]]
                
            if point[1] not in d:
                snode1 = singleNode(point[1])
                d[point[1]] = snode1
            else:
                snode1 = d[point[1]]
            
            snode0.next = snode1
            snode1.pre = snode0
            print('point[0]', point[0], snode0.pre)
        
    print('len(d)', len(d))
    print('d', d)
        
    p = snode0
    while(p.pre != None):
        p = p.pre
        
    nodes = []
    while(p != None):
        nodes.append(p.val)
        p = p.next
    print(nodes)
    return nodes

        
"""
    (2, 1) (4, 3) (5, 6) (3, 5) (1, 4) 
    (1, 4) (2, 1) (3, 5) (4, 3) (5, 6)   
    (2, 1) (1, 4) (4, 3) (3, 5) (5, 6)
"""

points = [(2, 1), (4, 3), (5, 6), (3, 5), (1, 4)]
makelist(points)
