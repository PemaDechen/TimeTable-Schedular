import matplotlib.pyplot as plt

def plot_cost_versus_iteration_graph(cost_history):
    plt.figure(figsize=(10, 5))
    plt.plot(range(len(cost_history)), cost_history, marker='o', linewidth=2)
    plt.xlabel("Iteration")
    plt.ylabel("Penalty Cost")
    plt.title("Cost vs Iteration - Simulated Annealing")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("cost_vs_iteration.png")
    plt.show()
    save_in_excel("cost_history.csv", cost_history, ['Iteration', 'Cost'])


import csv

def save_in_excel(fileName, data, rowNames):
    with open( fileName, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([rowNames[0], rowNames[1]])
        for i, cost in enumerate(data):
            writer.writerow([i, cost])