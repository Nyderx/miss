import simpy

from utils import *
from random import randint

class BusStop:
    def __init__(self, id, name, x, y):
        self.id = id
        self.name = name
        self.x = x
        self.y = y
        self.waiting_people = []

        self.routes = []

    def set_routes(self, routes):
        self.routes = routes

    def add_person(self, person):
        self.waiting_people.append(person)


    def take_passengers(self, bus):
        entering_people = [person for person in self.waiting_people if person.wants_to_enter(bus)][:bus.free_places()]
        self.waiting_people = [person for person in self.waiting_people if not person in entering_people]

        return entering_people


class Person:
    def __init__(self, id, source, destination):
        self.id = id
        self.source = source
        self.destination = destination

        self.exit_stop = destination

    def enter_bus(self, bus, busStop):
        print("{} entering bus {} at bus stop {}".format(self.id, bus.id, busStop.name))

    def leave_bus(self, bus, busStop):
        print("{} leaving bus {} at bus stop {}".format(self.id, bus.id, busStop.name))

    def wants_to_enter(self, bus):
        if self.destination in bus.next_stops():
            return True

        for stop in bus.next_stops():
            for route in stop.routes:
                if self.destination in route:
                    self.exit_stop = stop
                    return True
        return False

    def wants_to_leave(self, busStop):
        print("stop " + str(busStop))
        print(self.exit_stop)
        return busStop is self.exit_stop


# route_times format - [time_of_staying_on_first_stop, time between 0 and 1 stop, ..., time_of_staying_on_last_stop]
class Bus:
    def __init__(self, id, capacity, route, route_times):
        self.id = id
        self.capacity = capacity
        self.route = route
        self.route_times = route_times

        self.x = self.route[0].x + STOP_WIDTH / 2 - BUS_WIDTH / 2
        self.y = self.route[0].y - BUS_HEIGHT

        self.last_stop_number = len(route) - 1

        self.passengers = []
        self.current_stop = 0
        self.current_direction = 1

    def free_places(self):
        return self.capacity - len(self.passengers)

    def next_stops(self):
        if self.current_direction > 0:
            return self.route[self.current_stop:]
        else:
            return self.route[0:self.current_stop]

    def __current_stop(self):
        return self.route[self.current_stop]

    def run(self, env):
        while True:
            # leave people on current stop
            leaving_people = [passenger for passenger in self.passengers if passenger.wants_to_leave(self.__current_stop())]
            for person in leaving_people:
                person.leave_bus(self, self.__current_stop())
            self.passengers = [passenger for passenger in self.passengers if not passenger.wants_to_leave(self.__current_stop())]
            yield env.timeout(1 * FACTOR)

            # if its 0 or last stop - wait for a while
            if self.current_stop == 0:
                yield env.timeout(self.route_times[0] * FACTOR)
            elif self.current_stop == self.last_stop_number:
                yield env.timeout(self.route_times[len(self.route_times) - 1] * FACTOR)

            # take people from current step
            entering_people = self.route[self.current_stop].take_passengers(self)
            for person in entering_people:
                person.enter_bus(self, self.route[self.current_stop])
            self.passengers += entering_people
            yield env.timeout(1 * FACTOR)

            # calculate move to next stop
            next_stop = self.current_stop + self.current_direction

            #move to start of road
            self.x = self.route[self.current_stop].x + STOP_WIDTH/2
            self.y = self.route[self.current_stop].y + STOP_HEIGHT/2

            # move
            print("Moving from {} to {} stop, free places {}".format(self.route[self.current_stop].name, self.route[next_stop].name, self.capacity - len(self.passengers)))
            time = self.route_times[max(next_stop, self.current_stop)]
            next_stop_object = self.route[next_stop]
            current_stop_object = self.route[self.current_stop]
            dx = (next_stop_object.x - current_stop_object.x)/time
            dy = (next_stop_object.y - current_stop_object.y)/time
            for i in range(time):
                self.x = self.x + dx
                self.y = self.y + dy
                yield env.timeout(1)

            self.x = next_stop_object.x + STOP_WIDTH/2 - BUS_WIDTH/2
            self.y = next_stop_object.y - BUS_HEIGHT
            self.current_stop = next_stop


            # change direction if needed
            if self.current_stop == 0 or self.current_stop == self.last_stop_number:
                self.current_direction *= -1
            yield env.timeout(1)

class PeopleSpawner():
    def __init__(self, stops, spawning_functions):
        self.stops = stops
        self.spawning_functions = spawning_functions

    def run(self, env):
        while True:
            for stop in self.stops:
                if(self.spawning_functions[stop](env.now)):
                    start_stop = stop
                    last_stop = stop
                    while last_stop is stop:
                        last_stop = self.stops[randint(0, len(self.stops) - 1)]

                    person = Person("name", start_stop, last_stop)
                    start_stop.add_person(person)
                yield env.timeout(1 * FACTOR)



def run_simulation(buses, routes, spawning_functions):
    env = simpy.rt.RealtimeEnvironment(factor=1/FACTOR)

    stops = []
    for route in routes:
        for stop in route:
            stops.append(stop)
    spawner = PeopleSpawner(stops, spawning_functions)

    for bus in buses:
        env.process(bus.run(env))

    env.process(spawner.run(env))
    env.run(1000)
