# Author: Luke Swanson
# Date: 2023March11
# Some optimizations suggested by ChatGPT

# Some resources used:
#https://en.wikipedia.org/wiki/Bresenham%27s_line_algorithm
#https://youtu.be/p4Iz0XJY-Qk
#https://en.wikipedia.org/wiki/Rotation_matrix
#https://pythonforundergradengineers.com/how-to-do-trig-with-Python

from pynput import mouse
from win32gui import FindWindow, GetWindowText, GetForegroundWindow, GetWindowRect

import os
import math

import numpy as np
from stl import mesh

# Converts an STL file to points in 3D space:
def stl_to_points(stl_location):
    stl_data = mesh.Mesh.from_file(stl_location)
    points = stl_data.points.reshape([-1, 3])
    
    point_list = np.unique(points, axis=0)
    
    all_points = []
    
    for i in point_list:
        i = list(i)
        all_points.append(i)
        
    x_max = max(all_points, key=lambda x: x[0])[0]
    x_min = min(all_points, key=lambda x: x[0])[0]
    
    y_max = max(all_points, key=lambda x: x[1])[1]
    y_min = min(all_points, key=lambda x: x[1])[1]
    
    z_max = max(all_points, key=lambda x: x[2])[2]
    z_min = min(all_points, key=lambda x: x[2])[2]
    
    x_avg = (x_max+x_min)/2
    y_avg = (y_max+y_min)/2
    z_avg = (z_max+z_min)/2
    
    for i in all_points:
        i[0] -= x_avg
        i[1] -= y_avg
        i[2] -= z_avg
    
    x_max = max(all_points, key=lambda x: x[0])[0]
    y_max = max(all_points, key=lambda x: x[1])[1]
    z_max = max(all_points, key=lambda x: x[2])[2]
    
    max_value = max(x_max,y_max,z_max)
    
    for i in all_points:
        i[0] = i[0]/max_value
        i[1] = i[1]/max_value
        i[2] = i[2]/max_value
    
    return all_points

# If delta x is less than delta y
def plotLineLow(x0, y0, x1, y1):
    dx = x1 - x0
    dy = y1 - y0
    yi = 1
    if dy < 0:
        yi = -1
        dy = -dy
    D = 2 * dy - dx
    y = y0

    for x in range(x0, x1+1):
        board_list.add((x,y,0))
        if D > 0:
            y += yi
            D += 2 * (dy - dx)
        else:
            D += 2 * dy

# If delta y is less than delta x
def plotLineHigh(x0, y0, x1, y1):
    dx = x1 - x0
    dy = y1 - y0
    xi = 1
    if dx < 0:
        xi = -1
        dx = -dx
    D = 2 * dx - dy
    x = x0

    for y in range(y0, y1+1):
        board_list.add((x,y,0))
        if D > 0:
            x += xi
            D += 2 * (dx - dy)
        else:
            D += 2 * dx
            
# Connects the points using Bresenham's algorithm:
def connect(point_1,point_2):
    x0,y0,z0 = point_1
    x1,y1,z1 = point_2
    
    z0 = round(z0,3)
    z1 = round(z1,3)
    
    #board_list.add((x0,y0,0))
    #board_list.add((x1,y1,0))
    
    if abs(y1 - y0) < abs(x1 - x0):
        if x0 > x1:
            plotLineLow(x1, y1, x0, y0)
        else:
            plotLineLow(x0, y0, x1, y1)
    else:
        if y0 > y1:
            plotLineHigh(x1, y1, x0, y0)
        else:
            plotLineHigh(x0, y0, x1, y1)

# Checks if a point is within the bounds of the board, if it is, it adds the point:
def create_board(board, board_list, width, height):
    for point in board_list:
        x,y,z = point
        if x < width and x > 0 and y < height and y > 0:
            board[y][x] = marker

    return board

# Centers all points around a point:
def offset(points,offset_point,cur_scale):
    points[0] = int(points[0]*2*cur_scale) + offset_point[0]
    points[1] = int(points[1]*cur_scale) + offset_point[1]
    return points

# Calculates how much to rotate the points:
def mouse_angle(center_point,pointer_point,width,height):
    y_angle = ((center_point[0] - pointer_point[0])/width)*2*math.pi
    x_angle = -((center_point[1] - pointer_point[1])/height)*2*math.pi
    return [x_angle,y_angle]

# Prints the board :D
def print_board(board,width,height):
    # Goes through each point on the board, and prints it :D
    os.system("cls")
    # In Python, join() is a string method that concatenates a list of strings using a specified delimiter.
    # In this case, the delimiter is "\n"
    print("\n".join(["".join(row) for row in board]))
        
