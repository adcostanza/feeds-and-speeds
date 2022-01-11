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
                    pow(cutter.length, 3) / (
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


if __name__ == "__main__":
    router = Router(input_voltage=120., input_current=6.5, efficiency=0.6, rated_speed=30000.)
    machine = Machine(maximum_machine_force=18., router=router)

    cutter = Cutter(
        material=CutterMaterial.carbide,
        diameter=0.25,
        length=0.75,
        flutes=3,
        shank_diameter=0.5,
        overall_stickout=1,
        maximum_deflection=0.0010)

    calculator = FeedsAndSpeedsCalculator(machine=machine,
                                          cutter=cutter,
                                          chipload=0.002,
                                          woc=0.1875,
                                          doc=0.0750,
                                          rpm=18000.,
                                          k_factor=10.,
                                          max_acceptable_deflection=0.0010)

    docs = np.linspace(0.001, 3. * .25, 100)
    wocs = np.linspace(0.05 * 0.25, .25, 100)

    combinations: List[Tuple[float, float]] = []
    for doc in docs:
        for woc in wocs:
            combinations.append((doc, woc))

    print(combinations)


    def calculator_with_doc_woc(calculator: FeedsAndSpeedsCalculator, doc: float,
                                woc: float) -> FeedsAndSpeedsCalculator:
        calculator_copy = copy.deepcopy(calculator)
        calculator_copy.doc = doc
        calculator_copy.woc = woc
        return calculator_copy


    calculators = [calculator_with_doc_woc(calculator, doc, woc) for doc, woc in combinations]
    acceptable_machine_force_calculators = [c for c in calculators if .18 < c.machine_force_percent < .20]
    print(acceptable_machine_force_calculators)
    print([(c.woc, c.doc) for c in acceptable_machine_force_calculators])
    # percent_of_max_machine_forces = [doc_dependent_calculation(doc).machine_force_percent for doc in docs]
    #
    # print(docs)
    # print(percent_of_max_machine_forces)
    #
    # plt.plot(docs, percent_of_max_machine_forces, 'o', color='black');
