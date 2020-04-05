"""
Crude simulation of a population, environment, and contagion.
The unit of population is an EpiHost, which has a state of unexposed, infected, or recovered.
If an infected host collides with an unexposed host, the unexposed host becomes infected.
If a host is recovered, it has no effect when colliding with any other host.
Infected hosts heal linearly with time.
After a constant time period, an infected host automatically becomes recovered.
Thus, all hosts survive in this simulation.

This simulation can be used to visualize the concept of "flattening the curve."
"""
import random
import sys
import pygame
from pygame import Color, Rect
from epidemiological_host import ContactResponse, make_hosts
from constants import InitialCondition, Disease, Screen, SimColor, PreventativeMeasure, HostConfig
from preventative_measures import PreventativeMeasures
from stats import EpidemicStats


def build_border():
    """
    Creates a Rect border around the Universe
    :return: Rect instance
    """
    return Rect(5, 5, Screen.WIDTH - 10, Screen.HEIGHT - 100)


class Universe(object):
    """
    Represents a 2-dimensional space and time containing a population of epidemiological hosts
    """

    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode(
            size=(Screen.WIDTH, Screen.HEIGHT),
            flags=0,
            depth=32,
        )

        self.hosts = make_hosts(
            unexposed=InitialCondition.POP_UNEXPOSED,
            infected=InitialCondition.POP_INFECTED
        )

        self.screen.fill(SimColor.DARK_GREY)
        self.border = build_border()
        self.clock = pygame.time.Clock()
        self.iteration = 0

        # Initialize stats instance
        self.stats = EpidemicStats(self)

        self.is_epidemic = True
        self.preventative_measures = None

    @property
    def total_population(self):
        return len(self.hosts)

    def calculate_state(self):
        """
        Increments the simulation state
        """
        if self.is_epidemic_over:
            return

        time_step = 1

        while time_step > ContactResponse.T_EPSILON:
            t_min = time_step
            t_min = self.detect_host_contacts(t_min)
            t_min = self.detect_border_contacts(t_min)

            for b in self.hosts:
                b.update(t_min)

            time_step -= t_min

    def detect_border_contacts(self, t_min):
        """
        Detects any EpiHost contact with space boundary of Universe
        :param t_min:
        :return:
        """
        for host in self.hosts:
            host.detect_boundary_contact(self.border, t_min)
            if host.contact_response.next_event_time < t_min:
                t_min = host.contact_response.next_event_time
        return t_min

    def detect_host_contacts(self, t_min):
        """
        Detects any contact between EpiHost instances
        :param t_min:
        :return:
        """
        for i in range(len(self.hosts)):
            for j in range(len(self.hosts)):
                if i < j:
                    self.hosts[i].detect_contact_with_other_host(self.hosts[j], t_min)

                if self.hosts[i].contact_response.next_event_time < t_min:
                    t_min = self.hosts[i].contact_response.next_event_time
        return t_min

    def draw(self):
        """
        Draws the Universe
        """
        pygame.draw.rect(self.screen, SimColor.LIGHT_GREY, self.border)
        for b in self.hosts:
            b.draw(self.screen)

    def run(self):
        """
        Runs the simulation
        """
        i = 0

        actions = [
            # PreventativeMeasure.LIMIT_TRAVEL,
            # PreventativeMeasure.VACCINATE_POP,
            PreventativeMeasure.SHELTER_IN_PLACE
        ]

        self.preventative_measures = PreventativeMeasures(
            self.hosts,
            actions,
            HostConfig.VACCINATION_DRIP,
            HostConfig.PREVENTATIVE_MEASURE_ADHERENCE
        )

        self.preventative_measures.enact()

        while not self.is_epidemic_over:
            self.calculate_state()
            self.draw()
            self.iteration += Screen.GRAPH_X_UNIT
            self.progress_healing()
            self.stats.update()

            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    self.quit()
            pygame.display.update()

        while self.is_epidemic_over:
            pygame.display.update()

    def progress_healing(self):
        """
        Decrements time units until fully recovered for all infected hosts,
        then sets Recovered state for hosts with no remaining recovery time units
        """
        for host in self.hosts:
            if host.vaccine:
                boost_recovery = 1 + random.randint(0, host.vaccine.drip_rate)
                print(boost_recovery)
                host.remaining_recovery -= boost_recovery

            if host.remaining_recovery <= 0:
                host.condition = Disease.RECOVERED

            if host.condition is Disease.INFECTED:
                host.remaining_recovery -= 1

            host.color = Disease.COLOR_MAP[host.condition]

    @staticmethod
    def quit():
        sys.exit()

    def get_population_count(self, target_condition) -> int:
        """
        Returns number of EpiHosts with provided `target_condition`
        :param target_condition: unexposed, infected, recovered state
        :return: int population size in provided `target_condition`
        """
        return len([host for host in self.hosts if host.condition is target_condition])

    def update_max_infected(self, infected_count):
        self.stats.max_infected = max(self.stats.max_infected, infected_count)
        self.stats.max_active_infected_percent = round((self.stats.max_infected / len(self.hosts)), 2) * 100

        current_infected = self.get_population_count(Disease.INFECTED)
        current_recovered = self.get_population_count(Disease.RECOVERED)

        self.stats.max_total_infected_percent = round((current_infected + current_recovered) / len(self.hosts), 2) * 100

    @property
    def is_epidemic_over(self):
        """
        Returns true if there are no infected hosts
        :return: Boolean
        """
        return self.get_population_count(Disease.INFECTED) is 0


if __name__ == "__main__":
    bw = Universe()
    bw.run()
