#### Fly agent class
from cmath import nan
from math import cos, sin
from curses.ascii import SP
from turtle import pos, position
import numpy as np
import matplotlib.pyplot as plt

from Utility import *

SPEED_DIC = {"fly_speed" : 0.205, "walking_speed" : 0.1025}
SEX = ["M", "F"]
class Fly2D:
    """ Fly 2D agent"""
    """ Many possible states : idle, explore, navigate, rest, investigate, forage, walk, feed"""
    def __init__(self, position, orientation, speed, cognition_radius, cognition_angle,  fertility, arena):
        """ 2D Fly constructor"""
        
        #Initial position
        self.position = np.array(position)
        #Initial angle
        self.angle = orientation
        #Initial state
        self.state = "idle"
        
        #Agent radius
        self.radius = 0.1
        
        #Agent sex M/F
        self.sex = SEX[np.random.randint(0, 2)]

        self.speed = speed
        self.fertility = fertility
        #Energy, maintain above 0 to stay alive
        self.energy = 100
        #Hunger, indicate to which degree fly will look for food
        self.hunger = 0
        #Reproduction, desire to reproduce
        self.reproduction = 0
        #Cognition is a circle around the agent
        #TODO implement angles, other sense : smell, vision etc...
        self.sight_radius = cognition_radius
        self.sight_angle = cognition_angle

        self.smell_radius = 0
        self.smell_angle = 2 * np.pi

        self.memory = []

        self.rest_time = np.random.uniform(0, 10)

        self.aim = self.__generateNewAim(arena)


    def getPolarCoord(self, arena) : 
        """ Return polar coordinates"""
        radius = np.linalg.norm(self.position - arena.getCenter())
        phi = np.arctan2(self.position[1], self.position[0])
        return radius, phi


    def getRoom(self, arena):
        """ Return room where the agent is"""
        
        return arena.getRoomfromPos(self.position)
    
    def update(self, dt, arena):
        " Main update function for agent"

        self.updateState(dt, arena)
        
        self.updatePosition(dt, arena)
        
        #self.updateEnergy(dt)
        
        #self.updateSpeed(dt, arena)
        
        self.updateAim(dt, arena)


        return self.state, self.position, self.energy, self.speed, self.aim


    def updateAim(self, dt, arena):
        """ Update aiming position of fly"""

        if self.state == "explore":
            if np.equal(self.position, self.aim).all():
                self.__generateNewAim(arena)
                return self.aim
            
        min_dist = 1.1 * self.radius
        #Aim change if other flies are too close to the objective
        visible_flies = [fly for fly in arena.flies if self.InSigth(fly.position) and np.linalg.norm(fly.position - self.position) > 0]
        if len(visible_flies) > 0:
            for fly in visible_flies:
                if self.InSigth(self.aim) and np.linalg.norm(fly.position - self.aim) <= min_dist:
                    pass
                    return self.__generateNewAim(arena)
        
        if self.state == "navigate":
            pass

        #Determine a new aiming point of interest
        if self.state == "investigate":
            self.aim = self.getClosestInterest(arena)
            return self.aim
            pass

        """#print(np.linalg.norm(self.position - self.aim))
        if self.speed == SPEED_DIC["walking_speed"] and np.linalg.norm(self.position - self.aim) > 100  * dt * self.speed :
            self.__generateNewAim(arena)
            pass"""

        return self.aim

    def updateEnergy(self, dt):
        """ Update energy """

        #Energy consumption 
        if self.state == "idle" or self.state == "rest":
            #No movement, resting
            lam = -1
        elif self.state == "feed":
            #Feeding
            lam = -5
        else:
            #Moving
            if self.speed == SPEED_DIC["fly_speed"]:
                lam = 1
            if self.speed == SPEED_DIC["walking_speed"]:
                lam = 0.33
        

        self.energy = self.energy - lam * dt 
        
        return self.energy
        
    def updateState(self, dt, arena):
        """ Update Fly state"""

        #Idle/resting state
        if np.equal(self.position, self.aim).all():
            self.state = "rest"
            self.state = "idle"

        
        #Navigate until aiming point reached
        if not np.equal(self.position, self.aim).all():
            self.state = "navigate"
            pass
        
        #If a point of interest is in cognition range and aiming point is not closest interest
        if len(self.checkForInterest(arena)) != 0 and not np.equal(self.aim, self.getClosestInterest(arena)).all():
            visible_flies =  [fly for fly in arena.flies if self.InSigth(fly.position) and np.linalg.norm(fly.position - self.position) > 0]
            on_objective = [fly for fly in visible_flies if np.linalg.norm(self.aim - fly.position) < 1]
            if len(on_objective) == 0:
                self.state = "investigate"
                pass
        
        #If aiming position is reached
        if np.equal(self.position, self.aim).all() and self.energy > 80: 
            self.state = "explore"
            pass

        #If fly is on ood, it will feed
        if np.equal(self.position, arena.food.position).all() and self.energy < 100:
            self.state = "feed"

        #print(self.state, self.position, self.aim, np.linalg.norm(self.aim - self.position), arena.allowMove(self.position, self.aim), self.getRoom(arena))
        
        return self.state
    
    def updateSpeed(self, dt, arena):
        """ Update speed of fly depending of state and energy"""

        #Start walking
        if self.energy < 45:
            self.speed = SPEED_DIC["walking_speed"]
            pass

        #Resume flying
        if self.energy > 60:
            self.speed = SPEED_DIC["fly_speed"]
            pass
        
        return self.speed
   
    def updatePosition(self, dt, arena):
        """ Update position for a timestep depedning of agent state"""

        #Idle does nothing
        if self.state == "idle" or self.state == "rest":
            pass
        
        #Set a new random aiming point
        if self.state == "explore":
            pass
            
        #Agent flies to aiming point    
        if self.state == "navigate":
            min_dist = 1.1 * self.radius
            #If aiming point is far
            if np.linalg.norm(self.aim - self.position) >= self.speed * dt :
                
                new_position = self.position + (self.aim - self.position) * (self.speed * dt / np.linalg.norm(self.aim - self.position))
                
                print(self.position, arena.getRoomfromPos(self.position), new_position, arena.getRoomfromPos(new_position), self.aim, arena.getRoomfromPos(self.aim), 
                np.around(np.linalg.norm(self.position - new_position), 2), arena.allowMove(self.position, new_position))

                #print(self.position, new_position)
                
                #Avoidance between agents 
                #TODO : MODIFIY SECOND componenet of new_postion
                """close_flies = [fly for fly in arena.flies if np.linalg.norm(fly.position - self.position) < min_dist and np.linalg.norm(fly.position - self.position) > 0]
                if len(close_flies) > 0:
                    direction = np.array([np.cos(self.angle), np.sin(self.angle)]) 
                    theta = 0
                    #print("nb close flies", len(close_flies))
                    for other in close_flies:
                        other_vec = other.position - self.position
                        angle = np.arccos(np.dot(other_vec, direction) /  np.linalg.norm(other_vec))
                        #if angle <= self.sight_angle / 2:
                            #theta += angle / np.linalg.norm(other_vec)
                        theta += angle
                        #theta = np.random.normal(0, 1)
                        
                        #cos_theta = np.dot(other_vec, direction) / (np.linalg.norm(direction) * np.linalg.norm(other_vec))
                        #sin_theta = np.linalg.norm(np.cross(direction, other_vec)) / (np.linalg.norm(direction) * np.linalg.norm(other_vec))

                    theta = theta / len(close_flies)

                    rotation_mat = np.array([[np.cos(theta), -np.sin(theta)], [np.sin(theta), np.cos(theta)]])

                    new_position_  =  self.position + np.dot(rotation_mat, new_position) * np.linalg.norm(new_position - self.position) / np.linalg.norm(np.dot(rotation_mat, new_position))
                    
                    #print("old",np.linalg.norm(new_position - self.position), "angle", np.rad2deg(theta))

                    if np.linalg.norm(new_position - other.position) < np.linalg.norm(new_position_ - other.position):
                        pass
                        new_position = new_position_
                    #print("new",np.linalg.norm(new_position - self.position), np.linalg.norm(direction),  np.linalg.norm(np.dot(rotation_mat, new_position)))"""

                if arena.allowMove(self.position, new_position):
                    self.__Move(new_position)
                    
                
                else:
                    self.__generateNewAim(arena)


            #Last move to reach aiming point
            if np.linalg.norm(self.aim - self.position) < self.speed * dt :
                new_position = self.position + (self.aim - self.position)

                #print(self.position, arena.getRoomfromPos(self.position), new_position, arena.getRoomfromPos(new_position), self.aim, arena.getRoomfromPos(self.aim), 
                #np.around(np.linalg.norm(self.position - new_position), 2), arena.allowMove(self.position, new_position))

                if arena.allowMove(self.position, new_position):
                    self.__Move(new_position)
                
                else:

                    #print("Aim not valid", self.position, self.aim, arena.allowMove(self.position, self.aim))
                    #self.angle += np.pi

                    self.__generateNewAim(arena)
                    pass

        if self.state == "investigate":
            pass
                    

        return self.position
    
    def __generateNewAim(self, arena):
        """ Generate new random aiming position"""
        
        #New aiming step drawn from normal distribution
        if self.speed == SPEED_DIC["fly_speed"]:
            var = self.speed * 10
        if self.speed == SPEED_DIC["walking_speed"]:
            var = self.speed * 5
        if len(arena.walls) != 0:
            if self.getRoom(arena) == len(arena.walls):
                wall = arena.walls[0]
            else:
                wall = arena.walls[self.getRoom(arena)]

            while True:
                stepx = np.random.normal(0, var)
                stepy = np.random.normal(0, var)
                
                #new objective position in same room
                aim = np.array([self.position[0] + stepx, self.position[1] + stepy])

                #print("move ", arena.allowMove(self.position, aim)," Aim ", aim," room ",arena.getRoomfromPos(aim))
                
                entrance_list = [e for e in wall.entrances if not e.isFake]
                for entrance in entrance_list:

                    #print("On segment ", onSegment(entrance.getEdges(wall)[0], entrance.getEdges(wall)[1], np.double(self.position)), self.position, entrance.getEdges(wall), entrance.coord)
                    #print(arena.allowMove(self.position, aim), aim, arena.getRoomfromPos(aim))
                    
                    #if onSegment_(entrance.getEdges(wall)[0], entrance.getEdges(wall)[1], self.position):
                    #if DistanceToSegment(entrance.getEdges(wall)[0], entrance.getEdges(wall)[1], self.position) < wall.width:
                    if np.linalg.norm(entrance.coord - self.position) < entrance.radius:
                        #print("On entrance !", aim, arena.getRoomfromPos(aim))
                        
                        if self.getRoom(arena) == len(arena.walls):
                            if arena.getRoomfromPos(aim) == 1:
                                
                                #print("next room ! ", aim, arena.getRoomfromPos(aim))
                                
                                self.aim = aim
                                return self.aim
                        if arena.getRoomfromPos(aim) == self.getRoom(arena) + 1:
                            
                            #print("next room !", aim, arena.getRoomfromPos(aim))
                            
                            self.aim = aim
                            return self.aim
                        
                    
                    else:
                        if arena.getRoomfromPos(aim) == self.getRoom(arena):
                            self.aim = aim
                            return self.aim
        else:
            while True:
                stepx = np.random.normal(0, var)
                stepy = np.random.normal(0, var)
                
                #new objective position in same room
                aim = np.array([self.position[0] + stepx, self.position[1] + stepy])
                if arena.checkInArena(aim):
                    self.aim = aim
                    return self.aim
        
    def __Move(self, new_position):
        """ Agent moves from his position to a new one"""
        # Will perform move without any check of possibility!

        delta_position = new_position - self.position
        new_angle = np.arctan2(delta_position[1], delta_position[0])
        if new_angle < 0:
            new_angle += np.pi * 2

        self.angle = new_angle
        self.position = new_position
        return self.position

    def updateCognition(self, dt, arena):
        """ Environment update of fly"""
        return 0
    
    
    def getClosestInterest(self, arena):
        """ Get closest point of interest from fly position"""

        #Retrieve interest in FOV
        interests = self.checkForInterest(arena)
        #If there >1 interests, return closest one
        if len(interests) != 0:
            distances = [np.linalg.norm(i - self.position) for i in interests]
            return interests[np.argmin(distances)]
        #Return empty coord if no interest
        else:
            return []
    
    def checkForInterest(self, arena):
        """ Return points of interests in fly's cognition"""
        
        interests = []

        for i in self.checkVision(arena):
            #if arena.getRoomfromPos(i) == self.getRoom(arena):
            interests.append(i)
            pass
        
        return interests
        
    def checkVision(self, arena):
        """ Check for any interest point in vision field"""
        interests = []

        #Other flies in vision
        visible_flies = [fly for fly in arena.flies if self.InSigth(fly.position) and np.linalg.norm(fly.position - self.position) > 0]
        #TODO : manage nan results from np.arccos()
        #Retrieve wall leading to the next room
        if len(arena.walls) != 0:
            if self.getRoom(arena) == len(arena.walls):
                wall = arena.walls[0]
            else:
                wall = arena.walls[self.getRoom(arena)]
            
            #print("Current room ", self.getRoom(arena), wall.entrances)

            for entrance in wall.entrances:
                #print(onSegment_(wall.coord1, wall.coord2, self.position), wall.coord1, wall.coord2)

                #if not onSegment_(wall.coord1, wall.coord2, self.position):
                if DistanceToSegment(wall.coord1, wall.coord2, self.position) > wall.width:
                    #TODO Modify arbitrary condition for not blocking in the wall
                    #Ignore points already visited?
                    if self.InSigth(entrance.coord):
                            interests.append(entrance.coord)


        if arena.food.room == self.getRoom(arena):
            if self.InSigth(arena.food.position):
                interests.append(arena.food.position)


        return interests

    def InSigth(self, position):
        """ Return Boolean wether the position is in sigth or not"""

        #Vector to position
        u = position - self.position
        u_norm = np.linalg.norm(u)
        #Direction vector of length 1
        v = np.array([np.cos(self.angle), np.sin(self.angle)])

        #Position is in sight radius
        if u_norm < self.sight_radius and u_norm > 0:
            theta = np.arccos(np.dot(v, u) / u_norm)
            #Position is in sight angle
            if theta < self.sight_angle / 2:
                return True
            else:
                return False
        else :
            return False



    def __repr__(self):
        """ str representation"""

        position = "Position : " + str([self.position[0], self.position[1]])
        speed = "Speed : " + str(self.speed)
        cognition = "Cognition : " + str(self.sight_radius)
        sep = " / "
        strg = position + sep + speed + sep + cognition
        return strg
