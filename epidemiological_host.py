import math
import random
from math import sin, cos, atan2, fabs

import pygame

from constants import Disease, Screen, HostConfig, SimColor


class EpiHost:
    """
    Host that can carry and transmit a pathogen.
    Has simple mechanical properties and a health condition
    """

    def _set_speed(self, speed, angle):
        self.speed = speed
        self.angle = angle
        self.speed_x = cos(math.radians(self.angle)) * self.speed
        self.speed_y = sin(math.radians(self.angle)) * self.speed

    def __init__(self, state):
        self.name = state.get('name')
        self.color = state.get('color')

        self.condition = state.get('condition')
        self.remaining_recovery = Disease.DEFAULT_RECOVERY_PERIOD

        self.x = state.get('x')
        self.y = state.get('y')
        self.r = state.get('r')
        self.speed_x = 0
        self.speed_y = 0
        self._set_speed(state.get('speed'), state.get('angle'))

        self.contact_response = ContactResponse()
        self.contact_response.new_speed_x = 0
        self.contact_response.new_speed_y = 0

        self.vaccine = None
        self.is_sheltering = False
        self.limit_travel = False

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.r)

        if self.vaccine:
            pygame.draw.circle(screen, SimColor.RECOVERED, (int(self.x), int(self.y)), 0.5 * self.r)

    def update(self, time):
        if self.is_sheltering:
            self.x = self.x
            self.y = self.y
            self.speed_x = 0
            self.speed_y = 0

        if self.contact_response.next_event_time < time \
                or fabs(self.contact_response.next_event_time - time) < ContactResponse.T_EPSILON:

            self.x = self.contact_response.update_x(self.speed_x, self.x)
            self.y = self.contact_response.update_y(self.speed_y, self.y)

            self.speed_x = self.contact_response.new_speed_x
            self.speed_y = self.contact_response.new_speed_y

        else:

            if not self.limit_travel:
                self.x = self.speed_x * time + self.x
                self.y = self.speed_y * time + self.y
            else:
                self.x = 0.3 * self.speed_x * time + self.x
                self.y = 0.3 * self.speed_y * time + self.y

        self.contact_response.reset()

    def detect_contact_with_other_host(self, other, time_step):
        # relative position:
        contact_response = self.contact_time_with_other_host(other)

        if contact_response.next_event_time - ContactResponse.T_EPSILON > time_step:
            return
        self.transmit_pathogen(other)
        self.contact_response.next_event_time = contact_response.next_event_time
        other.contact_response.next_event_time = contact_response.next_event_time

        contact_point_x = self.contact_response.get_exact_new_x(self.speed_x, self.x)
        contact_point_y = self.contact_response.get_exact_new_y(self.speed_y, self.y)

        other_contact_point_x = other.contact_response.update_x(other.speed_x, other.x)
        other_contact_point_y = other.contact_response.update_y(other.speed_y, other.y)

        theta = atan2(
            other_contact_point_y - contact_point_y,
            other_contact_point_x - contact_point_x
        )

        speed_p = self.speed_x * cos(theta) + self.speed_y * sin(theta)
        speed_q = -self.speed_x * sin(theta) + self.speed_y * cos(theta)

        other_speed_p = other.speed_x * cos(theta) + other.speed_y * sin(theta)
        other_speed_q = -other.speed_x * sin(theta) + other.speed_y * cos(theta)

        self.contact_response.new_speed_x = other_speed_p * cos(-theta) + speed_q * sin(-theta)
        self.contact_response.new_speed_y = -other_speed_p * sin(-theta) + speed_q * cos(-theta)

        other.contact_response.new_speed_x = speed_p * cos(-theta) + other_speed_q * sin(-theta)
        other.contact_response.new_speed_y = -speed_p * sin(-theta) + other_speed_q * cos(-theta)

    def transmit_pathogen(self, interlocutor):
        if interlocutor.condition is Disease.INFECTED \
                and self.condition is not Disease.RECOVERED:
            self.condition = Disease.INFECTED
            self.color = Disease.COLOR_MAP[self.condition]
        if self.condition is Disease.INFECTED \
                and interlocutor.condition is not Disease.RECOVERED:
            interlocutor.condition = Disease.INFECTED
            interlocutor.color = Disease.COLOR_MAP[interlocutor.condition]

    def contact_time_with_other_host(self, interlocutor):

        x = self.x - interlocutor.x
        y = self.y - interlocutor.y
        r = self.r + interlocutor.r

        # relative speed between hosts
        speed_x = self.speed_x - interlocutor.speed_x
        speed_y = self.speed_y - interlocutor.speed_y

        a = speed_x ** 2 + speed_y ** 2
        b = (x * speed_x + y * speed_y) * 2
        c = x ** 2 + y ** 2 - r ** 2
        delta = b ** 2 - 4 * a * c

        response = ContactResponse()

        if a == 0:
            if b != 0:
                t = -c / b
                if t > 0:
                    response.next_event_time = t
                    return response
            else:
                return response

        elif delta < 0:
            return response

        else:
            t1 = (-b - math.sqrt(delta)) / (2 * a)
            t2 = (-b + math.sqrt(delta)) / (2 * a)

            if t1 > 0:
                response.next_event_time = t1

            elif t2 > 0:
                response.next_event_time = t2

            return response

    def detect_boundary_contact(self, bounds, time_step):
        """
        Detects contact with one of four sides of Universe boundary
        :param bounds:
        :param time_step:
        :return:
        """
        contactable = self.detect_contact_vertical_bounds(bounds.x, time_step)
        if contactable.next_event_time < self.contact_response.next_event_time:
            self.contact_response = contactable

        contactable = self.detect_contact_vertical_bounds(bounds.x + bounds.width, time_step)
        if contactable.next_event_time < self.contact_response.next_event_time:
            self.contact_response = contactable

        contactable = self.detect_contact_horizontal_bounds(bounds.y, time_step)
        if contactable.next_event_time < self.contact_response.next_event_time:
            self.contact_response = contactable

        contactable = self.detect_contact_horizontal_bounds(bounds.y + bounds.height, time_step)
        if contactable.next_event_time < self.contact_response.next_event_time:
            self.contact_response = contactable

    def detect_contact_vertical_bounds(self, x, time_step):
        """
        Handle contact with vertical boundaries
        :param x:
        :param time_step:
        :return:
        """
        if self.speed_x == 0:
            return ContactResponse()
        if x > self.x:
            distance = x - self.x - self.r
        else:
            distance = x - self.x + self.r
        time = distance / self.speed_x
        if time > 0 and (time < time_step or math.fabs(time - time_step) < ContactResponse.T_EPSILON):
            response = ContactResponse(time)
            response.next_event_time = time
            response.new_speed_x = -self.speed_x
            response.new_speed_y = self.speed_y
            return response
        else:
            return ContactResponse()

    def has_time_within_step_period(self, time, time_step):
        pass

    def detect_contact_horizontal_bounds(self, y, time_step):
        """
        Handle contact with horizontal boundaries
        :param y:
        :param time_step:
        :return:
        """
        if self.speed_y == 0:
            return ContactResponse()
        if y > self.y:
            distance = y - self.y - self.r
        else:
            distance = y - self.y + self.r
        time = distance / self.speed_y
        if time > 0 and (time < time_step or math.fabs(time - time_step) < ContactResponse.T_EPSILON):
            response = ContactResponse(time)
            response.new_speed_x = self.speed_x
            response.new_speed_y = -self.speed_y
            response.next_event_time = time
            return response
        else:
            return ContactResponse()


