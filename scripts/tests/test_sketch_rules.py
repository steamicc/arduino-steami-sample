# SPDX-License-Identifier: GPL-3.0-or-later
"""EXTI line 0 rule: the sketches leave it to MENU_BUTTON.

On the STM32WB55, INT_EXPANDER (PB0) shares EXTI line 0 with MENU_BUTTON
(PA0). A SteamiMCP23009E built with INT_EXPANDER calls attachInterrupt() on
PB0 and replaces the MENU interrupt of SteamiButtons (same rule as
steamicc/arduino-steami-lib scripts/tests/test_exti0_rules.py).
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# A SteamiMCP23009E construction that passes INT_EXPANDER.
EXPANDER_WITH_IRQ = re.compile(
    r"SteamiMCP23009E\s+\w+\s*[({][^;]*\bINT_EXPANDER\b", re.DOTALL
)


class SketchRulesTest(unittest.TestCase):
    def test_matcher_sees_the_interrupt_pin(self) -> None:
        self.assertTrue(
            EXPANDER_WITH_IRQ.search(
                "SteamiMCP23009E dpad(Steami.wire(), RST_EXPANDER, MCP23009_I2C_ADDR, INT_EXPANDER);"
            ),
            "matcher is blind",
        )
        self.assertFalse(
            EXPANDER_WITH_IRQ.search(
                "SteamiMCP23009E dpad(Steami.wire(), RST_EXPANDER, MCP23009_I2C_ADDR);"
            )
        )

    def test_no_sketch_attaches_the_expander_interrupt(self) -> None:
        sketches = sorted((ROOT / "examples").glob("*/*/*.ino"))
        self.assertTrue(sketches, "no sketch found")
        offenders = [
            str(p.relative_to(ROOT))
            for p in sketches
            if EXPANDER_WITH_IRQ.search(p.read_text(encoding="utf-8", errors="replace"))
        ]
        self.assertEqual(offenders, [])


if __name__ == "__main__":
    unittest.main()
