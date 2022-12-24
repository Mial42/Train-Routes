from collections import deque
import time
import sys
import random
from heapq import heappush, heappop
from math import pi, acos, sin, cos
from tkinter import *
from tkinter.ttk import *
#from PIL import Image, ImageTk

master = Tk()
master.geometry('1200x700')
w = Canvas(master, width=1000, height=700) #Setting up the Tkinter window and canvas
w.pack()

beg = time.perf_counter()


def calcd(y1, x1, y2, x2):
    if y1 == y2 and x1 == x2:
        return 0
    y1 = float(y1)
    x1 = float(x1)
    y2 = float(y2)
    x2 = float(x2)
    R = 3958.76  # miles = 6371 km
    y1 *= pi / 180.0
    x1 *= pi / 180.0
    y2 *= pi / 180.0
    x2 *= pi / 180.0
    return acos(sin(y1) * sin(y2) + cos(y1) * cos(y2) * cos(x2 - x1)) * R


node_lat_long = {}  # Nodes to latitude and longitude
city_to_node = {}  # City to Node
edges = {}
edge_to_distance = {}


def build_lat_long(filename):
    with open(filename) as f:
        for line in f:
            temp = line.split(" ")
            node, latitude, longitude = temp[0].strip(), temp[1].strip(), temp[2].strip()
            node_lat_long[node] = (latitude, longitude)


build_lat_long("rrNodes.txt")


def heuristic(node1, node2):
    y1, x1 = node_lat_long[node1]
    y2, x2 = node_lat_long[node2]
    return calcd(y1, x1, y2, x2)


def build_city_nodes(filename):
    with open(filename) as f:
        for line in f:
            node = line[0:7].strip()
            city = line[8:].strip()
            city_to_node[city] = node


def build_edge_to_distance(filename):
    with open(filename) as f:
        for line in f:
            node1, node2 = line.strip().split(' ')
            x = heuristic(node1, node2)
            edge_to_distance[(node1, node2)] = x
            edge_to_distance[(node2, node1)] = x


build_edge_to_distance('rrEdges.txt')

build_city_nodes("rrNodeCity.txt")


def build_edges(filename):  # Needs reworking: node1 can have more than one connection!
    with open(filename) as f:
        for line in f:
            temp = line.strip().split(" ")
            node1, node2 = temp[0], temp[1]
            if node1 in edges and node2 in edges:
                arr = edges[node1]
                arr.append(node2)
                edges[node1] = arr
                arr = edges[node2]
                arr.append(node1)
                edges[node2] = arr
            elif node1 in edges:
                arr = edges[node1]
                arr.append(node2)
                edges[node1] = arr
                edges[node2] = [node1]
            elif node2 in edges:
                arr = edges[node2]
                arr.append(node1)
                edges[node2] = arr
                edges[node1] = [node2]
            else:
                edges[node1] = [node2]
                edges[node2] = [node1]


build_edges("rrEdges.txt")


def get_children(node):
    try:
        return edges[node]
    except:
        return []


fin = time.perf_counter()

time_to_make_data_structures = (fin - beg)


def draw_coordinates():
    for edge in edges:
        end_nodes = edges[edge]
        for end_node in end_nodes:
            y1, x1 = node_lat_long[edge]
            y2, x2 = node_lat_long[end_node]
            x1, y1, x2, y2 = convert_lat_long_to_canvas(x1, y1, x2, y2)
            w.create_line(x1, y1, x2, y2) #x1 y1 x2 y2


def reset_command():
    w.delete("line")


# def mark_the_correct_path(city1, city2):
#     x = 0
#     start, end = city_to_node[city1], city_to_node[city2]
#     correct_path = {start:None} #Child:Parent
#     closed = set()
#     fringe = [(0, start, 0)]
#     while fringe:
#         heur, v, distance = heappop(fringe)
#         if v == end:
#             key = v
#             path = []
#             while key is not None:
#                 path.append(key)
#
#                 y1, x1 = node_lat_long[key]
#                 y2, x2 = node_lat_long[correct_path[key]]
#                 x1, y1, x2, y2 = convert_lat_long_to_canvas(x1, y1, x2, y2)
#                 w.create_line(x1, y1, x2, y2, fill="#1c1cf0", tags='line')
#
#                 key = correct_path[key]
#                 x = x + 1
#             return distance
#         if v not in closed:
#             closed.add(v)
#             children = get_children(v)
#             for child in children:
#                 correct_path[child] = v
#                 new_distance = distance + edge_to_distance[(v, child)]
#                 new_heuristic = new_distance + heuristic(child, end)
#                 heappush(fringe, (new_heuristic, child, new_distance))
#     return None


