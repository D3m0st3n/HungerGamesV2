#### Food object

from operator import pos
import numpy as np 


class Food:
    """ Food class object"""

    def __init__(self, position, room, lifetime, arena):
        """ Food object initialization"""
        
        if arena.checkInArena(position):
            self.position = position
        else: 
            self.position = arena.getRoomCenter(room)
        #self.room = arena.getRoomfromPos(self.position)
        self.room = room

        self.energy = 100

        self.maxlifetime = lifetime
        self.lifetime = 0

        #Parameters to define odor gradient
        #Distance to which gradient extend
        self.odor_radius = 2
        #Starting strength of gradient
        self.odor_strength = 10

    def update(self, arena, dt):
        
        #Update lifetime
        if self.lifetime < self.maxlifetime:
            self.lifetime += 1 * dt

        #Switch room once max lifetime is reached
        if self.lifetime >= self.maxlifetime:
        
            new_room = self.room + 1
            if new_room > len(arena.walls):
                new_room = 1

            self.SwitchRoom(new_room, arena)
        
        return 0

    def SwitchRoom(self, room, arena):
        """ Switch food from room"""
        #New room
        self.room = room
        #New position at center of room
        self.position = arena.getRoomCenter(room)
        #Reset lifetime
        self.lifetime = 0

        return self.position, self.room
    
    def SwitchPosition(self, position, arena):
        """ Switch food to new position"""

        #New position
        if arena.checkInArena(position):
            new_room = arena.getRoomfromPos(position)
            #Check if room is valid
            if new_room > 0 and new_room <= len(arena.walls):
                self.position = position
                self.room = new_room
        #Reset lifetime
        self.lifetime = 0

        return self.position, self.room

    def GetGradient(self, position):
        """ Return gradient strength value i.e. odor strength"""
        
        if np.linalg.norm(self.position - position) > self.odor_radius:
            #If position is outside gradient
            return 0
        return self.odor_strength * (1 - 1/self.odor_radius**2 * ((position[0] - self.position[0])**2 + (position[1] - self.position[1])**2))