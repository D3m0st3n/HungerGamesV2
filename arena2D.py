#### Arena definition for Fly Hunger Games 2D

from Utility import *
import numpy as np
import matplotlib.pyplot as plt
from Fly import Fly2D
from Food import Food

class Entrance:
    """ Entrance object"""

    #TODO : entrance = coordinates + radius
    def __init__(self, coord = [0, 0], radius = 0.5, xy = 1, z = 0, isFake : bool = False):
        """" Set entrance position on wall"""
        
        #center coordinate
        self.coord = np.array(coord)
        #width/radius
        self.radius = radius
        
        #Distance to first point of wall
        self.xy = xy
        #Height of entrance on wall
        #Always 0 in 2D
        self.z = z
        #True or Fake entrance
        self.isFake = isFake


        #self.position = []
    
    def __repr__(self) -> str:
        """ String representation of the object"""
        coord = "Coord : " + str(self.coord)
        fake = "Fake : " + str(self.isFake)
        sep = " / "
        return coord + sep + fake
    
    def getEdges(self, wall):
        """ Return starting and ending coordinates"""

        start = [self.coord[0] - self.radius * np.cos(wall.getAngle()), self.coord[1] - self.radius * np.sin(wall.getAngle())]
        end = [self.coord[0] + self.radius * np.cos(wall.getAngle()), self.coord[1] + self.radius * np.sin(wall.getAngle())]

        return np.array(start), np.array(end)

    def getCoordinates(self, wall):
        """ Return coordinates of entrances"""
        
        vec = wall.coord2 - wall.coord1 
        nvec = np.linalg.norm(vec)
        
        return np.array( vec / nvec * self.xy + wall.coord1)

