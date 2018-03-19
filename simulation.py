import simpy


class BusStop:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.waitingPeople = []

    def addPerson(self, person):
        self.waitingPeople.append(person)


    def takePassengers(self, bus):
        enteringPeople = [person for person in self.waitingPeople if person.wantsToEnter(bus)][:bus.freePlaces()]
        self.waitingPeople = [person for person in self.waitingPeople if not person in enteringPeople]

        return enteringPeople


class Person:
    def __init__(self, id, source, destination):
        self.id = id
        self.source = source
        self.destination = destination

    def enterBus(self, bus, busStop):
        print("{} entering bus {} at bus stop {}".format(self.id, bus.id, busStop.name))

    def leaveBus(self, bus, busStop):
        print("{} leaving bus {} at bus stop {}".format(self.id, bus.id, busStop.name))

    def wantsToEnter(self, bus):
        return True

    def wantsToLeave(self, busStop):
        return busStop is self.destination



class Bus:
    def __init__(self, id, capacity, route):
        self.id = id
        self.capacity = capacity
        self.route = route
        self.lastStopNumber = len(route) - 1

        self.passengers = []
        self.currentStop = 0
        self.currentDirection = 1

    def freePlaces(self):
        return self.capacity - len(self.passengers)

    def run(self, env):
        while True:
            # take people from current step
            enteringPeople = self.route[self.currentStop].takePassengers(self)
            for person in enteringPeople:
                person.enterBus(self, self.route[self.currentStop])
            self.passengers += enteringPeople

            # calculate move to next stop
            nextStop = self.currentStop + self.currentDirection

            # move
            print("Moving from {} to {} stop, free places {}".format(self.route[self.currentStop].name, self.route[nextStop].name, self.capacity - len(self.passengers)))
            yield env.timeout(3)
            self.currentStop = nextStop

            # leave people on current stop
            leavingPeople = [passenger for passenger in self.passengers if passenger.wantsToLeave(self.currentStop)]
            for person in leavingPeople:
                person.leaveBus(self, self.route[self.currentStop])
            self.passengers = [passenger for passenger in self.passengers if not passenger.wantsToLeave(self.currentStop)]

            # change direction if needed
            if self.currentStop == 0 or self.currentStop == self.lastStopNumber:
                self.currentDirection *= -1

busStop1 = BusStop(0, "AGH")
busStop2 = BusStop(1, "Czarnowiejska")

person1 = Person("Wojtek", busStop1.id, busStop2.id)
person2 = Person("Krzysiek", busStop2.id, busStop1.id)


busStop1.addPerson(person1)
busStop2.addPerson(person2)

route = [busStop1, busStop2]

env = simpy.Environment()
env.process(Bus("Happy bus", 10, route).run(env))

env.run(until=15)