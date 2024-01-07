import math
import random


# this is to test git commit, pull, push, pull request, merge
# this is some updates mode from new branch test_git

from constants import PreventativeMeasure


class PreventativeMeasures:
    """
    Represents a set of strategies for minimizing scope of infection
    """

    def __init__(self, hosts, measures, vaccination_rate, percent):
        self.hosts = hosts
        self.measures = measures
        self.vaccination_rate = vaccination_rate
        self.percent = percent

        # some modifications of new code

    def enact(self):
        for measure in self.measures:
            if measure is PreventativeMeasure.SHELTER_IN_PLACE:
                self.shelter_in_place()
            if measure is PreventativeMeasure.LIMIT_TRAVEL:
                self.limit_travel()
            if measure is PreventativeMeasure.VACCINATE_POP:
                self.vaccinate_population()

    def get_random_sample(self):
        return random.sample(
            self.hosts,
            math.ceil(len(self.hosts) * self.percent)
        )

    def shelter_in_place(self):
        for host in self.get_random_sample():
            host.is_sheltering = True

    def limit_travel(self):
        for host in self.get_random_sample():
            host.limit_travel = True

    def vaccinate_population(self):
        for host in self.get_random_sample():
            host.vaccine = Vaccine(self.vaccination_rate)


class Vaccine:
    """
    Represents a vaccine that prevents the infection in a receiving host
    """

    def __init__(self, drip_rate):
        self.drip_rate = drip_rate
