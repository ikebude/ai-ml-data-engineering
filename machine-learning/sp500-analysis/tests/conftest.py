"""Make `pytest` regenerate reports/ and img/ byte-for-byte on any machine.

Loaded by pytest before the test modules, i.e. before the pipeline imports scikit-learn.
- scikit-learn's OpenMP code (e.g. HistGradientBoosting) sums in an order that depends on the
  number of threads, so a 4-core CI runner and an 8-core laptop drew slightly different charts.
- A machine-wide matplotlibrc (MATPLOTLIBRC, ~/.config/matplotlib) can change fonts and hinting;
  charts are always rendered with matplotlib's built-in defaults.
"""
import os

os.environ["OMP_NUM_THREADS"] = "1"
os.environ.pop("MATPLOTLIBRC", None)

import matplotlib  # noqa: E402

matplotlib.rcdefaults()
