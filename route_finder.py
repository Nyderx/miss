import itertools

from simulation import Bus, BusStop


class RouteFinder:
    def __init__(self, buses):
        self.prepare_stop_buses_map(buses)
        self.prepare_connections(buses)



    def find_route(self, start, destination):
        route = self.find_buses(start, destination)
        route_plan = self.prepare_plan(start, destination, route)
        return route_plan

    def prepare_stop_buses_map(self, buses):
        self.stop_buses_map = {}

        for bus in buses:
            for stop in bus.route:
                if stop not in self.stop_buses_map:
                    self.stop_buses_map[stop] = []

                self.stop_buses_map[stop].append(bus)


    def prepare_connections(self, buses):
        self.connections = {}
        for bus in buses:
            if bus not in self.connections:
                self.connections[bus] = []

            for stop in bus.route:
                for crossing_bus in self.stop_buses_map[stop]:
                    if crossing_bus not in self.connections[bus]:
                      self.connections[bus] = self.connections[bus] + self.stop_buses_map[stop]

    def find_buses(self, start, destination):
        routes_to_process = [[bus] for bus in self.stop_buses_map[start]]

        while len(routes_to_process) > 0:
            route = routes_to_process.pop()
            last_connection = route[len(route) - 1]
            if destination in last_connection.route:
                return route
            else:
                routes_to_add = [route + [connection] for connection in self.connections[last_connection]]
                routes_to_process = routes_to_process + routes_to_add

    def prepare_plan(self, start, destination, route):
        possibilities = list(itertools.product([-1, 1], repeat=len(route)))
        
        for possibility in possibilities:
            plan = self.get_plan(start, destination, route, possibility)
            if len(plan) != 0:
                return plan

        print("no possibilities")

    def get_plan(self, start, destination, route, possibility):
        stops = []
        current_stop = start

        for i in range(0, len(route)):
            bus = route[i]
            direction = possibility[i]
            current_stop_id = bus.route.index(current_stop)

            next_stops = self.next_stops(bus, current_stop_id, direction)

            if i == len(route) - 1:
                stops.append(destination)
                if destination in next_stops:
                    stops.append(destination)
                    return stops
                else:
                    return []
            else:
                found = False
                for stop in next_stops:
                    if route[i+1] in self.stop_buses_map[stop]:
                        stops.append(stop)
                        current_stop = stop
                        found = True
                        continue
                if not found:
                    return []

    def next_stops(self, bus, current_stop_id, direction):
        if direction == 1:
            return bus.route[current_stop_id:]
        else:
            return bus.route[0: current_stop_id + 1]

#