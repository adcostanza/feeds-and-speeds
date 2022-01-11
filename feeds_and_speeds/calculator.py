import copy
import itertools
import pprint
from dataclasses import dataclass
from enum import Enum
from math import sqrt, pi
from typing import Tuple, List

import numpy as np
from matplotlib import pyplot as plt


class CutterMaterial(str, Enum):
    carbide = 'carbide'
    hss = 'hss'
    cobalt = 'cobalt'


@dataclass
class Cutter:
    material: CutterMaterial
    diameter: float
    length: float
    flutes: int
    shank_diameter: float
    overall_stickout: float
    maximum_deflection: float

    @property
    def youngs_modulus(self) -> float:
        if self.material == CutterMaterial.carbide:
            return 87000000.
        elif self.material == CutterMaterial.hss:
            return 30000000.
        else:
            return 30000000.

    def __str__(self):
        return f"""
        material = {self.material}
        diameter = {self.diameter}
        length = {self.length}
        flutes = {self.flutes}
        shank_diameter = {self.shank_diameter}
        overall_stickout = {self.overall_stickout}
        maximum_deflection = {self.maximum_deflection}
        youngs_modulus = {self.youngs_modulus}
        """


@dataclass
class Router:
    input_voltage: float
    input_current: float
    efficiency: float
    rated_speed: float

    @property
    def input_power(self) -> float:
        return self.input_voltage * self.input_current

    @property
    def output_power(self) -> float:
        return self.input_power * self.efficiency / 745.7

    def __str__(self):
        return f"""
        input_voltage = {self.input_voltage}
        input_current = {self.input_current}
        efficiency = {self.efficiency}
        rated_speed = {self.rated_speed}"""


@dataclass
class Machine:
    maximum_machine_force: float
    router: Router

    def __str__(self):
        return f"""
        maximum_machine_force = {self.maximum_machine_force}
        {self.router}"""


@dataclass
class FeedsAndSpeedsCalculator:
    machine: Machine
    cutter: Cutter

    chipload: float
    woc: float
    doc: float
    rpm: float
    k_factor: float
    max_acceptable_deflection: float

    pp = pprint.PrettyPrinter(indent=4)

    def print_inputs(self):
        print(self.machine)
        print(self.cutter)

    def print_feeds_and_speeds(self):
        print(f"""
        (Imperial)
        doc = {self.doc} in
        woc = {self.woc} in
        feedrate = {self.feedrate} in/min
        mrr = {self.material_removal_rate} in^3/min
        
        (Metric)
        doc = {self.doc * 25.4} mm
        woc = {self.woc * 25.4} mm
        feedrate = {self.feedrate * 25.4} mm/min
        mrr = {self.material_removal_rate * pow(25.4, 3)} mm^3/min
        """)

    def print_outputs(self):
        print("hi")

    # print("{0:0.5f}".format(adjusted_chipload))
    # print("{0:0.0f}".format(feedrate))
    # print("{0:0.2f}".format(mrr))
    # print("{0:0.3f}".format(power_usage))
    # print("{0:0.2f}".format(torque))
    # print("{0:0.2f}".format(machine_force))
    # print("{0:0.0f}%".format(machine_force_percent * 100))
    # print("{0:0.0f}%".format(available_power_percent * 100))
    #
    # print("{0:0.1f}".format(router_cutting_power_increase))
    #
    # print("{0:0.2f}%".format(max_deflection_percent * 100))

    @property
    def adjusted_chipload(self) -> float:
        if self.woc > self.cutter.diameter / 2:
            return self.chipload
        else:
            return (self.cutter.diameter * self.chipload) / (
                    2.0 * sqrt((self.cutter.diameter * self.woc) - pow(self.woc, 2)))

    @property
    def feedrate(self) -> float:
        return float(self.cutter.flutes) * self.rpm * self.adjusted_chipload

    @property
    def material_removal_rate(self) -> float:
        return self.feedrate * self.doc * self.woc

    @property
    def power_usage(self) -> float:
        return self.material_removal_rate / self.k_factor

    @property
    def torque(self) -> float:
        return self.power_usage * 63024. / self.rpm

    @property
    def machine_force(self) -> float:
        return self.torque / (self.cutter.diameter / 2)

    @property
    def machine_force_percent(self) -> float:
        return self.machine_force / self.machine.maximum_machine_force

    @property
    def available_power_percent(self) -> float:
        return self.power_usage / self.machine.router.output_power

    @property
    def router_cutter_power_increase(self) -> float:
        return self.power_usage * 745.7

    @property
    def max_deflection(self) -> float:
        if self.cutter.diameter < self.cutter.shank_diameter:
            return self.machine_force * (
                    pow(self.cutter.length, 3) / (
                    3 * self.cutter.youngs_modulus * (pi * pow(self.cutter.diameter / 2, 4) / 4)) + pow(
                self.cutter.overall_stickout - self.cutter.length, 3) / (
                            3 * self.cutter.youngs_modulus * (pi * pow(self.cutter.shank_diameter / 2, 4) / 4)))
        elif self.cutter.diameter == self.cutter.shank_diameter:
            return self.machine_force * pow(self.cutter.overall_stickout, 3) / (
                    3 * self.cutter.youngs_modulus * (pi * pow(self.cutter.diameter / 2, 4) / 4))
        else:
            return self.machine_force * pow(self.cutter.overall_stickout, 3) / (
                    3 * self.cutter.youngs_modulus * pi * pow(cutter.shank_diameter / 2, 4) / 4)

    @property
    def max_deflection_percent(self):
        return self.max_deflection / self.max_acceptable_deflection
