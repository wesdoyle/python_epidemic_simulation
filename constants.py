"""
Simulation Constants
"""

"""
just for fun
"""
class SimColor:
"""
Tuples corresponding to RGB colors
"""
    LIGHT_GREY = (240, 240, 240)
    DARK_GREY = (30, 30, 50)
    BLACK = (0, 0, 0)
    LIMIT_LINE = (80, 80, 100)
    INFECTED = (210, 100, 140)
    RECOVERED = (0, 160, 0)
    UNEXPOSED = (0, 120, 240)


class Disease:
"""
Constants for disease
"""
    INFECTED = 0
    RECOVERED = 1
    UNEXPOSED = 2

    DEFAULT_RECOVERY_PERIOD = 340

    COLOR_MAP = {
        INFECTED: SimColor.INFECTED,
        RECOVERED: SimColor.RECOVERED,
        UNEXPOSED: SimColor.UNEXPOSED
    }


class Screen:
"""
Constants for Screen
"""
    WIDTH = 680
    HEIGHT = 480
    FONT_SIZE = 18
    GRAPH_X_UNIT = 0.8
    MEDICAL_LIMIT = 50

"""
Class for initial condition of Patient
"""
class InitialCondition:
    POP_UNEXPOSED = 49
    POP_INFECTED = 1


class HostConfig:
    SIZE = 11
    VACCINATION_DRIP = 3
    PREVENTATIVE_MEASURE_ADHERENCE = 0.5
    MAX_SPEED = 6
    MIN_SPEED = 2


class PreventativeMeasure:
    SHELTER_IN_PLACE = 0
    VACCINATE_POP = 1
    LIMIT_TRAVEL = 2

    SELECTED = [
        LIMIT_TRAVEL,
        VACCINATE_POP,
        SHELTER_IN_PLACE
    ]
