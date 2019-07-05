# -*- coding: utf-8 -*-
"""
Created on Sun May 19 19:54:52 2019

@author: akasza
"""

import pygame
import OpenGL
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import copy
import os
import numpy as np
import math
import pickle


#Tuple representation of unit-cube vertices
vertices = (
        (1, 0, 0),
        (1, 1, 0),
        (0, 1, 0),
        (0, 0, 0),
        (1, 0, 1),
        (1, 1, 1),
        (0, 0, 1),
        (0, 1, 1)
        )

# Tuple representation of unit-cube edges - the numbers are indices
# of vertices which are to be connected
edges = (
        (0,1),
        (0,3),
        (0,4),
        (2,1),
        (2,3),
        (2,7),
        (6,3),
        (6,4),
        (6,7),
        (5,1),
        (5,4),
        (5,7)
        )

# Tuple representation of surfaces - numbers are indices of edges on which 
# the surface should be created
surfaces = (
    (0,1,2,3), #back
    (3,2,7,6), #left
    (6,7,5,4), #front
    (4,5,1,0), #right
    (1,5,7,2), #up
    (4,0,3,6) #down
    )


def coords_to_index(x, y, z):
    """Translates (x, y, z) coordinates to index in ZYX order."""
    return x*16**2 + y*16 + z
    
def index_to_coords(index):
    """Translates index to (x, y, z) coordinates in ZYX order."""
    c = index%16
    b = ((index-c)/16)%16
    a = ((index-c-16*b)/16**2)%16
    return (a, b, c)

class Camera:
    
    """Simple class containing rotation method so far."""
    def __init__(self):
        pass
        
    def rotate(self, pitch, yaw):
        """Rotates camera by given pitch and yaw angles in degrees."""
        buffer = glGetDoublev(GL_MODELVIEW_MATRIX)
        m = buffer.flatten()
        
        glRotate(yaw, m[1],m[5],m[9])
        glRotate(pitch, m[0],m[4],m[8])
        
        glRotated(-math.atan2(-m[4],m[5]) * \
                180.0/np.pi ,m[2],m[6],m[10])
        
        
        
        
        

class Cube:
    """Class representation of cube."""
    
    def __init__(self, x, y, z, color):
        global vertices, edges
        self.x = x
        self.y = y
        self.z = z
        self.color = color
        self.edges = copy.copy(edges)
        self.surfaces = copy.copy(surfaces)
        self.vertices = []
        
        #Create local copy of vertices offset by postion of the cube
        for vertex in vertices:
            self.vertices.append((vertex[0]+self.x, vertex[1]+self.y, vertex[2]+self.z))
        
        
        
        
    def drawSurface(self, surf):
            """Draws specified surface of the cube - 0-5 for back-left-front-right-up-down."""
            glColor3fv(self.color)
            for vertex in self.surfaces[surf]:
                glVertex3fv(self.vertices[vertex])
    
    
    def drawSurfaces(self):
        """Draws all surfaces of the cube."""
        for surface in self.surfaces:
            for vertex in surface:
                glColor3fv(self.color)
                glVertex3fv(self.vertices[vertex])
                
        """Draws all edges of the cube."""
    def drawEdges(self):
       for edge in self.edges:
            for vertex in edge:
                glColor3f(0, 0, 0)
                glVertex3fv(self.vertices[vertex])
                
#Below block classes extending cube class - for type recognition and color setting                
                
class Air(Cube):
    def __init__(self, x, y, z):
        Cube.__init__(self, x, y, z, None)

class Sand(Cube):
    def __init__(self, x, y, z):
        Cube.__init__(self, x, y, z, (1, 1, 0))
        
class Grass(Cube):
    def __init__(self, x, y, z):
        Cube.__init__(self, x, y, z, (0, 1, 0))
        
class Dirt(Cube):
    def __init__(self, x, y, z):
        Cube.__init__(self, x, y, z, (0.5, 0.25, 0.05))

class Stone(Cube):
    def __init__(self, x, y, z):
        Cube.__init__(self, x, y, z, (0.2, 0.2, 0.2))




