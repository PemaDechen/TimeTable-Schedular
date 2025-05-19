import math
import random
import time
import os
import csv
from datetime import datetime
from operator import itemgetter
import matplotlib.pyplot as plt # type: ignore
from multiprocessing import Pool, cpu_count, freeze_support

from intitial_solution import generate_random_initial_solution
from parse_data import courses, rooms, weights, distributions, students
from sample_result import result
from cost_function import full_cost_function
from neighbor import generate_neighbor
from graph_utils import (
    plot_cost_versus_iteration_graph,
    plot_penalty_breakdown,
)

# ───── SA PARAMETERS ─────
initial_temps = [10, 100, 1000]
cooling_rate = 0.95
min_temp = 1
max_iterations = 100
num_runs = 10

# ───── PATH SETUP ─────
metrics_dir = "metrics_track"
os.makedirs(metrics_dir, exist_ok=True)
run_log_path = os.path.join(metrics_dir, "run_log.csv")

# ───── INIT LOG FILE IF NEEDED ─────
if not os.path.exists(run_log_path):
    with open(run_log_path, mode="w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Temp", "Run", "InitialTemp", "CoolingRate", "Iterations",
            "FinalCost", "ExecutionTime_sec", "StartTime", "EndTime"
        ])

# ───── SA CORE FUNCTION ─────
def simulated_annealing(initial_solution, courses, students, rooms, weights, distributions, temp):
    current_solution = initial_solution
    current_cost, penalty_breakdown = full_cost_function(current_solution, courses, rooms, students, weights, distributions)

    best_solution = current_solution
    best_cost = current_cost
    best_penalty_breakdown = penalty_breakdown

    temperature = temp
    iteration = 0
    cost_history = []

    while temperature > min_temp and iteration < max_iterations:
        neighbor = generate_neighbor(current_solution, courses, rooms, weights)
        neighbor_cost, neighbor_penalty_breakdown = full_cost_function(neighbor, courses, rooms, students, weights, distributions)

        delta = neighbor_cost - current_cost
        if delta < 0 or random.uniform(0, 1) < math.exp(-delta / temperature):
            current_solution = neighbor
            current_cost = neighbor_cost
            if current_cost < best_cost:
                best_solution = current_solution
                best_cost = current_cost
                best_penalty_breakdown = neighbor_penalty_breakdown

        cost_history.append(current_cost)
        temperature *= cooling_rate
        iteration += 1

    return best_solution, best_cost, cost_history, best_penalty_breakdown

# ───── WORKER FUNCTION FOR PARALLEL SA RUN ─────
def sa_worker(args):
    temp, run_num = args
    print(f"\n✨ Running SA | Temp={temp}, Run={run_num}")
    start_time = time.time()
    initial_solution = generate_random_initial_solution(courses, rooms)

    final_solution, final_cost, cost_history, best_penalty_breakdown = simulated_annealing(
        initial_solution, courses, students, rooms, weights, distributions, temp
    )

    end_time = time.time()
    execution_time = round(end_time - start_time, 4)
    start_dt = datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S')
    end_dt = datetime.fromtimestamp(end_time).strftime('%Y-%m-%d %H:%M:%S')

    # ───── GRAPHING ─────
    cost_folder = os.path.join(metrics_dir, f"cost_vs_iteration_{temp}")
    penalty_folder = os.path.join(metrics_dir, f"penalty_breakdown_{temp}")
    os.makedirs(cost_folder, exist_ok=True)
    os.makedirs(penalty_folder, exist_ok=True)

    plot_cost_versus_iteration_graph(
        cost_history,
        filename=f"cost_vs_iteration_run{run_num}",
        subfolder=f"cost_vs_iteration_{temp}",
        csvfolder=cost_folder
    )

    plot_penalty_breakdown(
        best_penalty_breakdown,
        filename=f"penalty_breakdown_run{run_num}",
        subfolder=f"penalty_breakdown_{temp}",
        csvfolder=penalty_folder
    )

    result(final_solution, f"SaResult_Temp{temp}_Run{run_num}")

    with open(run_log_path, mode="a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            temp, run_num, temp, cooling_rate, max_iterations,
            final_cost, execution_time, start_dt, end_dt
        ])

    return {
        "temp": temp,
        "run": run_num,
        "cost": final_cost,
        "time": execution_time,
        "breakdown": best_penalty_breakdown,
        "cost_curve": cost_history
    }

# ───── RUN SA IN PARALLEL ACROSS TEMPS ─────
def main():
    all_cost_curves = {}
    for temp in initial_temps:
        args_list = [(temp, run_id) for run_id in range(1, num_runs + 1)]
        with Pool(min(cpu_count(), num_runs)) as pool:
            results = pool.map(sa_worker, args_list)
        combined_cost = [0] * max_iterations
        
        for res in results:
            for idx, cost in enumerate(res["cost_curve"]):
                combined_cost[idx] += cost
        avg_cost_curve = [v / num_runs for v in combined_cost]
        all_cost_curves[temp] = avg_cost_curve
        # ───── SAVE TOP 3 PER TEMP ─────
        top3 = sorted(results, key=itemgetter("cost"))[:3]
        with open(os.path.join(metrics_dir, f"top3_temp_{temp}.csv"), "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Run", "FinalCost", "ExecutionTime_sec"] + list(top3[0]["breakdown"].keys()))
            for entry in top3:
                writer.writerow([
                    entry["run"], entry["cost"], entry["time"]
                ] + list(entry["breakdown"].values()))
                
# ───── COMBINED PLOT: COST VS ITERATION FOR ALL TEMPS ─────
    plt.figure(figsize=(10, 6))
    for temp, curve in all_cost_curves.items():
        plt.plot(range(len(curve)), curve, label=f"Temp={temp}")
    plt.xlabel("Iteration")
    plt.ylabel("Average Cost")
    plt.title("Cost vs Iteration for Different Initial Temperatures")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(metrics_dir, "combined_cost_vs_iteration.png"))
    plt.close()
    print("✅ Combined cost vs iteration graph saved.")

if __name__ == "__main__":
    freeze_support()
    main()