def convert_lat_long_to_canvas(x1, y1, x2, y2):
    y1, x1, y2, x2 = -12 * float(y1) + 800, 12 * float(x1) + 1600, -12 * float(y2) + 800, 12 * float(x2) + 1600
    return x1, y1, x2, y2

def djikstras(city1, city2, speed): #Color the final path a different color
    start, end = city_to_node[city1], city_to_node[city2]
    lbl.configure(text = "Not yet arrived.")
    closed = set()
    x = 0
    fringe = [(0, start, start)]
    while fringe:
        distance, v, path = heappop(fringe)
        if v == end:
            print("I'm done: Djikstra")
            lbl.configure(text = "Arrived!")
            string_to_path(path)
            return distance, path
        if v not in closed:
            closed.add(v)
            children = get_children(v)
            for child in children:
                y1, x1 = node_lat_long[v]
                y2, x2 = node_lat_long[child]
                x1, y1, x2, y2 = convert_lat_long_to_canvas(x1, y1, x2, y2)
                x = x + 1
                w.create_line(x1, y1, x2, y2, fill="#ff0000", tags='line')
                if x >= speed:
                    w.update()
                    x = 1

                new_distance = distance + edge_to_distance[(v, child)]
                heappush(fringe, (new_distance, child, path + " " + child))
    return None


def A_star(city1, city2, speed):  #Color the final path a different color
    start, end = city_to_node[city1], city_to_node[city2]
    lbl.configure(text = "Not yet arrived.")
    closed = set()
    x = 0
    fringe = [(0, start, 0, start)]
    while fringe:
        heur, v, distance, path = heappop(fringe)
        if v == end:
            print("I'm done!")
            lbl.configure(text = "Arrived!")
            string_to_path(path)
            return distance, path
        if v not in closed:
            closed.add(v)
            children = get_children(v)
            for child in children:
                y1, x1 = node_lat_long[v]
                y2, x2 = node_lat_long[child]
                x1, y1, x2, y2 = convert_lat_long_to_canvas(x1, y1, x2, y2)
                x = x + 1
                w.create_line(x1, y1, x2, y2, fill="#ff0000", tags='line')
                if x >= speed:
                    w.update()
                    x = 1
                new_distance = distance + edge_to_distance[(v, child)]
                new_heuristic = new_distance + heuristic(child, end)
                heappush(fringe, (new_heuristic, child, new_distance, path + " " + child))
    return None


def scuffed_A_star(city1, city2):  #Color the final path a different color
    start, end = city_to_node[city1], city_to_node[city2]
    lbl.configure(text = "Not yet arrived.")
    closed = set()
    fringe = [(0, start, 0, start)]
    while fringe:
        heur, v, distance, path = heappop(fringe)
        if v == end:
            print("I'm done!")
            lbl.configure(text = "Arrived!")
            string_to_path(path)
            return distance, path
        if v not in closed:
            closed.add(v)
            children = get_children(v)
            for child in children:
                new_distance = distance + edge_to_distance[(v, child)]
                new_heuristic = new_distance + heuristic(child, end)
                heappush(fringe, (new_heuristic, child, new_distance, path + " " + child))
    return None


def string_to_path(string):
    path = string.strip().split(' ')
    for x in range(0, len(path) - 1):
        start_node = path[x]
        end_node = path[x + 1]
        y1, x1 = node_lat_long[start_node]
        y2, x2 = node_lat_long[end_node]
        x1, y1, x2, y2 = convert_lat_long_to_canvas(x1, y1, x2, y2)
        w.create_line(x1, y1, x2, y2, fill="#1c1cf0", tags='line')
        w.update()


def dfs(city1, city2, speed): #fine as it is
    start, end = city_to_node[city1], city_to_node[city2]
    lbl.configure(text="Not yet arrived.")
    visited = set()
    x = 0
    fringe = deque()
    visited.add(start)
    fringe.append(start)
    while fringe:
        v = fringe.pop()
        if v == end:
            lbl.configure(text = "Arrived!")
            return "We did it!"
        children = get_children(v)
        for child in children:
            if child not in visited:
                y1, x1 = node_lat_long[v]
                y2, x2 = node_lat_long[child]
                x1, y1, x2, y2 = convert_lat_long_to_canvas(x1, y1, x2, y2)
                x = x + 1
                w.create_line(x1, y1, x2, y2, fill="#ff0000", tags='line')
                if x >= speed:
                    w.update()
                    x = 1
                fringe.append(child)
                visited.add(child)
    return None


