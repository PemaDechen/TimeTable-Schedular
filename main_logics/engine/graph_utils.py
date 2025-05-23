import matplotlib.pyplot as plt  # type: ignore
import csv
from datetime import datetime
import os

# base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
base_dir = os.getcwd()
output_folder = os.path.join(base_dir, 'output_files')
os.makedirs(output_folder, exist_ok=True) 
graph_dir = os.path.join(output_folder, "graphs")
os.makedirs(graph_dir, exist_ok=True)

def plot_cost_versus_iteration_graph(cost_history, filename, subfolder, csvfolder):
    # creating folder inside graphs
    full_folder = os.path.join(graph_dir, subfolder)
    os.makedirs(full_folder, exist_ok=True)  # Ensure it exists
    save_image_path = os.path.join(full_folder, filename)
    plt.figure(figsize=(10, 5))
    plt.plot(range(len(cost_history)), cost_history, marker="o", linewidth=2)
    plt.xlabel("Iteration")
    plt.ylabel("Penalty Cost")
    plt.title("Cost vs Iteration - Simulated Annealing")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(save_image_path)
    plt.close()
    save_path_csv = os.path.join(csvfolder, filename)
    save_in_excel(save_path_csv + ".csv", cost_history, ["Iteration", "Cost"])
    print(f"{filename} is saved")


def plot_penalty_breakdown(penalty_breakdown, filename, subfolder, csvfolder):
    full_folder = os.path.join(graph_dir, subfolder)
    os.makedirs(full_folder, exist_ok=True)  # Ensure it exists
    save_path = os.path.join(full_folder, filename)

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
    plt.savefig(save_path)
    plt.close()
    save_path_csv = os.path.join(csvfolder, filename)
    save_in_excel(
        save_path_csv + ".csv",
        [penalties, constraints],
        ["Constraint", "Penalty"],
    )
    print(f"{filename} is saved")


def save_in_excel(fileName, data, rowNames):

    with open(fileName, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([rowNames[0], rowNames[1]])
        if rowNames[0] == "Constraint":
           penalties, constraints = data
           for constraint, penalty in zip(constraints, penalties):
               writer.writerow([constraint, penalty])
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
