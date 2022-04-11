#### Simulation
import pygame
from pygame.locals import *
from matplotlib import scale
import matplotlib.pyplot as py
from arena2D import *
from Utility import * 


class FlySim2D:

    def __init__(self, arena, timestep, total_time):
        """ 2D Fly Simulator object"""

        self.arena = arena
        self.dt = timestep
        self.total_time = total_time

        self.flies_pos = []
        self.flies_state = []
        self.flies_aim = []
        for fly in self.arena.flies:
            self.flies_pos.append([fly.position])
            self.flies_state.append([fly.state])
            self.flies_aim.append([fly.aim])
    
    def runSim(self):
        """ Main simulation method"""


        time = 0
        while(time < self.total_time):
            self.updateSim(time)
            time += self.dt
            """#Update fly status
            for i, fly in enumerate(self.arena.flies):
                self.flies_state[i].append(fly.updateState(self.dt, self.arena))
                self.flies_pos[i].append(fly.updatePosition(self.dt, self.arena))
                self.flies_aim[i].append(fly.aim)
            

            
            #Update food status
            self.arena.food.update(self.dt)

            time += self.dt"""

        return 0

    def updateSim(self, time):
        """ Update simulation for one timestep"""
        if time < self.total_time:
            #Update fly status
            for i, fly in enumerate(self.arena.flies):
                state, position, energy, speed, aim = fly.update(self.dt, self.arena) 
                self.flies_state[i].append(state)
                self.flies_pos[i].append(position)
                self.flies_aim[i].append(aim)
            
            #Update food status
            self.arena.food.update(self.arena, self.dt)


        return 0
    def countMovement(self):
        """ Count how many moves/idles an agent made during the simulation"""
        #TODO : adapt code for future implementation (such as state of flies ....)

        #Lists of 0 and 1, 0 : idle, 1 : move
        move_list = []

        for fly in self.flies_pos:
            list_ = []
            for i, pos in enumerate(fly):
                if i + 1 < len(fly):
                    if pos[0] == fly[i + 1][0] and pos[1] == fly[i + 1][1]:
                        #Add 0 if the fly does not move
                        list_.append(0)
                    else :
                        #Add 1 if fly moves
                        list_.append(1)
            move_list.append(list_)
        
        #Reverse output to match agent index
        if len(move_list) > 1:
            return move_list[::-1] 
                    
        
        else:
            return move_list
                    
def DrawArena(screen, Sim, COLOR_DIC, DISPLAY_FACTOR, THICKNESS):
    center = Sim.arena.getCenter()
    radius = Sim.arena.radius

    center_display = [c * DISPLAY_FACTOR for c in center]
    radius_display = radius * DISPLAY_FACTOR

    background = COLOR_DIC["WHITE"]

    screen.fill(background)

    #Arena display
    #Length factor for window display
    #outer wall 
    pygame.draw.circle(screen, COLOR_DIC["BLACK"], center_display, radius_display, THICKNESS)
    #inner walls & entrances
    for i, w in enumerate(Sim.arena.walls):
        coord_display = w.coord1 * DISPLAY_FACTOR, w.coord2 * DISPLAY_FACTOR
        pygame.draw.line(screen, COLOR_DIC["BLACK"], coord_display[0], coord_display[1], THICKNESS)
        font = pygame.font.SysFont('Helvetica', 20)
        font_position_display = (Sim.arena.getRoomCenter(i + 1, 1.75)[0] * DISPLAY_FACTOR, Sim.arena.getRoomCenter(i + 1, 1.75)[1] * DISPLAY_FACTOR)
        room_number = font.render(str(i + 1), False, COLOR_DIC["BLACK"])
        screen.blit(room_number,font_position_display)
        for j, e in enumerate(w.getEntrancesCoord()):
            COLOR = COLOR_DIC["GREEN"]
            if w.entrances[j].isFake:
                COLOR = COLOR_DIC["RED"]
            start = ((e[0] - w.entrances[j].radius * np.cos(w.getAngle())) * DISPLAY_FACTOR, (e[1] - w.entrances[j].radius * np.sin(w.getAngle())) * DISPLAY_FACTOR) 
            end = ((e[0] + w.entrances[j].radius * np.cos(w.getAngle())) * DISPLAY_FACTOR, (e[1] + w.entrances[j].radius * np.sin(w.getAngle())) * DISPLAY_FACTOR)
            pygame.draw.line(screen, COLOR, start, end, 5)
    return 0


