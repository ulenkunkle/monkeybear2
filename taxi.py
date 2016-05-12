import numpy as np
import sys
import pygame as pg
import os
import time
from six import StringIO
import random

from gym import spaces, utils
from gym.envs.toy_text import discrete

MAP = [
    "+---------+",
    "|R: | : :G|",
    "| : : : : |",
    "| : : : : |",
    "| | : | : |",
    "|Y| : |B: |",
    "+---------+",
]

class TaxiEnv(discrete.DiscreteEnv):
    """
    The Taxi Problem
    from "Hierarchical Reinforcement Learning with the MAXQ Value Function Decomposition"
    by Tom Dietterich

    rendering:
    - blue: passenger
    - magenta: destination
    - yellow: empty taxi
    - green: full taxi
    - other letters: locations

    """
    metadata = {'render.modes': ['human', 'ansi']}

    def __init__(self):
        pg.init()
        self.player = pg.image.load('dude.png')
        self.player2 = pg.image.load('dude2.png')
        self.player3 = pg.image.load('dude3.png')
        self.player4 = pg.image.load('Map1.png')
        self.desc = np.asarray(MAP,dtype='c')
        

        self.locs = locs = [(0,0), (0,4), (4,0), (4,3)]
        self.dir = ["South", "North", "East", "West", "Pickup", "Dropoff"]

        nS = 500
        nR = 5
        nC = 5
        maxR = nR-1
        maxC = nC-1
        isd = np.zeros(nS)
        nA = 6
        P = {s : {a : [] for a in range(nA)} for s in range(nS)}
        for row in range(5):
            for col in range(5):
                for passidx in range(5):
                    for destidx in range(4):
                        if passidx < 4 and passidx != destidx: 
                            isd[state] += 1                        
                        for a in range(nA):
                            state = self.encode(row, col, passidx, destidx)
                            # defaults
                            newrow, newcol, newpassidx = row, col, passidx
                            reward = -1
                            done = False
                            taxiloc = (row, col)

                            if a==0:
                                newrow = min(row+1, maxR)
                            elif a==1:
                                newrow = max(row-1, 0)
                            if a==2 and self.desc[1+row,2*col+2]==":":
                                newcol = min(col+1, maxC)
                            elif a==3 and self.desc[1+row,2*col]==":":
                                newcol = max(col-1, 0)
                            elif a==4: # pickup
                                if (passidx < 4 and taxiloc == locs[passidx]):
                                    newpassidx = 4
                                else:
                                    reward = -10
                            elif a==5: # dropoff
                                if (taxiloc == locs[destidx]) and passidx==4:
                                    done = True
                                    reward = 20
                                elif (taxiloc in locs) and passidx==4:
                                    newpassidx = locs.index(taxiloc)
                                else:
                                    reward = -10
                            newstate = self.encode(newrow, newcol, newpassidx, destidx)
                            P[state][a].append((1.0, newstate, reward, done))
        isd /= isd.sum()
        discrete.DiscreteEnv.__init__(self, nS, nA, P, isd)

        self.observation_space = spaces.Discrete(500)
        self.action_space = spaces.Discrete(6)

    def encode(self, taxirow, taxicol, passloc, destidx):
        # (5) 5, 5, 4
        i = taxirow
        i *= 5
        i += taxicol
        i *= 5
        i += passloc
        i *= 4
        i += destidx
        return i

    def decode(self, i):
        out = []
        out.append(i % 4)
        i = i // 4
        out.append(i % 5)
        i = i // 5
        out.append(i % 5)
        i = i // 5
        out.append(i)
        assert 0 <= i < 5
        return reversed(out)

    def _render(self, mode='human', close=False):
        font = pg.font.SysFont("comicsansms", 72)
        buzzdude = random.randint(0,19)
        duzzdude = random.randint(0,29)
        duzzbude = random.randint(0,39)
        text_color = (210, 210, 210)
        #msg2 = font.render("Hello, World", True, (0, 128, 0))
        if close:
            return

        outfile = StringIO() if mode == 'ansi' else sys.stdout

        out = self.desc.copy().tolist()
        out = [[c.decode('utf-8') for c in line] for line in out]
        taxirow, taxicol, passidx, destidx = self.decode(self.s)
        screen = pg.display.set_mode((350, 500))
        def ul(x): return "Q" if x == " " else x
        if passidx < 4:
            out[1+taxirow][2*taxicol+1]# = utils.colorize(out[1+taxirow][2*taxicol+1], 'yellow', highlight=True)
            print[1+taxirow]
            print taxirow
            
            
            pi, pj = self.locs[passidx]
            out[1+pi][2*pj+1]# = utils.colorize(out[1+pi][2*pj+1], 'blue', bold=True)
            
            screen.blit(self.player2, (2*(29+pi),18*(pj+1)))
            #pg.display.flip()
        else: # passenger in taxi
            out[1+taxirow][2*taxicol+1]# = utils.colorize(ul(out[1+taxirow][2*taxicol+1]), 'green', highlight=True)
        
        di, dj = self.locs[destidx]
        #screen.blit(msg2,(300,200))
        #screen.blit(text,(300,200))
        screen.blit(self.player4,(1+buzzdude,1+buzzdude))
        screen.blit(self.player, (67*taxirow,67*taxicol+1))
        screen.blit(self.player3, (duzzbude+5*(29+di),duzzdude+10*(dj+1)))
        #pg.display.flip()
        time.sleep(0.5)
        out[1+di][2*dj+1] = utils.colorize(out[1+di][2*dj+1], 'magenta')
        outfile.write("\n".join(["".join(row) for row in out])+"\n")
        if self.lastaction is not None:
            outfile.write("  ({})\n".format(["South", "North", "East", "West", "Pickup", "Dropoff"][self.lastaction]))
            tmp = self.lastaction
            #self.msg1 = outfile.write
            msg1= self.dir[tmp]#msg2 = msg1
            msg2 = font.render(msg1,1,text_color)
            if self.lastaction is not None:
                screen.blit(msg2,(45,350))
            pg.display.flip()
        else: outfile.write("\n")

        # No need to return anything for human
        if mode != 'human':
            return outfile
