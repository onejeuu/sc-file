from pathlib import Path

from tools.cmd.audit.runner import Plan
from . import arms, face


BUILDERS = {
    arms.KIND: arms.build,
    face.KIND: face.build,
}
NAMES = tuple(BUILDERS)


def build(root: Path, selected: tuple[str, ...]) -> Plan:
    plan = Plan()
    for name in selected:
        plan.extend(BUILDERS[name](root))
    return plan