def kDFS(city1, city2, k, speed, x):
    start, end = city_to_node[city1], city_to_node[city2]
    lbl.configure(text="Not yet arrived.")
    fringe = []
    fringe.append((start, 0, {start}))
    while fringe:
        state, distance, ancestors = fringe.pop()
        if state == end:
            lbl.configure(text="Arrived!")
            print(str(distance))
            return distance, x
        if distance < k:
            children = get_children(state)
            for child in children:
                if child not in ancestors:
                    y1, x1 = node_lat_long[state]
                    y2, x2 = node_lat_long[child]
                    x1, y1, x2, y2 = convert_lat_long_to_canvas(x1, y1, x2, y2)
                    x = x + 1
                    w.create_line(x1, y1, x2, y2, fill="#ff0000", tags='line')
                    if x >= speed:
                        w.update()
                        x = 1
                    fringe.append((child, distance + heuristic(state, child),ancestors.union([child])))
    return None, x


def id_dfs():
    k = 0
    tru, z = kDFS(cities1.get(), cities2.get(), k, speed = int(speeds.get()), x = 0)
    while tru is None:
        w.delete('line')
        tru, z = kDFS(cities1.get(), cities2.get(), k, int(speeds.get()), z)
        k = k + 100
    scuffed_A_star(cities1.get(), cities2.get())
    return tru

def A_star_command():
    A_star(cities1.get(), cities2.get(), speed = int(speeds.get()))

def djikstra_command():
    djikstras(cities1.get(), cities2.get(), speed = int(speeds.get()))

def dfs_command():
    dfs(cities1.get(), cities2.get(), speed = int(speeds.get()))


def test_tkinter():
    window = Tk()
    lbl = Label(window, text="Hello", font=("Arial Bold", 50))  # creating a label, setting the text, setting font size

    def clicked():
        res = "Welcome to " + txt.get()
        lbl.configure(text=res)

    btn = Button(window, text="Click Me", command=clicked, bg="orange", fg="red")
    btn.grid(column=1, row=0)  # Row column determines the placement on the grid
    window.geometry('1200x800')  # window size
    lbl.grid(column=0, row=0)
    txt = Entry(window, width=10)
    txt.grid(column=0, row=1)
    txt.focus()
    window.title("TrainRoutes")
    window.mainloop()

#print(str(id_dfstest()))


cities1 = Combobox(master)
cities1['values'] = tuple(city_to_node.keys())
cities2 = Combobox(master)
cities2['values'] = tuple(city_to_node.keys())
cities1.place(x=270, y=0)
cities2.place(x=450,y=0)
speeds = Combobox(master)
speeds['values'] = (1, 5, 10, 25, 50, 100, 200, 300, 400, 500, 1000, 2000, 3000, 4000, 5000, 10000, 20000, 50000, 100000, 200000, 300000, 1000000)
speeds.place(x=600,y=0)

lbl = Label(master, text="Not yet arrived.")
lbl.place(x = 750, y=0)
button_a_star = Button(master, text="A*", command = A_star_command)
button_djikstra = Button(master, text = 'Djikstra\'s', command = djikstra_command)
reset_button = Button(master, text = 'Reset', command = reset_command)
button_a_star.place(x = 0, y = 0)
button_djikstra.place(x=75, y=0)
reset_button.place(x = 150, y = 0)

button_dfs = Button(master, text = 'DFS', command = dfs_command)
button_dfs.place(x=0, y=30)

button_id_dfs = Button(master, text='ID-DFS', command = id_dfs)
button_id_dfs.place(x=75,y=30)

img = PhotoImage(file = 'map.png')
w.create_image(450, 300, image = img)

draw_coordinates()


#djikstras(sys.argv[1], sys.argv[2])
mainloop()

#A_star(sys.argv[1], sys.argv[2])

# This is for Train Routes Part 1
# print("Time to create data structure: " + str(time_to_make_data_structures))
# start = time.perf_counter()
# d, path = djikstras(sys.argv[1], sys.argv[2])
# end = time.perf_counter()
# print(sys.argv[1] + " to " + sys.argv[2] + " with Djikstra: " + str(d) + " in " + str(end - start) + " seconds.")
# start = time.perf_counter()
# d, temp = A_star(sys.argv[1], sys.argv[2])
# end = time.perf_counter()
# print(sys.argv[1] + " to " + sys.argv[2] + " with A*: " + str(d) + " in " + str(end - start) + " seconds.")
# #This is for purely testing purposes
# print(path)
# print(temp)
#
# arrDjikstra = path.split(' ')
# arrAstar = temp.split(' ')
#
# x = 0
# print(path == temp)
# print(arrAstar == arrDjikstra)
#
# for x in range(0, len(arrAstar)):
#    if arrAstar[x] != arrDjikstra[x]:
#       print(str(x))
#       print(arrDjikstra[x])
#       print(arrAstar[x])

