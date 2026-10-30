"""Make `pytest` regenerate reports/ and img/ byte-for-byte on any machine.

scikit-learn's OpenMP code (e.g. HistGradientBoosting) sums in an order that depends on the
number of threads, so a 4-core CI runner and an 8-core laptop drew slightly different charts.
pytest imports this file before the test modules, i.e. before scikit-learn starts OpenMP.
"""
import os

os.environ["OMP_NUM_THREADS"] = "1"