class ContactResponse(object):
    """
    Provides data about an incoming contact event
    """

    T_EPSILON = 0.01

    def __init__(self, next_event_time=float('inf')):
        self.next_event_time = next_event_time

    def update_x(self, curr_speed_x, curr_x):
        if self.next_event_time > self.T_EPSILON:
            return curr_x + curr_speed_x * (self.next_event_time - self.T_EPSILON)
        return curr_x

    def update_y(self, curr_speed_y, curr_y):
        if self.next_event_time > self.T_EPSILON:
            return curr_y + curr_speed_y * (self.next_event_time - self.T_EPSILON)
        return curr_y

    def get_exact_new_x(self, curr_speed_x, curr_x):
        return curr_x + curr_speed_x * self.next_event_time

    def get_exact_new_y(self, curr_speed_y, curr_y):
        return curr_y + curr_speed_y * self.next_event_time

    def reset(self):
        self.next_event_time = float('inf')


def build_host(condition, i):
    """
    EpiHost factory
    :param condition: unexposed, infected, recovered epidemiological state
    :param i: iterator
    :return: new EpiHost instance
    """
    state = {
        'condition': condition,
        'x': random.randint(HostConfig.SIZE + 12, Screen.WIDTH - HostConfig.SIZE - 12),
        'y': random.randint(HostConfig.SIZE + 12, Screen.HEIGHT - 100 - HostConfig.SIZE - 12),
        'speed': random.randint(HostConfig.MIN_SPEED, HostConfig.MAX_SPEED),
        'angle': random.randint(0, 359),
        'r': HostConfig.SIZE / 2.,
        'name': str(i),
        'color': Disease.COLOR_MAP[condition],
    }

    return EpiHost(state)


def make_hosts(unexposed: int, infected: int) -> list:
    """
    Makes a number of unexposed and infected hosts
    :param unexposed: int number of unexposed EpiHosts
    :param infected: int number of infected EpiHosts
    :return: list EpiHost instances
    
    """
    unexposed = [build_host(Disease.UNEXPOSED, i) for i in range(unexposed)]
    infected = [build_host(Disease.INFECTED, i) for i in range(infected)]
    return unexposed + infected