class BlockArray():
    """Class designed to be used in optimization of hidden surface removal."""   
    def __init__(self, blocks):
        self.blocks = blocks
        
    def set_block(self, index, block):
        self.blocks[index] = block
    
    def set_block(self, x, y, z, block):
        if(x >= 0 and y >= 0 and z >= 0):
            set_block(coords_to_index(x, y, z), block)
    
    def get_block(self, index):
        return self.blocks[index]
    
    def get_block(self, x, y, z):
        if(x >= 0 and y >= 0 and z >= 0):
            return get_block(coords_to_index(x, y, z))
        return None #TODO other chunk
    
    def get_neighbour(self, x, y, z, side):
        return get_block(x+(side<4)*(side%2)*(side-2), y+(side>=4)*((-1)**(side)), z+(side<4)*((side+1)%2)*(side-1))
    
        
        

class Chunk:
    
    """Same as BlockArray. Represents 16x16x16 cubes set in space""" 
    def __init__(self, x, y, z, blocks):
        self.visibles = [[] for i in range(0, 16**3)]
    def neighbour_is_air(x, y, z, side):
        return type(self.blocks.get_neighbour(x, y, z, side)) == Air
    
    def update_visible(self):
        for index in range (0, 16**3):
            curr_block = self.blocks.get_block(index)
            if(type(curr_block)!=Air):
                x, y, z = index_to_coords(index)
                for side in range (0,6):
                    is_x = (side<4) and (side)
                    if(neighbour_is_air(x, y, z, side)):
                        most[side] = y
                        self.visibles[side] = curr_block
               
                for i in range (0,6):
                    self.visibles[i] = self.visibles[i].filter(lambda b : b!=[])
                    
        
def initialize_opengl():
    display = (800, 600)
    aspect = display[0]/display[1]
    fogColor = (135.0/255, 206.0/255, 250.0/255)
    #Initialize OpenGL settings
    pygame.display.set_mode(display, DOUBLEBUF|OPENGL)
    glMatrixMode(GL_PROJECTION)
    
    glFogi(GL_FOG_MODE, GL_LINEAR)
    glFogfv(GL_FOG_COLOR, fogColor)
    glHint(GL_FOG_HINT, GL_DONT_CARE)
    glFogf(GL_FOG_START, 10.0)
    glFogf(GL_FOG_END, 20.0)
    glEnable(GL_FOG);
    gluPerspective(75., aspect, 0.001, 100000.0);
    glClearDepth(1.0)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_CULL_FACE)
    glDepthFunc(GL_LEQUAL)
    glCullFace(GL_FRONT)
    glClear(GL_DEPTH_BUFFER_BIT);
    glClearColor(135.0/255, 206.0/255, 250.0/255, 1.0)
    glMatrixMode(GL_MODELVIEW)
    