class Wall:
    """ Wall object"""

    def __init__(self, coord1 = [0, 0], coord2 = [1, 1], nb_ent = 3):
        """" Position"""

        #Coordinates
        self.coord1 = np.array(coord1)
        self.coord2 = np.array(coord2)

        #Entrances
        self.entrances = self.__buildEntrances(nb_ent, 0.08 * self.getLength())

        #Width
        self.width = 0.05
    
    def getLength(self):
        """ Get legnth of wall"""

        return np.linalg.norm(self.coord2-self.coord1)

    def getAngle(self):
        """ Return angle with x axis"""

        #Angle return in radians
        v = self.coord2 - self.coord1
        phi = np.arctan2(v[1], v[0])
        if phi < 0:
            phi += 2 * np.pi
        return phi

    def __repr__(self):
        """ Return representatio of object as a string"""

        coord = "Coord : " + str(self.coord1) + str(self.coord2)
        a = self.getAngle() * 180 / np.pi
        if a < 0:
            a += 360
        angle = "Angle : " + str(a)
        sep = " / "
        return coord + sep + angle 
    
    def __buildEntrances(self, nb_entrances = 2, thr = 1.0, ent_radius = 0.1):
        """ Build entrances on wall"""
        #Return list of entrances object
        entrances = []
        while len(entrances) < nb_entrances:
            
            while True :
                #TODO : add distribution choice
                #dist = np.random.uniform(0.05, 0.95) * self.getLength()
                dist = np.abs(np.random.normal(self.getLength()//2, self.getLength() * 0.3))
                #Avoid entrances creation too close from outer walls and center
                if dist < self.getLength() * 0.95 and dist > self.getLength() * 0.1 and (dist > ent_radius and dist < self.getLength() - ent_radius):
                    break
            
            vec = self.coord2 - self.coord1 
            nvec = np.linalg.norm(vec)
            coord = np.array( vec / nvec * dist + self.coord1)
            
            e = Entrance(coord, ent_radius, dist, z=0, isFake=np.random.randint(0, 2))

            if len(entrances) != 0:
                add_flag = True
                e.isFake = True
                for e_ in entrances:
                    #avoid creation too close
                    if np.linalg.norm(e.coord - e_.coord) < thr + ent_radius:
                        add_flag = False
                        break
                if add_flag:            
                    entrances.append(e)
                    add_flag = False

            if len(entrances) == 0:
                e.isFake = False
                entrances.append(e)

        print("Entraces Built")
        
        return entrances
    
    def getEntrancesCoord(self):
        """ Return entrances coordinates"""

        #Entrances coordinates list
        ecoord_l = []
        for e in self.entrances:
            ecoord_l.append(e.coord)

        return ecoord_l


class CircleArena:
    """" Circle arena object"""

    def __init__(self, center = [0, 0], radius = 1, nb_rooms = 4, nb_ent = 3, nb_flies = 0, starting_room = 1, food_lifetime = 100):
        """ Set arena diemnsions"""

        #Circle propeties
        self.center = np.array(center)
        self.radius = radius

        #Room building
        self.walls = self.__buildWalls(nb_rooms, nb_ent)

        #Place flies        
        self.flies = []
        position = self.getRoomCenter(starting_room)
        for i in range(nb_flies):
            while True:
                position = np.random.normal(self.getRoomCenter(starting_room), 0.5)
                if self.getRoomfromPos(position) == starting_room:
                    break
            self.flies.append(Fly2D(position, orientation=0, speed=0.205, cognition_radius=0.5 ,cognition_angle= np.pi , fertility=0, arena=self))
        
        
        food_room = starting_room + 1
        if nb_rooms == 1:
            food_room = starting_room

        if starting_room == nb_rooms:
            food_room = 1
        self.food = Food(self.getRoomCenter(food_room), food_room, lifetime=food_lifetime, arena=self)

        for i, wall in enumerate(self.walls):
            for j, entrance in enumerate(wall.entrances):
                print("Wall ", i," Entrance in room ", self.getRoomfromPos(entrance.coord), " at ",entrance.coord )

    

    def __buildWalls(self, nb_rooms = 4, nb_ent = 3):
        """ Build walls in arena"""
        
        #Return list of walls object
        #Build walls by rotation around the center of the arena
        if nb_rooms == 1:
            return []
        walls = []
        c = self.getCenter()
        angles = np.arange(0, np.pi * 2, np.pi/(nb_rooms/2))
        for i, a in enumerate(angles):
            x = self.radius * np.cos(a)
            y = self.radius * np.sin(a)
            walls.append(Wall(c, [x, y] + c, nb_ent))
            print("Angle of wall ", i, ":", a * 180 / np.pi, walls[i].getAngle() * 180 / np.pi)
            print("Wall coord :", walls[i].coord1, walls[i].coord2)
            

        print("Walls Built")
        return walls

    def getCenter(self):
        """ Return center coordinates"""

        return self.center

    def getCoordinates(self, sample = 360):
        """ Return all points of the arena"""

        phi = np.linspace(0, 2 * np.pi, sample)
        xc = self.radius * np.cos(phi) + self.center[0]
        yc = self.radius * np.sin(phi) + self.center[1]

        return xc, yc

    def getRoomfromPos(self, position):
        """ Return room number from coordinates"""
        
        #Convention : rooms are counted from 1
        #Return 0 if no room is not found , -1 if position is on wall

        #Check if position is in arena
        if not self.checkInArena(position):
            #print(" Position outside the arena ", position)
            return 0

        if len(self.walls) == 0:
            return 1

        #Find closest wall
        """#List of distances to walls
        wall_dist = [DistanceToSegment(wall.coord1, wall.coord2, position) for wall in self.walls]
        #List of sorted indices of distances to walls
        sort_indeces = np.argsort(wall_dist)
        wall_index = sort_indeces[0]
        wall = self.walls[wall_index]
        
       # print(sort_indeces, np.sort(wall_dist))
        
        for i in sort_indeces:
            
            wall_index = i
            wall = self.walls[wall_index]
            projection = np.dot((position - wall.coord1),(wall.coord2 - wall.coord1)) / np.linalg.norm(wall.coord2 - wall.coord1)**2  * (wall.coord2 - wall.coord1) + wall.coord1
            if onSegment_(wall.coord1, wall.coord2, projection):
                if wall_index > 1 and wall_index + 1 < len(wall_dist):
                    #print(projection, wall_index, wall_dist[wall_index], wall_index + 1, wall_dist[wall_index - 1],wall_index - 1, wall_dist[wall_index + 1])
                    pass
                break
        

        if np.cross((wall.coord2 - wall.coord1), (position - wall.coord1)) <= 0:
            #Point is on the left of the wall
            
            if DistanceToSegment(wall.coord1, wall.coord2, position) <= wall.width:
                #Point is in contact with the wall
                
                #print("wall", wall_index, "cross ", np.cross((wall.coord2 - wall.coord1), (position - wall.coord1)) / np.linalg.norm(wall.coord2 - wall.coord1), DistanceToSegment(wall.coord1, wall.coord2, position), wall.coord1, wall.coord2)

                for entrance in wall.entrances:
                
                    e_coord1, e_coord2 = entrance.getEdges(wall)

                    if np.linalg.norm(entrance.coord - position) <= entrance.radius or onSegment_(e_coord1, e_coord2, position):
                    #if np.linalg.norm(entrance.coord - position) <= entrance.radius and DistanceToSegment(e_coord1, e_coord2, position) <= wall.width:

                        if wall_index == 0:
                            return len(self.walls)
                        return wall_index
                return -1
            
            else:
                if wall_index == 0:
                    return len(self.walls)
                return wall_index
            
        if np.cross((wall.coord2 - wall.coord1), (position - wall.coord1)) > 0 :
            #Point is on the right of wall

            if DistanceToSegment(wall.coord1, wall.coord2, position) <= 0:
                #Point is in contact with the wall

                #print("wall", wall_index, "cross ", np.cross((wall.coord2 - wall.coord1), (position - wall.coord1)) / np.linalg.norm(wall.coord2 - wall.coord1), DistanceToSegment(wall.coord1, wall.coord2, position), wall.coord1, wall.coord2)

                for entrance in wall.entrances:
                
                    e_coord1, e_coord2 = entrance.getEdges(wall)

                    if np.linalg.norm(entrance.coord - position) <= entrance.radius or onSegment_(e_coord1, e_coord2, position):
                    #if np.linalg.norm(entrance.coord - position) <= entrance.radius and DistanceToSegment(e_coord1, e_coord2, position) <= wall.width:
                    #if onSegment_(e_coord1, e_coord2, position):
                        if wall_index == 0:
                            return len(self.walls)
                        return wall_index
                return -1
            
            return wall_index + 1"""

        
        """phi = np.arctan2((position[1] - self.center[1]), (position[0] - self.center[0]))
        if phi < 0:
            phi += 2 * np.pi
        for i in range(len(self.walls)):
            p_wall = self.walls[i]
            p_angle = p_wall.getAngle()
            if i + 1 == len(self.walls):
                n_wall = self.walls[0]
                n_angle = n_wall.getAngle() + 2 * np.pi
            else:
                n_wall = self.walls[i + 1]
                n_angle = n_wall.getAngle()

                
            if phi >= p_angle and phi <= n_angle:
                    
                #print(p_angle * 180 / np.pi, phi * 180 / np.pi, n_angle * 180 / np.pi, i, i + 1)
                if DistanceToSegment(p_wall.coord1, p_wall.coord2, position) <= p_wall.width:
                    for entrance in p_wall.entrances:
                        
                        e_coord1, e_coord2 = entrance.getEdges(p_wall)

                        if np.linalg.norm(entrance.coord - position) <= entrance.radius or onSegment_(e_coord1, e_coord2, position):
                            #return i + 1
                            pass


                if DistanceToSegment(n_wall.coord1, n_wall.coord2, position) <= n_wall.width:
                    for entrance in n_wall.entrances:
                        
                        e_coord1, e_coord2 = entrance.getEdges(n_wall)

                        if np.linalg.norm(entrance.coord - position) <= entrance.radius or onSegment_(e_coord1, e_coord2, position):
                            if n_angle == 2 * np.pi:
                                return len(self.walls)
                            else:
                                return i + 1
                            pass
                    return -1
                
                return i + 1"""

        #print(" No room found for this position", position)
        return 0 

    def getRoomCenter(self, room = 1, scale = 1):
        """ Return room center given room number"""

        #Return center of room 1 by default
        if len(self.walls) == 0:
            return self.getCenter()
        room = room - 1

        if scale > 2 or scale <= 0:
            scale = 1

        #Get room angle
        if room + 1 < len(self.walls):
            a1 = self.walls[room].getAngle()
            a2 = self.walls[room + 1].getAngle()
        else:
            a1 = self.walls[room].getAngle()
            #a2 = self.walls[0].getAngle()
            a2 = 2 * np.pi
        
        #Correction of angle, angle are expressed between +pi and -pi
        """if a1 > 0 and a2 < 0:
            a2 = a2 +  np.pi * 2"""
        phi = (a1 + a2) /2

        #Convert polar coordinates in cartesian coord
        x = np.cos(phi) * self.radius/2 * scale + self.getCenter()[0]
        y = np.sin(phi) * self.radius/2 * scale + self.getCenter()[1]
        return [x, y]

    def allowMove(self, position, new_position):
        """ Check if movement is possible"""
        #Get current room and room of new position
        current_room = self.getRoomfromPos(position)
        new_room = self.getRoomfromPos(new_position)
        #Check if new_pos is in arena
        if self.checkInArena(new_position):

            #Check if new_pos room is the following room of current position : One way trip
            #Movement accross wall

            if  new_room == current_room + 1 or (current_room == len(self.walls) and new_room == 1):
                if current_room == len(self.walls):
                    wall = self.walls[0]
                else:
                    wall = self.walls[current_room]

                #print("Wall angle ", wall.getAngle() * 180/np.pi)
                #print(wall.coord1, wall.coord2)

                #TODO : rework implement for other entrance definition (eg. entrenca with a width)            
                #Segment crossing
                index = np.argmin([np.linalg.norm(entrance.coord - position) for entrance in wall.entrances])
                entrance = wall.entrances[index]
                

                if entrance.isFake and np.linalg.norm(position - entrance.coord) <= entrance.radius:

                    #print("False entrance")
                    return False
                
                if not entrance.isFake:

                    start, end = entrance.getEdges(wall)

                    #print("Intersect ", Intersect(start, end, position, new_position))

                    return Intersect(start, end, position, new_position)
                    

            #new_pos in current room
            if current_room == new_room:
                return True
            #other results, -1, movement on wall
            else:

                #print("Movement on wall ")
                #print(position, new_position)

                return False
                
        #new_pos outside arena, movement not allowed
        else:
            return False

    def checkInArena(self, position):
        """ Check if position is in arena"""

        #Distance to center of arena
        norm = np.linalg.norm(position - self.getCenter())
        return norm < self.radius




def main():
    CA = CircleArena([5, 5], 5, 4, nb_ent=3, nb_flies=1, starting_room=1)
    
    #Plot simulation

    coord = CA.getCoordinates(180)
    plt.plot(coord[0], coord[1])
    for i, w in enumerate(CA.walls):

        #print("wall info ", w.getEntrancesCoord())
        #print("Wall angle : ", w.getAngle())

        plt.plot([w.coord1[0], w.coord2[0]], [w.coord1[1], w.coord2[1]], color="orange")
        room_center = CA.getRoomCenter(i + 1, scale = 1.75)
        #print("Room ", i + 1, " center : ", room_center)
        #plt.scatter(room_center[0], room_center[1], marker="x", color ="black")
        room_center = CA.getRoomCenter(i + 1, scale = 1.75)

        plt.annotate(i + 1, room_center)

        Fake = [e.isFake for e in w.entrances]
        colors = ["green", "red"]
        for i, c in enumerate(w.getEntrancesCoord()):
            plt.scatter(c[0], c[1], marker="o", edgecolor=colors[Fake[i]], facecolor = "none")
    
    #print(CA.flies)
    for f in CA.flies:
        plt.scatter(f.position[0], f.position[1], marker = "x", color = "black")


    plt.scatter(CA.food.position[0], CA.food.position[1], marker="o", color = "red")


    
    r = CA.flies[0].cog_radius
    s_angle = CA.flies[0].angle - CA.flies[0].cog_angle/2
    e_angle = CA.flies[0].angle + CA.flies[0].cog_angle/2
    pos = CA.flies[0].position
    phi = np.linspace(s_angle, e_angle, 90)

    x_a = r * np.cos(phi) + pos[0]
    y_a = r * np.sin(phi) + pos[1]

    plt.plot(x_a, y_a, color = "green", alpha  = 0.35)

    plt.xlim(-1, 11)
    plt.ylim(0, 10)

    plt.xlabel("X")
    plt.ylabel("Y")

    plt.show()

if __name__ == "__main__":
    main()

