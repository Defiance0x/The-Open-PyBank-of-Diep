import os
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"

import numpy as np

from mpi4py import MPI

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()


class NBody():

    def __init__(self):
           
        angv = 1/(3.145e7*10000) #* 250e6)
        self.r = np.random.uniform(0.1,1)*1e3*3e8*3.2e7 # ly to m
        #theta = np.random.uniform(0, 2*np.pi)
        self.x = self.r*np.cos(np.random.uniform(0,2*np.pi))
        self.y = self.r*np.sin(np.random.uniform(0,2*np.pi))#1.5e3
        self.m = np.random.uniform(0.5,8)*2e30 # 0.5-8 solar masses in kg
        
        self.pos = np.array([self.x, self.y]) # array needed to vectorise
        
        self.perp_vect = np.array([-self.y,self.x])
        self.perp_unit_vect = self.perp_vect/np.linalg.norm(self.pos) # (-y,x) = anticlockwise
        
        self.vx = self.perp_unit_vect[0]*angv*self.r#np.random.uniform(1e-5,1)*100e3 # m/s
        #self.vy = np.sqrt(100e3**2 - self.vx**2)*self.perp_unit_vect[1]
        # actually between 200-250 km/s for orbital velocity
        self.vy = self.perp_unit_vect[1]*angv*self.r#np.random.uniform(0.8,1)*100e3 # m/s
        self.ax = 0
        self.ay = 0

        self.vel = np.array([self.vx, self.vy])
        self.acc = np.array([self.ax, self.ay])
        

    def update_velocity(self, dt):
        #print("before",self.vel)
        self.vel = self.vel + self.acc*dt
        #print("after",self.vel)
        return self.vel

    def update_position(self, dt):
        self.pos = self.pos + self.vel*dt
        return self.pos
    
    def get_mass(self):
        return self.m
    
    def get_acceleration(self):
        return self.acc
    
    def get_velocity(self):
        return self.vel
    
    def get_position(self):
        return self.pos


def send_to_master(N): # workers send lists to be compiled by the master

    bodies = []

    
    if rank == 0: # master node appends the newtonian blackhole
     

        Newtonian_Blackhole = NBody().__new__(NBody) # __new__ ignores constructor
        Newtonian_Blackhole.m = 2.6e15 * 1.989e30
        Newtonian_Blackhole.pos = np.array([0,0])
        Newtonian_Blackhole.vel = np.array([0,0])
        Newtonian_Blackhole.acc = np.array([0,0])
    
        bodies.append(Newtonian_Blackhole) # adding the blackhole

    for i in np.arange(start = int(rank*N/size), stop = int((rank+1)*N/size), step = 1): # must be int since can't have 0.5 stars
        temp = NBody() # size nodes append into list
        bodies.append(temp)


    print("Rank ",rank, "has number of objects = ",len(bodies))
    if rank != 0:
        comm.send(bodies, dest=0)
    
    if rank == 0:
        for i in np.arange(start = 1, stop = size, step = 1): # (1, size) skips the master node
            bodies += comm.recv(source=i)
        #print("Number of bodies on master node: ", len(bodies))
    

    return bodies

def redist(bodies): # redistributes list of bodies
    if rank != 0:
        bodies = []
    if rank == 0:
        for i in np.arange(start = 1, stop = size, step = 1):
            comm.send(bodies,dest=i)
    if rank != 0:
        bodies += comm.recv(source=0)
    return bodies

#@cython.boundscheck(False)  # Deactivate bounds checking
#@cython.wraparound(False)   # Deactivate negative indexing.


def force_integrator(bods):

    t1 = MPI.Wtime()
    
    ### attempted optimisation ###
#    cdef float dt = 3.145e7 #* 250e6/400
#    cdef float time_end =  3.145e7 * 1000 #* 250e6 *4 # seconds in a year * x years
#    cdef int i
#    cdef float G = 6.673e-11
#    cpdef int start, stop
    
    dt = 3.145e7
    time_end =  3.145e7 * 1000
    G = 6.673e-11
    
#    fig = plt.figure()
#    ims = []
    
    
    for time_step in np.arange(0, time_end, step = dt):

        
        xc = [] # reset the positions to make it so no slug trail is left on the 
        yc = [] # animation

        for i in np.arange(start = int(rank*len(bods)/size),stop = int((rank+1)*len(bods)/size)): # takes body i_1 then does F = ma with body
            for j in np.arange(start = 0, stop = len(bods)): # j_1, j_2, j_3 etc
                if i == j:
                    continue # stops division by zero and commands i != j

                r_vec = bods[i].get_position() - bods[j].get_position()
                r_mag = np.linalg.norm(r_vec)
                r_hat = r_vec/r_mag
                acc = -G*bods[j].get_mass()/(r_mag**2)*r_hat
                bods[i].acc = np.array([acc[0],acc[1]])

            bods[i].update_velocity(dt)
            bods[i].update_position(dt)
            xc.append(bods[i].pos[0])
            yc.append(bods[i].pos[1])
            
        if rank != 0:
            comm.send(xc,dest=0)
        if rank == 0:
            for i in np.arange(start = 1, stop = size):
                xc += comm.recv(source=i)
        if rank != 0:
            comm.send(yc,dest=0)
        if rank == 0:
            for i in np.arange(start = 1, stop = size):
                yc += comm.recv(source=i)

#        if rank == 0:
#            
#            step = plt.scatter(xc,yc,color='b') # make one node collect data
#            ims.append([step]) # same for this line
#    
#    if rank == 0:
#    
#        ani = animation.ArtistAnimation(fig, ims, interval = 10)
#    
#        ani.save("Cython_Simulation_15.mp4")
    
    

    t2 = MPI.Wtime()
    
    print("rank = ",rank,", Time Lapsed = ", t2-t1)

    return

"""  Set up for N-bodies  """

N = 500 # N = number of stars in galaxy

"""  Animation & Force Integrator  """

bodss = redist(send_to_master(N))

force_integrator(bodss)
