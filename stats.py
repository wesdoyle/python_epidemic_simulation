import pygame
from pygame.rect import Rect

from constants import InitialCondition, Screen, Disease, SimColor

# new comment line added
class EpidemicStats:
    """
    Provides statistics and visualization about current state
    """

    def __init__(self, universe):
        self.universe = universe

        # Initialize counts
        self.max_active_infected_percent = round((InitialCondition.POP_INFECTED / len(self.universe.hosts)), 2) * 100
        self.max_total_infected_percent = self.max_active_infected_percent
        self.max_infected = InitialCondition.POP_INFECTED
        self.medical_limit = Screen.MEDICAL_LIMIT

    def update(self):
        """
        Updates the graph visualization
        """
        legend = Rect(10, 10, 180, 110)
        font = pygame.font.SysFont(pygame.font.get_default_font(), Screen.FONT_SIZE)

        pygame.draw.rect(self.universe.screen, SimColor.LIGHT_GREY, legend)
        infected_count = self.universe.get_population_count(Disease.INFECTED)
        recovered_count = self.universe.get_population_count(Disease.RECOVERED)
        unexposed_count = self.universe.get_population_count(Disease.UNEXPOSED)

        self.universe.update_max_infected(infected_count)
        rect_infected = Rect(self.universe.iteration + 5, Screen.HEIGHT - 10, 5, -infected_count)
        pygame.draw.rect(self.universe.screen, SimColor.INFECTED, rect_infected)

        unexposed_label = font.render(f"Unexposed: {unexposed_count:6}", 1, SimColor.UNEXPOSED)
        self.universe.screen.blit(unexposed_label, (20, 20))

        infected_label = font.render(f"Infected: {infected_count:12}", 1, SimColor.INFECTED)
        self.universe.screen.blit(infected_label, (20, 40))

        recovered_label = font.render(f"Recovered: {recovered_count:7}", 1, SimColor.RECOVERED)
        self.universe.screen.blit(recovered_label, (20, 60))

        max_infected_label = font.render(
            f"Max Active Infected: {round(self.max_active_infected_percent, 2):5}%", 1, SimColor.BLACK)
        self.universe.screen.blit(max_infected_label, (20, 80))

        max_infected_label = font.render(
            f"Max Total Infected: {round(self.max_total_infected_percent, 2):5}%", 1, SimColor.BLACK)
        self.universe.screen.blit(max_infected_label, (20, 100))

        pygame.draw.rect(self.universe.screen, SimColor.LIMIT_LINE, (0, Screen.HEIGHT - Screen.MEDICAL_LIMIT, Screen.WIDTH, 1), 2)