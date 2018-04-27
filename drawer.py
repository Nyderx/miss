from threading import Thread
from tkinter import *
from utils import *
from spawning_functions import *

import simulation
from simulation import BusStop, Bus

class Drawer():
    def __init__(self, routes, buses):
        self.routes = routes
        self.buses = buses
        self.window = Tk()
        self.window.title("Public transport simulation")
        self.window.geometry('800x600')
        self.canvas = None

        self.stop_labels = {}
        self.bus_labels = {}
        self.bus_rectangles = {}


    def draw(self):
        self.canvas = Canvas(self.window, width=800, height=600)

        self.draw_routes()
        self.draw_buses()

        self.canvas.pack()

        self.canvas.delete()

        self.canvas.after(int(1000/FACTOR), self.redraw)

    def redraw(self):
        for stop, label in self.stop_labels.items():
            self.canvas.itemconfig(label, text=str(len(stop.waiting_people)))

        for bus, label in self.bus_labels.items():
            self.canvas.itemconfig(label, text=str(len(bus.passengers)))
            old_x, old_y = self.canvas.coords(label)
            self.canvas.move(label, bus.x + BUS_WIDTH/2 - old_x, bus.y + FONT_SIZE/2 + 1 - old_y)


        for bus, rectangle in self.bus_rectangles.items():
            old_x, old_y, _, _ = self.canvas.coords(rectangle)
            self.canvas.move(rectangle, bus.x - old_x, bus.y - old_y)



        self.canvas.after(int(1000/FACTOR), self.redraw)


    def draw_routes(self):
        for route in self.routes:
            last_stop_x = route[0].x
            last_stop_y = route[0].y

            for stop in route[1:]:
                self.canvas.create_line(last_stop_x+STOP_WIDTH/2, last_stop_y+STOP_HEIGHT/2, stop.x+STOP_WIDTH/2, stop.y+STOP_HEIGHT/2, fill='blue')
                last_stop_x = stop.x
                last_stop_y = stop.y

            for stop in route:
                self.draw_bus_stop(self.canvas, stop)

    def draw_buses(self):
        for bus in self.buses:
            self.draw_bus(self.canvas, bus)

    def draw_bus(self, window, bus):
        x = bus.x
        y = bus.y

        rectangle_id = self.canvas.create_rectangle(x, y, x + BUS_WIDTH, y + BUS_HEIGHT, fill='white')
        text_id = self.canvas.create_text(x + BUS_WIDTH/2, y + FONT_SIZE/2 + 1, text=str(len(bus.passengers)), font = ('Times New Roman', FONT_SIZE), width=BUS_WIDTH)

        self.bus_labels[bus] = text_id
        self.bus_rectangles[bus] = rectangle_id


    def draw_bus_stop(self, window, stop):
        x = stop.x
        y = stop.y
        self.canvas.create_rectangle(x, y, x + STOP_WIDTH, y + STOP_HEIGHT, fill='grey')

        self.canvas.create_text(x + STOP_WIDTH/2, y + FONT_SIZE/2 + 1, text=stop.name, font = ('Times New Roman', FONT_SIZE), width=STOP_WIDTH)

        self.canvas.create_line(x, y + STOP_HEIGHT/2, x + STOP_WIDTH, y + STOP_HEIGHT/2)

        text_id = self.canvas.create_text(x + STOP_WIDTH/2, y + FONT_SIZE/2 + 1 + STOP_HEIGHT/2, text=str(len(stop.waiting_people)), font = ('Times New Roman', FONT_SIZE), width=STOP_WIDTH)

        self.stop_labels[stop] = text_id

bus_stop1 = BusStop(0, "AGH", 10, 20)
bus_stop2 = BusStop(0, "Czarnowiejsk", 200, 50)
bus_stop3 = BusStop(0, "Kawiory", 500, 500)

bus_stop4 = BusStop(0, "Piaski", 400, 50)
bus_stop5 = BusStop(0, "Bieżanowska", 400, 500)

stops = [bus_stop1, bus_stop2, bus_stop3, bus_stop4, bus_stop5]

spawning_func= {}
spawning_func[bus_stop1] = standard_center_function
spawning_func[bus_stop2] = standard_center_function
spawning_func[bus_stop3] = standard_center_function
spawning_func[bus_stop4] = standard_suburbs_function
spawning_func[bus_stop5] = standard_suburbs_function

route1 = (bus_stop1, bus_stop2, bus_stop3)
route2 = (bus_stop4, bus_stop2, bus_stop5)

routes = [route1, route2]

for stop in stops:
    stop.set_routes(routes)

bus1 = Bus("Happy bus", 10, route1, [1, 10, 15, 2])
bus2 = Bus("Unhappy bus", 10, route2, [1, 10, 2])


Thread(target = simulation.run_simulation, args=([bus1, bus2], routes, spawning_func)).start()

print("drawering")
drawer = Drawer([route1, route2], [bus1, bus2])
drawer.draw()
drawer.window.mainloop()



