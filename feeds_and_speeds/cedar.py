import copy
from typing import Tuple, List

import numpy as np

from feeds_and_speeds.calculator import (
    FeedsAndSpeedsCalculator,
    CutterMaterial,
    Machine,
    Router,
    Cutter,
)
from feeds_and_speeds.defaults import cutter_201, shapeoko

if __name__ == "__main__":
    calculator = FeedsAndSpeedsCalculator(
        machine=shapeoko,
        cutter=cutter_201,
        chipload=0.001,
        woc=0.1875,
        doc=0.0750,
        rpm=18000.0,
        k_factor=10.0,
        max_acceptable_deflection=0.0010,
    )
    min_doc = 0.001
    max_doc = 3.0 / 16.0
    min_woc = 0.05 * 0.25
    max_woc = 0.25
    docs = np.linspace(min_doc, max_doc, 100)
    wocs = np.linspace(min_woc, max_woc, 100)

    combinations: List[Tuple[float, float]] = []
    for doc in docs:
        for woc in wocs:
            combinations.append((doc, woc))

    print(combinations)

    def calculator_with_doc_woc(
        calculator: FeedsAndSpeedsCalculator, doc: float, woc: float
    ) -> FeedsAndSpeedsCalculator:
        calculator_copy = copy.deepcopy(calculator)
        calculator_copy.doc = doc
        calculator_copy.woc = woc
        return calculator_copy

    calculators = [
        calculator_with_doc_woc(calculator, doc, woc) for doc, woc in combinations
    ]
    acceptable_machine_force_calculators = [
        c
        for c in calculators
        if 0.24 < c.machine_force_percent < 0.25
        and 0.24 < c.available_power_percent < 0.25
        and c.max_deflection_percent < 0.1
        and c.feedrate < 180
    ]
    # print(acceptable_machine_force_calculators)
    print(
        [
            (c.woc, c.doc, c.material_removal_rate)
            for c in acceptable_machine_force_calculators
        ]
    )
    print(len(acceptable_machine_force_calculators))
    calculator_with_max_mrr: FeedsAndSpeedsCalculator = (
        acceptable_machine_force_calculators[0]
    )
    for c in acceptable_machine_force_calculators:
        if c.material_removal_rate > calculator_with_max_mrr.material_removal_rate:
            calculator_with_max_mrr = c

    calculator_with_max_mrr.print_feeds_and_speeds()
