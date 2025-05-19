import csv
import os
from multiprocessing import Pool, cpu_count, freeze_support


# ───── PATH SETUP ─────
# This file is based on algorithms
def run_log_csv(path):
    # ───── INIT LOG FILE IF NEEDED ─────
    if not os.path.exists(path):
        with open(path, mode="w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    "Temp",
                    "Run",
                    "InitialTemp",
                    "CoolingRate",
                    "Iterations",
                    "FinalCost",
                    "ExecutionTime_sec",
                    "StartTime",
                    "EndTime",
                ]
            )