# Called when the mouse moves:
def on_move(x, y):
    global mouse_pos
    mouse_pos = [x, y]
    listener.stop()
    
# Called when the mouse wheel is scrolled:
def on_scroll(x, y, dx, dy):
    global scale
    if dy > 0:
        scale += 1
    else:
        scale -= 1
        
    if scale <= 0:
        scale = 0
    listener.stop()

# Matrix multiplication [3x3]*[1x3]
def matrix(matrixA,matrixB):
    x = (matrixA[0][0]*matrixB[0] + matrixA[1][0]*matrixB[1] + matrixA[2][0]*matrixB[2])
    y = (matrixA[0][1]*matrixB[0] + matrixA[1][1]*matrixB[1] + matrixA[2][1]*matrixB[2])
    z = (matrixA[0][2]*matrixB[0] + matrixA[1][2]*matrixB[1] + matrixA[2][2]*matrixB[2])
    return [x,y,z]


# MAIN CODE
def MAIN_CODE():
    placeholder = 0

stl_location = input("Enter stl location: ")
scale = int(input("Enter size: "))
cur_scale = 0
mouse_pos = []

row, col = 0,0
cur_row, cur_col = 0,0

width, height = 0,0
cur_width, cur_height = 0,0

all_points = stl_to_points(stl_location)
marker = "•"

while True:
    with mouse.Listener(on_scroll=on_scroll, on_move=on_move) as listener:
        listener.join()  
    
    # Location of the mouse pointer:
    mouse_pos_x, mouse_pos_y = mouse_pos
    
    # Locations of the display window:
    window_top_x, window_top_y, window_bottom_x, window_bottom_y = GetWindowRect(GetForegroundWindow())
    
    mouse_pos_y = min(mouse_pos_y, window_bottom_y)
    mouse_pos_x = max(window_top_x, min(mouse_pos_x, window_bottom_x - 32))
    
    col = max(((mouse_pos_x - window_top_x)//8)-1,0)
    row = max(((mouse_pos_y - window_top_y)//16)-2,0)

    width = ((window_bottom_x-window_top_x)//8)-4
    height = ((window_bottom_y-window_top_y)//16)-3
    
    # Updates the screen when the mouse is moved.    
    if (cur_col, cur_row, cur_scale) != (col, row, scale):
        cur_scale, cur_col, cur_row = scale, col, row

        vector = []
        for point in all_points:
            vector.append(point)

        # Creating board to put markers onto.
        board = [[" " for x_num in range(width)] for y_num in range(height)]
        
        center_point = [width//2,height//2]
        pointer_point = [cur_col,cur_row]
        
        offset_point = center_point
        
        # Rotation angles
        x_angle = mouse_angle(center_point,pointer_point,width,height)[0]
        y_angle = mouse_angle(center_point,pointer_point,width,height)[1]
        
        # Definition matrices:
        projection_matrix = ((1,0,0),(0,1,0),(0,0,0))
        rotate_z = ((math.cos(x_angle),math.sin(x_angle),0),(-math.sin(x_angle),math.cos(x_angle),0),(0,0,1))
        rotate_x = ((1,0,0),(0,math.cos(x_angle),math.sin(x_angle)),(0,-math.sin(x_angle),math.cos(x_angle)))
        rotate_y = ((math.cos(y_angle),0,-math.sin(y_angle)),(0,1,0),(math.sin(y_angle),0,math.cos(y_angle)))                
        
        # Rotation about the y-axis.
        for array in range(len(vector)):
            vector[array] = matrix(rotate_y,vector[array])
        
        # Roation about the x-axis,    
        for array in range(len(vector)):
            vector[array] = matrix(rotate_x,vector[array])
        
        # Rotation about the z-axis.
        #for array in range(len(vector)):
            #for point in range(len(vector[array])):
                #vector[array][point] = matrix(rotate_x,vector[array][point])
        
        # Projecting a 3D object onto a 2D plane.
        projection = []
        for array in vector:
            projection.append(offset(matrix(projection_matrix,array),offset_point,cur_scale))
        
        # Connects the points in the same planes
        #for z_positions in range(len(projection)):
            #for points in range(len(projection[z_positions])):                        
                #if points == len(projection[z_positions])-1:
                    #connect(board_list,projection[z_positions][point],projection[z_positions][0])
                #else:
                    #connect(board_list,projection[z_positions][points],projection[z_positions][points+1])
        
        # Connects the planes together
        #for z_positions in range(len(projection)-1):
            #for points in range(len(projection[z_positions])):
                #connect(board_list,projection[z_positions][points],projection[z_positions+1][points])
        
        #print(len(projection))
        board = create_board(board,projection,width,height)
        print_board(board,width,height)