import numpy as np 

def onSegment(p1, p2, p):
    """ Return boolean for point p on rectangle p1 - p2"""
    return np.min(np.array([p1[0], p2[0]])) <= p[0] <= np.max(np.array([p1[0], p2[0]])) and np.min(np.array([p1[1], p2[1]])) <= p[1] <= np.max(np.array([p1[1], p2[1]]))

def onSegment_(p1, p2, p):
    """ Return boolean for point p on segment p1 - p2"""
    u = p2 - p1
    v = p2 - p
    w = p - p1
    #arbitrary threshold to approximate collision
    return (np.linalg.norm(v) + np.linalg.norm(w) - np.linalg.norm(u)) < 1e-8
    #return np.linalg.norm(v) + np.linalg.norm(w) == np.linalg.norm(u)

def DistanceToSegment(p1, p2, p):
    """ Return distance of a point to a segment by vector projection"""
    u = p2 - p1
    v = p - p1 
    distance = np.linalg.norm(np.cross(u, v)) / np.linalg.norm(u) 
    return distance

def DistanceToPoint(p1, p):
    """ Return distance from p to p1"""
    return np.linalg.norm(p1 - p)

def Intersect(p1, p2, p3, p4):
    """ Check if two segment intersect"""
    d1 = np.cross((p1 - p3), (p4 - p3))
    d2 = np.cross((p2 - p3), (p4 - p3))
    d3 = np.cross((p3 - p1), (p2 - p1))
    d4 = np.cross((p4 - p1), (p2 - p1))
    
    if ((d1 < 0 and d2 > 0) or (d1 > 0 and d2 < 0)) and ((d3 > 0 and d4 < 0) or (d3 < 0 and d4 > 0 )):
        return True
    elif d1 == 0 and onSegment_(p3, p4, p1):
        return True
    elif d2 == 0 and onSegment_(p3, p4, p2):
        return True
    elif d3 == 0 and onSegment_(p1, p2, p3):
        return True
    elif d4 == 0 and onSegment_(p1, p2, p4):
        return True
    else:
        return False