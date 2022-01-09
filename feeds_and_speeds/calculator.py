from dataclasses import dataclass
from enum import Enum
from math import sqrt


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


@dataclass
class Router:
    input_voltage: float
    input_current: float
    efficiency: float
    rated_speed: float

    @property
    def input_power(self) -> float:
        return self.input_voltage * self.input_current


@dataclass
class Machine:
    maximum_machine_force: float
    router: Router


def get_adjusted_chipload(cutter_diameter: float, woc: float, chipload: float) -> float:
    if woc > cutter_diameter / 2:
        return chipload
    else:
        return (cutter_diameter * chipload) / (2.0 * sqrt((cutter_diameter * woc) - pow(woc, 2)))


router = Router(input_voltage=120., input_current=6.5, efficiency=0.6, rated_speed=30000.)
machine = Machine(maximum_machine_force=18., router=router)

cutter = Cutter(
    material=CutterMaterial.carbide,
    diameter=0.25,
    length=0.75,
    flutes=3,
    shank_diameter=0.25,
    overall_stickout=1)

chipload: float = 0.002
woc: float = 0.1875
doc: float = 0.0750

k_factor = 10.
rpm = 18000.


def get_feedrate(flutes: int, rpm: float, adjusted_chipload: float) -> float:
    return float(flutes) * rpm * adjusted_chipload


adjusted_chipload = get_adjusted_chipload(cutter_diameter=cutter.diameter, woc=woc, chipload=chipload)
print("{0:0.5f}".format(adjusted_chipload))
print("{0:0.0f}".format(get_feedrate(flutes=cutter.flutes, rpm=rpm, adjusted_chipload=adjusted_chipload)))

