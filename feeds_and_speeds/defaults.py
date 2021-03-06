from feeds_and_speeds.calculator import Cutter, CutterMaterial, Router, Machine

shapeoko = Machine(
    maximum_machine_force=18.0,
    router=Router(
        input_voltage=120.0, input_current=6.5, efficiency=0.6, rated_speed=30000.0
    ),
)

cutter_201 = Cutter(
    material=CutterMaterial.carbide,
    diameter=0.25,
    length=0.75,
    flutes=3,
    shank_diameter=0.25,
    overall_stickout=1,
    maximum_deflection=0.0010,
)

cutter_205e = Cutter(
    material=CutterMaterial.carbide,
    diameter=0.25,
    length=1,
    flutes=2,
    shank_diameter=0.25,
    overall_stickout=1.25,
    maximum_deflection=0.0010,
)
