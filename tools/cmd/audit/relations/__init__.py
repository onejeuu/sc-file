from pathlib import Path

from tools.cmd.audit.runner import Plan
from . import arms


BUILDERS = {arms.KIND: arms.build}
NAMES = tuple(BUILDERS)


def build(root: Path, selected: tuple[str, ...]) -> Plan:
    plan = Plan()
    for name in selected:
        plan.extend(BUILDERS[name](root))
    return plan