def main():
    #Simulation initialization
    center = [5.2, 5.2]
    radius = 5
    time = 0
    CA = CircleArena(center, radius, nb_rooms=4, nb_ent=3, nb_flies=0, starting_room=1, food_lifetime=100)
    Sim = FlySim2D(CA, 1, 10000)


    #Utility variable
    COLOR_DIC = {"WHITE":(255, 255,255), "BLACK":(0,0,0), "RED":(250, 100, 100), "BLUE":(0, 0, 255), "GREEN":(100, 200, 100), "PURPLE":(150, 100, 250), "ORANGE":(250, 150, 100)}
    STATE_DIC = {"idle":"Id", "explore":"Ex", "navigate":"N", "rest":"R", "investigate":"In", "walk":"W", "feed":"F"}
    #Pygame visualisation of the simulation
    #initialization
    pygame.init()
    pygame.font.init()

    DISPLAY_FACTOR = 100
    THICKNESS = 2
    center_display = [c * DISPLAY_FACTOR for c in center]
    radius_display = radius * DISPLAY_FACTOR

    size = radius_display * 2.1, radius_display * 2.1
    width, height = size
    background = COLOR_DIC["WHITE"]
    clock = pygame.time.Clock()
    #window definition
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption("Fly simulator")

    DrawArena(screen, Sim, COLOR_DIC, DISPLAY_FACTOR, THICKNESS)
    pygame.display.update()

    running = True
    pause = False

    while running:
        clock.tick(60 * 1/Sim.dt)
        event_list = pygame.event.get()
        for event in event_list:
            #print(event)
            if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    if event.key == pygame.K_p:
                        pause = True
                    if event.key == pygame.K_r:
                        main()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    #print(event.pos)
                    for f in Sim.arena.flies:
                        f.aim = np.array([event.pos[0] / DISPLAY_FACTOR, event.pos[1] / DISPLAY_FACTOR])
                    pass
            
            if event.type == pygame.QUIT:
                running = False
        
        while pause == True:
            #Pause state
            for event in pygame.event.get():
                if event.type==pygame.KEYDOWN:
                    if event.key==pygame.K_p:
                        pause = False
                    if event.key == pygame.K_ESCAPE:
                        pygame.QUIT()
                    if event.key == pygame.K_r:
                        main()
                if event.type == pygame.QUIT:
                    pygame.QUIT()


        if time == Sim.total_time:
            running = False
        DrawArena(screen, Sim, COLOR_DIC, DISPLAY_FACTOR, THICKNESS)
        #draw food
        food = Sim.arena.food
        food_display = (food.position[0] * DISPLAY_FACTOR, food.position[1] * DISPLAY_FACTOR)
        pygame.draw.circle(screen, COLOR_DIC["RED"], food_display, food.energy * 0.06 * THICKNESS)
        #food odor gradient 
        pygame.draw.circle(screen, COLOR_DIC["RED"], food_display, food.odor_radius * DISPLAY_FACTOR ,1)

        #Food timer
        font = pygame.font.SysFont('Helvetica', 18)
        font_position_display = (10,10)
        food_energy = "Food lifetime : " + str(np.trunc(food.maxlifetime - food.lifetime))
        food_energy_render = font.render(food_energy, False, COLOR_DIC["BLACK"])
        screen.blit(food_energy_render,font_position_display)
        #draw flies
        flies = Sim.arena.flies
        for fly in flies:
            #agent display
            fly_position_display = (fly.position[0] * DISPLAY_FACTOR, fly.position[1] * DISPLAY_FACTOR)
            fly_radius_display = fly.radius * DISPLAY_FACTOR 
            pygame.draw.circle(screen, COLOR_DIC["PURPLE"], fly_position_display, fly_radius_display, THICKNESS)
            #agent angle
            font = pygame.font.SysFont('Helvetica', 15)
            font_position_display = (fly_position_display[0] + 10, fly_position_display[1] + 10)
            text_angle = font.render(str(np.trunc(fly.angle * 180 / np.pi)), False, COLOR_DIC["BLACK"])
            fly_angle = np.arctan2(fly.position[1] - CA.center[1],fly.position[0] - CA.center[0])
            if fly_angle < 0:
                fly_angle += 2 * np.pi
            fly_angle_render = font.render(str(np.trunc(fly_angle * 180 / np.pi)), False, COLOR_DIC["BLACK"])
            fly_energy = str(np.trunc(fly.energy))
            fly_state_render = font.render(STATE_DIC[fly.state] + fly_energy, True, COLOR_DIC["BLACK"])
            screen.blit(fly_state_render,font_position_display)
            end_line = fly_radius_display * np.cos(fly.angle) + fly_position_display[0], fly_radius_display * np.sin(fly.angle) + fly_position_display[1]
            pygame.draw.line(screen, COLOR_DIC["PURPLE"], fly_position_display, end_line, THICKNESS)
            #angle of vision
            vision_rad_display = fly.sight_radius * DISPLAY_FACTOR
            phi = np.linspace(fly.angle - fly.sight_angle / 2, fly.angle + fly.sight_angle / 2, 45)
            x_cog_display = fly_position_display[0] + vision_rad_display * np.cos(phi)
            y_cog_display = fly_position_display[1] + vision_rad_display * np.sin(phi)
            vision_display = [(x, y) for x, y in zip(x_cog_display, y_cog_display)]
            vision_display.append(fly_position_display)
            pygame.draw.polygon(screen, COLOR_DIC["PURPLE"], vision_display, 1)
            #current aim 
            aim_display = fly.aim[0] * DISPLAY_FACTOR, fly.aim[1] * DISPLAY_FACTOR
            pygame.draw.circle(screen, COLOR_DIC["ORANGE"], aim_display, 8)
            #interests
            for interest in fly.checkForInterest(Sim.arena):
                if len(interest) != 0:
                    interest_display = (interest[0] * DISPLAY_FACTOR, interest[1] * DISPLAY_FACTOR )
                    pygame.draw.line(screen, COLOR_DIC["ORANGE"], fly_position_display, interest_display)
                    
                    font_position_display = (interest_display[0] + 10, interest_display[1] + 10)

                    """theta = np.arctan2(interest[1] - fly.position[1], interest[0] - fly.position[0])
                    if theta < 0:
                        theta += np.pi * 2
                    text_angle = font.render(str(np.trunc(theta * 180 / np.pi)), False, COLOR_DIC["BLACK"])
                    screen.blit(text_angle,font_position_display)"""

        font = pygame.font.SysFont('Helvetica', 15)
        #Position display
        font_position_display = ( pygame.mouse.get_pos()[0]+ 10, pygame.mouse.get_pos()[1] - 10)
        mouse_pos = font.render(str([pygame.mouse.get_pos()[0] / DISPLAY_FACTOR, pygame.mouse.get_pos()[1] / DISPLAY_FACTOR]), False, COLOR_DIC["BLACK"])
        screen.blit(mouse_pos, font_position_display)
        #Room display
        font_position_display_2 = ( pygame.mouse.get_pos()[0]+ 100, pygame.mouse.get_pos()[1] - 10)
        #Sim.arena.getRoomfromPos([pygame.mouse.get_pos()[0] / DISPLAY_FACTOR, pygame.mouse.get_pos()[1] / DISPLAY_FACTOR])

        room_nb = font.render(str(Sim.arena.getRoomfromPos([pygame.mouse.get_pos()[0] / DISPLAY_FACTOR, pygame.mouse.get_pos()[1] / DISPLAY_FACTOR])), False, COLOR_DIC["BLACK"])
        screen.blit( room_nb, font_position_display_2)
        #Food odor strength display
        odor_strength = font.render(str(np.around(food.GetGradient(np.array([pygame.mouse.get_pos()[0] / DISPLAY_FACTOR, pygame.mouse.get_pos()[1] / DISPLAY_FACTOR])), 2)), False, COLOR_DIC["BLACK"])
        #screen.blit(odor_strength, font_position_display)

        

        Sim.updateSim(time)
        time += Sim.dt


        
        pygame.display.update()
    pygame.quit()
    for state in Sim.flies_state:
        val, count = np.unique(state, return_counts=True)
        print("State ", val," Count ", count)


if __name__ == "__main__" :
    main()