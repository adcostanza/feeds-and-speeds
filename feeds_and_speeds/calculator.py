from dataclasses import dataclass
from enum import Enum
from math import sqrt, pi


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

    @property
    def output_power(self) -> float:
        return self.input_power * self.efficiency / 745.7


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
    shank_diameter=0.5,
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


def get_machine_force(torque: float, cutter_diameter: float) -> float:
    return torque / (cutter_diameter / 2)


machine_force = get_machine_force(torque=torque, cutter_diameter=cutter.diameter)
machine_force_percent = machine_force / machine.maximum_machine_force
print("{0:0.2f}".format(machine_force))
print("{0:0.0f}%".format(machine_force_percent * 100))

available_power_percent = power_usage / machine.router.output_power

print("{0:0.0f}%".format(available_power_percent * 100))

router_cutting_power_increase = power_usage * 745.7

print("{0:0.1f}".format(router_cutting_power_increase))

parse_me = "=IF(E30="","",IF($D$5<$D$8,G30*($D$6^3/(3*$D$12*(PI()*($D$5/2)^4/4))+($D$9-$D$6)^3/(3*$D$12*(PI()*($D$8/2)^4/4))),IF($D$5=$D$8,G30*$D$9^3/(3*$D$12*(PI()*($D$5/2)^4/4)),G30*$D$9^3/(3*$D$12*PI()*($D$8/2)^4/4)))/$D$13)"
mapping = {
    "D5": "cutter_diameter",
    "D8": "shank_diameter",
    "G30": "machine_force",
    "D6": "cutter_length",
    "D12": "youngs_modulus",
    "D9": "overall_stickout",
    "D13": "maximum_acceptable_deflection"
}
parsed = parse_me.replace("$", "")
for key, value in mapping.items():
    parsed = parsed.replace(key, value)
print(parsed)


def get_youngs_modulus(cutter_material: CutterMaterial) -> float:
    if cutter_material == CutterMaterial.carbide:
        return 87000000.
    elif cutter_material == CutterMaterial.hss:
        return 30000000.
    else:
        return 30000000.


youngs_modulus = get_youngs_modulus(cutter_material=cutter.material)


def get_max_deflection_percent(cutter: Cutter, machine_force: float, youngs_modulus: float,
                               max_acceptable_deflection: float):
    if cutter.diameter < cutter.shank_diameter:
        max_deflection = machine_force * (
                pow(cutter.length, 3) / (3 * youngs_modulus * (pi * pow(cutter.diameter / 2, 4) / 4)) + pow(
            cutter.overall_stickout - cutter.length, 3) / (
                        3 * youngs_modulus * (pi * pow(cutter.shank_diameter / 2, 4) / 4)))
    elif cutter.diameter == cutter.shank_diameter:
        max_deflection = machine_force * pow(cutter.overall_stickout, 3) / (
                3 * youngs_modulus * (pi * pow(cutter.diameter / 2, 4) / 4))
    else:
        max_deflection = machine_force * pow(cutter.overall_stickout, 3) / (
                3 * youngs_modulus * pi * pow(cutter.shank_diameter / 2, 4) / 4)

    return max_deflection / max_acceptable_deflection


max_acceptable_deflection = 0.0010
max_deflection_percent = get_max_deflection_percent(cutter=cutter, machine_force=machine_force,
                                                    youngs_modulus=youngs_modulus,
                                                    max_acceptable_deflection=max_acceptable_deflection)

print("{0:0.2f}%".format(max_deflection_percent * 100))
