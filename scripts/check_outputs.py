#!/usr/bin/env python3
"""Fail CI when a project's regenerated outputs differ from the committed ones in a way that matters.

Run from a project folder after its tests have regenerated reports/ and img/.

- .json / .csv: every number must match the committed value within REL_TOL / ABS_TOL. That is far
  tighter than anything the READMEs quote (3 decimals), so a real change in results still fails,
  while floating-point noise from a different CPU (SIMD width, BLAS kernel) does not.
- .png: never compared. Anti-aliasing and font hinting differ between machines; the numbers behind
  the charts are already checked above.
- any other tracked file: must be byte-identical.

Differences are printed and also emitted as GitHub annotations so they can be read without logs.
"""
from __future__ import annotations

import csv
import io
import json
import math
import subprocess
import sys

REL_TOL = 1e-4
ABS_TOL = 1e-6


def git(*args: str) -> str:
    return subprocess.run(["git", *args], check=True, capture_output=True, text=True).stdout


def committed(path: str) -> str:
    return git("show", f"HEAD:./{path}")


def close(a: object, b: object) -> bool:
    if isinstance(a, bool) or isinstance(b, bool):
        return a == b
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        if isinstance(a, float) and isinstance(b, float) and math.isnan(a) and math.isnan(b):
            return True
        return math.isclose(a, b, rel_tol=REL_TOL, abs_tol=ABS_TOL)
    return a == b


def json_diffs(old: object, new: object, where: str = "$") -> list[str]:
    if isinstance(old, dict) and isinstance(new, dict):
        out: list[str] = []
        for k in sorted(set(old) | set(new)):
            if k not in old or k not in new:
                out.append(f"{where}.{k}: key only in {'new' if k in new else 'committed'}")
            else:
                out += json_diffs(old[k], new[k], f"{where}.{k}")
        return out
    if isinstance(old, list) and isinstance(new, list):
        if len(old) != len(new):
            return [f"{where}: length {len(old)} -> {len(new)}"]
        out = []
        for i, (a, b) in enumerate(zip(old, new)):
            out += json_diffs(a, b, f"{where}[{i}]")
        return out
    return [] if close(old, new) else [f"{where}: {old!r} -> {new!r}"]


def num(cell: str) -> object:
    try:
        return float(cell)
    except ValueError:
        return cell


def csv_diffs(old: str, new: str) -> list[str]:
    a = list(csv.reader(io.StringIO(old)))
    b = list(csv.reader(io.StringIO(new)))
    if len(a) != len(b):
        return [f"rows {len(a)} -> {len(b)}"]
    out = []
    for r, (ra, rb) in enumerate(zip(a, b)):
        if len(ra) != len(rb):
            out.append(f"row {r}: columns {len(ra)} -> {len(rb)}")
            continue
        for c, (x, y) in enumerate(zip(ra, rb)):
            if not close(num(x), num(y)):
                out.append(f"row {r} col {c}: {x} -> {y}")
    return out


def main() -> int:
    changed = [p for p in git("diff", "--name-only", "--relative", "--", ".", ":!**/__pycache__").splitlines() if p]
    problems: list[str] = []
    for path in changed:
        if path.endswith(".png"):
            print(f"ignored (image): {path}")
            continue
        with open(path, encoding="utf-8") as fh:
            new = fh.read()
        old = committed(path)
        if path.endswith(".json"):
            diffs = json_diffs(json.loads(old), json.loads(new))
        elif path.endswith(".csv"):
            diffs = csv_diffs(old, new)
        else:
            diffs = [] if old == new else ["content changed"]
        if diffs:
            problems.append(f"{path}: " + "; ".join(diffs[:10]) + (f" (+{len(diffs) - 10} more)" if len(diffs) > 10 else ""))
        else:
            print(f"within tolerance: {path}")
    for p in problems:
        print(f"::error::{p}")
    if problems:
        print("Committed results are stale. Re-run the tests locally and commit reports/ and img/.")
        return 1
    print("Outputs match the committed results.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
