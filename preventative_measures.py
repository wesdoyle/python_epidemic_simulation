import math
import random

from constants import PreventativeMeasure


class PreventativeMeasures:
    """
    Represents a set of strategies for minimizing the scope of infection.

    Attributes:
        hosts (list): A list of hosts that can be affected by the infection.
        measures (list): A list of preventative measures to be enacted.
        vaccination_rate (float): The effectiveness rate of the vaccine.
        percent (float): The percentage of the population to apply measures to.
    """

    def __init__(self, hosts, measures, vaccination_rate, percent):
        """
        Initializes the PreventativeMeasures class with hosts, measures, vaccination rate, and percentage.

        Args:
            hosts (list): The list of hosts.
            measures (list): The list of preventative measures.
            vaccination_rate (float): The effectiveness rate of the vaccine.
            percent (float): The percentage of the population to apply measures to.
        """
        self.hosts = hosts
        self.measures = measures
        self.vaccination_rate = vaccination_rate
        self.percent = percent

    def enact(self):
        """
        Enacts the preventative measures on the population.
        """
        for measure in self.measures:
            if measure is PreventativeMeasure.SHELTER_IN_PLACE:
                self.shelter_in_place()
            if measure is PreventativeMeasure.LIMIT_TRAVEL:
                self.limit_travel()
            if measure is PreventativeMeasure.VACCINATE_POP:
                self.vaccinate_population()

    def get_random_sample(self):
        """
        Gets a random sample of the population based on the specified percentage.

        Returns:
            list: A random sample of hosts.
        """
        return random.sample(
            self.hosts,
            math.ceil(len(self.hosts) * self.percent)
        )

    def shelter_in_place(self):
        """
        Applies the shelter-in-place measure to a random sample of the population.
        """
        for host in self.get_random_sample():
            host.is_sheltering = True

    def limit_travel(self):
        """
        Applies the limit travel measure to a random sample of the population.
        """
        for host in self.get_random_sample():
            host.limit_travel = True

    def vaccinate_population(self):
        """
        Vaccinates a random sample of the population.
        """
        for host in self.get_random_sample():
            host.vaccine = Vaccine(self.vaccination_rate)


class Vaccine:
    """
    Represents a vaccine that prevents the infection in a receiving host.

    Attributes:
        drip_rate (float): The effectiveness rate of the vaccine.
    """

    def __init__(self, drip_rate):
        """
        Initializes the Vaccine class with a drip rate.

        Args:
            drip_rate (float): The effectiveness rate of the vaccine.
        """
        self.drip_rate = drip_rate
