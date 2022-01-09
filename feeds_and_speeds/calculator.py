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
    maximum_deflection: float


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
    overall_stickout=1,
    maximum_deflection=0.0010)

chipload: float = 0.002
woc: float = 0.1875
doc: float = 0.0750

k_factor = 10.
rpm = 18000.


def get_feedrate(flutes: int, rpm: float, adjusted_chipload: float) -> float:
    return float(flutes) * rpm * adjusted_chipload


adjusted_chipload = get_adjusted_chipload(cutter_diameter=cutter.diameter, woc=woc, chipload=chipload)
feedrate = get_feedrate(flutes=cutter.flutes, rpm=rpm, adjusted_chipload=adjusted_chipload)


def get_mrr(feedrate: float, doc: float, woc: float) -> float:
    return feedrate * doc * woc


mrr = get_mrr(feedrate=feedrate, doc=doc, woc=woc)

print("{0:0.5f}".format(adjusted_chipload))
print("{0:0.0f}".format(feedrate))
print("{0:0.2f}".format(mrr))


def get_power_usage(mrr: float, k_factor: float) -> float:
    return mrr / k_factor


def get_torque(power_usage: float, rpm: float) -> float:
    return power_usage * 63024. / rpm


power_usage = get_power_usage(mrr=mrr, k_factor=k_factor)
torque = get_torque(power_usage=power_usage, rpm=rpm)

print("{0:0.3f}".format(power_usage))
print("{0:0.2f}".format(torque))


# max deflection
#=IF(E30="","",IF($D$5<$D$8,G30*($D$6^3/(3*$D$12*(PI()*($D$5/2)^4/4))+($D$9-$D$6)^3/(3*$D$12*(PI()*($D$8/2)^4/4))),IF($D$5=$D$8,G30*$D$9^3/(3*$D$12*(PI()*($D$5/2)^4/4)),G30*$D$9^3/(3*$D$12*PI()*($D$8/2)^4/4)))/$D$13)

