import os, sys  

engine_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "engine"))
dataset_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "dataset"))
if engine_path not in sys.path:
    sys.path.append(engine_path)
    
from initial_solution import generate_random_initial_solution
from parse_data import courses, rooms, weights, distributions, students
from final_result import result
from cost_function import full_cost_function
from neighbor import generate_neighbor
from graph_utils import (
    plot_cost_versus_iteration_graph,
    plot_penalty_breakdown,
    save_in_text
)


base_dir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "output_files")
)
metrics_dir = os.path.join(base_dir, "metrics_track")

os.makedirs(metrics_dir, exist_ok=True)
