from multiprocessing import freeze_support
import os, time
from index import save_in_text
from ga import run_parallel_ga_experiments
from sa import sa_main_code
from ts import run_parallel_ts_experiments
# base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
base_dir = os.getcwd()

output_folder = os.path.join(base_dir, 'output_files')
os.makedirs(output_folder, exist_ok=True) 
execution_time_dir = os.path.join(output_folder, "execution_time")
os.makedirs(execution_time_dir, exist_ok=True)

def main(algo_type):
    if algo_type == "SA":
        sa_main_code()
    elif algo_type =="TS":
        run_parallel_ts_experiments()
    elif algo_type == "GA":
        run_parallel_ga_experiments()

# algo_type="SA"
algo_type="TS"
if __name__ == "__main__":
    freeze_support()
    start_time = time.time()
    main(algo_type)
    end_time = time.time()
    execution_time = round(end_time - start_time, 4)
    print('Total Time taken', execution_time)
    save_in_text(f'{execution_time_dir}/{algo_type}_execution.csv', [start_time, end_time, execution_time])