def main():
    """Initialization of OpenGL, pygame and main loop."""
    
    cam = Camera()
    
    movement = [0, 0, 0]
    position = [0, 0, 0]
    display = (800, 600)
    
    blocks = {}
    
    #Load saved position and blocks if exist.
    try:
        blocks = pickle.load(open("blocks", "rb"))
        position = pickle.load(open("position", "rb"))
    except(FileNotFoundError):
        pass
    
    
    def add_block(block_type):
        buffer = glGetDoublev(GL_MODELVIEW_MATRIX)
        m = buffer.flatten()
        x = -int(position[0] + 0.3 + 3*m[2])
        y = -int(position[1] + 0.25+ 3*m[6])
        z = -int(position[2] + 1 + 3*m[10])
        index = coords_to_index(x, y, z)
        blocks[index] = block_type(x, y, z)
        print("Block added at: ", str(x),", ", str(y), ", ", str(z))
        
    def remove_block():
        buffer = glGetDoublev(GL_MODELVIEW_MATRIX)
        m = buffer.flatten()
        x = -int(position[0] + 0.3 + 3*m[2])
        y = -int(position[1] + 0.25+ 3*m[6])
        z = -int(position[2] + 1 + 3*m[10])
        index = coords_to_index(x, y, z)
        if index in blocks:
            del blocks[index]
            
    #Initialize pygame     
    pygame.init()
     
    initialize_opengl()
    
    #Stick mouse to the window
    pygame.mouse.set_visible(False)
    pygame.event.set_grab(True)
    
    #Move to saved position
    glTranslate(position[0], position[1], position[2])
    
    #Index of chosen block
    chosen_index = 0
    
    #List of available blocks
    block_list = [Dirt, Sand, Grass, Stone]
    
    while True:
        
        #Clear scene
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        
        #Set matrix mode
        glMatrixMode(GL_MODELVIEW)
        
        
        chosen_block = block_list[chosen_index%len(block_list)]
        
        buffer = glGetDoublev(GL_MODELVIEW_MATRIX)
        m = buffer.flatten()
        
        #Display coords info and chosen block type
        pygame.display.set_caption("MinePy: x: {:.3f}, y: {:.3f}, z: {:.3f} | Chosen block: {}".format(position[0], position[1], position[2], chosen_block.__name__))
        
        #Mouse and keyboard controls
        for event in pygame.event.get():
            
            #FPS Camera
            if event.type == pygame.MOUSEMOTION:
                
                rel = pygame.mouse.get_rel()
                
                #Motion of mouse on screen
                motionX = rel[0] 
                motionY = rel[1]
                
                #Move to (0, 0, 0), rotate, and move back to position.
                glTranslatef(-position[0], -position[1], -position[2])
                cam.rotate(90.0*(motionY)/display[1], 90.0*(motionX)/display[0])
                glTranslatef(position[0], position[1], position[2])
        
                
            
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
                
            #Keyboard controls (moving and exit)
            if event.type == pygame.KEYDOWN:
                
                if event.key == pygame.K_a:
                    movement[0] = 1
                if event.key == pygame.K_d:
                    movement[0] = -1
                
                if event.key == pygame.K_w:
                    movement[2] = 1
                if event.key == pygame.K_s:
                    movement[2] = -1   
                    
                if event.key == pygame.K_SPACE:
                    movement[1] = -1
                if event.key == pygame.K_LSHIFT:
                    movement[1] = 1
                    
                if event.key == pygame.K_ESCAPE:
                    pygame.mouse.set_visible(True)
                    pygame.event.set_grab(False)
                    pickle.dump(blocks, open("blocks", "wb"))
                    pickle.dump(position, open("position", "wb"))
            
            #Mouse controls - block operations
            if event.type == pygame.MOUSEBUTTONDOWN:
                if(event.button == 1):
                    add_block(block_type = chosen_block)
                if(event.button == 3):
                    remove_block()
                if(event.button == 4):
                    chosen_index += 1
                    chosen_block = block_list[chosen_index%len(block_list)]
                if(event.button == 5):
                    chosen_index -= 1
                    chosen_block = block_list[chosen_index%len(block_list)]
                
            
            #Stop movement on keyup
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_a or event.key == pygame.K_d:
                    movement[0] = 0
                if event.key == pygame.K_s or event.key == pygame.K_w:
                    movement[2] = 0
                if event.key == pygame.K_SPACE or event.key == pygame.K_LSHIFT:
                    movement[1] = 0
        
        # "Move the character"
        glTranslate(movement[2]*0.1*m[2], movement[2]*0.1*m[6], movement[2]*0.1*m[10]) #forward
        glTranslate(movement[0]*0.1*m[0], movement[0]*0.1*m[4], movement[0]*0.1*m[8]) #strafe
        glTranslatef(0, movement[1]*0.1, 0) #up and down
        
        #Update position vector
        position[0] += movement[2]*0.1*m[2]+movement[0]*0.1*m[0]
        position[1] += movement[2]*0.1*m[6]+movement[0]*0.1*m[4]+movement[1]*0.1
        position[2] += movement[2]*0.1*m[10]+movement[0]*0.1*m[8]
        
        #Draw edges for focuesed block in space
        x_foc = -int(position[0] + 0.3 + 3*m[2])
        y_foc = -int(position[1] + 0.25 + 3*m[6])
        z_foc = -int(position[2] + 1 + 3*m[10])
        
        focused = Air(x_foc, y_foc, z_foc)
        
        glBegin(GL_LINES)
        focused.drawEdges()
        glEnd()
        
        #Draw every cube
        for cube in blocks.values():
            glBegin(GL_QUADS)
            cube.drawSurfaces()
            glEnd()
        
        
        pygame.display.flip()
        pygame.time.wait(10)
        
main()