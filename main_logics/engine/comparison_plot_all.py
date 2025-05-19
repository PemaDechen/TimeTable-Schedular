import pandas as pd #type:ignore
import matplotlib.pyplot as plt #type:ignore
import seaborn as sns #type:ignore
import os
from glob import glob


def load_and_tag_results(file_pattern, algo_label):
    files = glob(file_pattern)
    all_dfs = []
    for file in files:
        df = pd.read_csv(file)
        df['Algorithm'] = algo_label
        all_dfs.append(df)
    return pd.concat(all_dfs, ignore_index=True)


def generate_comparison_plot():
    base_dir = "output_files/metrics_track"
    all_data = pd.concat([
        load_and_tag_results(os.path.join(base_dir, "sa_experiment_*.csv"), "SA"),
        load_and_tag_results(os.path.join(base_dir, "tabu_experiment_*.csv"), "TS"),
        load_and_tag_results(os.path.join(base_dir, "ga_experiment_*.csv"), "GA"),
        load_and_tag_results(os.path.join(base_dir, "hybrid_ga_sa_experiment_*.csv"), "GA+SA"),
        load_and_tag_results(os.path.join(base_dir, "hybrid_ga_ts_experiment_*.csv"), "GA+TS"),
        load_and_tag_results(os.path.join(base_dir, "hybrid_sa_ts_experiment_*.csv"), "SA+TS"),
    ], ignore_index=True)

    plt.figure(figsize=(10, 6))
    sns.boxplot(x='Algorithm', y='Best Cost', data=all_data)
    plt.title("Comparison of Metaheuristic Algorithms: Best Cost")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    return all_data

# To use:
# df = generate_comparison_plot()
