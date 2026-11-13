"""Run all examples and report the convergence of every solve."""
import io
import runpy
import sys
import warnings
from contextlib import redirect_stdout
from pathlib import Path

from tespy.networks import Network

EXAMPLES = [
    "libr_water_absorber.py",
    "libr_water_absorber_cooled.py",
    "libr_water_desorber.py",
    "libr_water_desorber_heated.py",
    "libr_water_chiller.py",
    "nh3_water_absorber.py",
    "nh3_water_generator_rectifier.py",
    "nh3_water_chiller.py",
]

statuses = []
solve = Network.solve


def recording_solve(self, *args, **kwargs):
    solve(self, *args, **kwargs)
    statuses.append(self.status)


Network.solve = recording_solve
warnings.simplefilter("ignore")
failed = False
for example in EXAMPLES:
    statuses.clear()
    try:
        with redirect_stdout(io.StringIO()):
            runpy.run_path(str(Path(__file__).parent / example), run_name="__main__")
        error = ""
    except Exception as e:
        error = f" - {type(e).__name__}: {e}"
    converged = sum(status in (0, 1) for status in statuses)
    failed = failed or error or converged < len(statuses)
    print(f"{example}: {converged} of {len(statuses)} solves converged{error}")
sys.exit(1 if failed else 0)
