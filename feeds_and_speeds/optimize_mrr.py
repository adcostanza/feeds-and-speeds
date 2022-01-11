import copy
from typing import Tuple, List

import numpy as np

from feeds_and_speeds.calculator import FeedsAndSpeedsCalculator
from feeds_and_speeds.defaults import cutter_201, shapeoko

if __name__ == "__main__":
    calculator = FeedsAndSpeedsCalculator(machine=shapeoko,
                                          cutter=cutter_201,
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
    acceptable_machine_force_calculators = [c for c in calculators if
                                            .24 < c.machine_force_percent < .25 and .24 < c.available_power_percent < 0.25 and c.max_deflection_percent < 0.1 and c.feedrate < 180]
    # print(acceptable_machine_force_calculators)
    print([(c.woc, c.doc, c.material_removal_rate) for c in acceptable_machine_force_calculators])
    print(len(acceptable_machine_force_calculators))
    calculator_with_max_mrr: FeedsAndSpeedsCalculator = acceptable_machine_force_calculators[0]
    for c in acceptable_machine_force_calculators:
        if c.material_removal_rate > calculator_with_max_mrr.material_removal_rate:
            calculator_with_max_mrr = c

    print((c.doc, c.woc, c.feedrate, c.material_removal_rate))
