from multiprocessing import Pool, cpu_count, freeze_support
from operator import itemgetter
import os, csv
import matplotlib.pyplot as plt  # type: ignore

from sa import initial_temps, num_runs, sa_worker, max_iterations
from index import metrics_dir


def main(algo_type):
    if algo_type == "SA":
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
            with open(
                os.path.join(metrics_dir, {algo_type}, f"top3_temp_{temp}.csv"),
                "w",
                newline="",
            ) as f:
                writer = csv.writer(f)
                writer.writerow(
                    ["Run", "FinalCost", "ExecutionTime_sec"]
                    + list(top3[0]["breakdown"].keys())
                )
                for entry in top3:
                    writer.writerow(
                        [entry["run"], entry["cost"], entry["time"]]
                        + list(entry["breakdown"].values())
                    )
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
    main(algo_type="SA")
