import matplotlib.pyplot as plt  # type: ignore
import csv
from datetime import datetime
import os

os.makedirs("./graphs", exist_ok=True)


def plot_cost_versus_iteration_graph(cost_history, fileName, folderName):
    plt.figure(figsize=(10, 5))
    plt.plot(range(len(cost_history)), cost_history, marker="o", linewidth=2)
    plt.xlabel("Iteration")
    plt.ylabel("Penalty Cost")
    plt.title("Cost vs Iteration - Simulated Annealing")
    plt.grid(True)
    plt.tight_layout()
    # plt.show()
    # Save in 'graphs/' directory
    save_path = os.path.join("graphs/" + folderName + "/" + fileName + ".png")
    plt.savefig(save_path)
    plt.close()
    save_in_excel(fileName + ".csv", cost_history, ["Iteration", "Cost"])
    print(f"{fileName} is saved")


def plot_penalty_breakdown(penalty_breakdown, filename, folderName):
    constraints = list(penalty_breakdown.keys())
    penalties = list(penalty_breakdown.values())
    plt.figure(figsize=(12, 6))
    bars = plt.bar(constraints, penalties, color="skyblue")
    plt.xticks(rotation=45, ha="right")
    plt.ylabel("Penalty Value")
    plt.title("Penalty Breakdown by Constraint")
    # Annotate each bar with its value
    for bar in bars:
        yval = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            yval + 5,
            int(yval),
            ha="center",
            va="bottom",
            fontsize=9,
        )
    plt.tight_layout()
    # plt.show()
    save_path = os.path.join("graphs/" + folderName + "/" + filename + ".png")
    plt.savefig(save_path)
    plt.close()
    save_in_excel(
        "./metrics_track/" + filename + ".csv",
        [penalties, constraints],
        ["Constraint", "Penalty"],
    )
    print(f"{filename} is saved")


def save_in_excel(fileName, data, rowNames):
    with open(fileName, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([rowNames[0], rowNames[1]])
        if rowNames[0] == "Constraint":
            for i, cost in enumerate(data[0]):
                writer.writerow([data[i], cost])
        else:
            for i, cost in enumerate(data):
                writer.writerow([i, cost])


def save_in_text(fileName, data):
    start_dt = datetime.fromtimestamp(data[0])
    end_dt = datetime.fromtimestamp(data[1])
    duration = data[2]
    with open(fileName, "w") as f:
        f.write(f"Started at: {start_dt.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Ended at: {end_dt.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total Execution Time: {duration:.4f} seconds\n")
        f.write(f"Final Cost {data[3]}")
        f.write(f"Execution Time {data[4]}")
        f.write(f"Penalty Breakdown{data[5]}")
