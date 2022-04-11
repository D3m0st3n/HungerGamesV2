from matplotlib import pyplot as plt
from Simulation2D import *



def main():
    CA = CircleArena([5, 5], 5, nb_rooms=5, nb_ent=3, nb_flies=10, starting_room=1)
    Sim = FlySim2D(CA, 0.1, 10)
    #Potting of simulation
    Sim.runSim()
    move_list = Sim.countMovement()
    #Plot simulation
    coord = Sim.arena.getCoordinates(180)
    plt.plot(coord[0], coord[1])
    for i, w in enumerate(Sim.arena.walls):

        #print("wall info ", w.getEntrancesCoord())
        #print("Wall angle : ", w.getAngle())

        plt.plot([w.coord1[0], w.coord2[0]], [w.coord1[1], w.coord2[1]], color="orange")
        room_center = Sim.arena.getRoomCenter(i + 1, scale = 1.75)
        #print("Room ", i + 1, " center : ", room_center)
        #plt.scatter(room_center[0], room_center[1], marker="x", color ="COLOR_DIC["black"]")
        plt.annotate(i + 1, room_center)
        Fake = [e.isFake for e in w.entrances]
        colors = ["green", "red"]
        for i, c in enumerate(w.getEntrancesCoord()):
            plt.scatter(c[0], c[1], marker="o", edgecolor=colors[Fake[i]], facecolor = "none")
    
    #Plot fly trajectory
    for list_pos in Sim.flies_pos:
        X = []
        Y = []
        for pos in list_pos:
            X.append(pos[0])
            Y.append(pos[1])
        plt.scatter(X[0], Y[0], marker = "x", color = "green", alpha = 0.8)
        plt.annotate("s", [X[0], Y[0]])
        plt.scatter(X[-1], Y[-1], marker = "x", color = "red", alpha = 0.8)
        plt.annotate("e", [X[-1], Y[-1]])
        #maker
        plt.plot(X, Y, marker = "x", alpha = 0.3)
        #no marker
        #plt.plot(X, Y, alpha = 0.3)

    
    #Plot aiming points
    for list_state, list_aim in zip(Sim.flies_state, Sim.flies_aim):
        #print(np.unique(list_aim))
        for i, aim in enumerate(list_aim):
            if list_state[i] == "investigate":
                plt.scatter(aim[0], aim[1], marker = "x", color = "purple", alpha = 0.25)
            else:
                if i > len(list_aim) - 10:
                    plt.scatter(aim[0], aim[1], marker = "x", color = "red", alpha = 0.25)
                pass
    

    plt.scatter(Sim.arena.food.position[0], Sim.arena.food.position[1], marker="o", color = "red")

    for fly in Sim.flies_state:
        val, count = np.unique(fly, return_counts=True)
        print("State ", val, " count :  ", count)



    plt.xlim(-1, 11)
    plt.ylim(0, 10)
    #plt.xlim(4.75, 10.25)
    #plt.ylim(4.75, 10.25)

    plt.xlabel("X")
    plt.ylabel("Y")

    plt.show()
    for i in range(10):
        #print(np.random.poisson(1), np.random.poisson(0.1), np.random.poisson(0.01))
        pass

if __name__ == "__main__" :
    main()