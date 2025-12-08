import os
from multiprocessing import Pool, freeze_support
import sys
import psutil
import random
import shutil
import time
import gc
from MC_rollout import MC_Rollout


def get_list_buffer_id_game_id(src_folder):
    return [
        (entry.name, sub_entry.name)
        for entry in os.scandir(src_folder) if entry.is_dir()
        for sub_entry in os.scandir(entry.path) if sub_entry.is_dir()
    ]

def worker(process_pid):
    time.sleep(process_pid)
    replay_buffer_dir = r"\\10.5.10.44\TienLenNew2\replay_buffer"
    stats_dir = r"\\10.5.10.44\TienLenNew2\stats_data_1"
    
    list_buffer_id_game_id = get_list_buffer_id_game_id(replay_buffer_dir)
    simulation = MC_Rollout()
    while True:
        try:
            buffer_id, game_id = random.choice(list_buffer_id_game_id)
            game_dir = os.path.join(replay_buffer_dir, buffer_id, game_id)

            stats_folder = os.path.join(stats_dir, buffer_id, game_id)
            if os.path.exists(stats_folder): continue
            os.makedirs(stats_folder, exist_ok=True)

            print(f"Process {process_pid} get the folder: {game_dir}")
            shutil.copy2(os.path.join(game_dir, "initial_game_info.pkl"), 
                        os.path.join(stats_folder, "initial_game_info.pkl"))
            for data_dir in os.scandir(game_dir):
                result_dir = os.path.join(stats_folder, data_dir.name)
                if os.path.exists(result_dir): continue
                simulation.cal_and_save_stats_of_state(data_dir.path, result_dir)
                gc.collect()

        except Exception as e:
            print(f"ERROR processing {game_dir} and {data_dir.path}: {e}", flush=True)

if __name__ == "__main__":
    n_process = int(1.8 * psutil.cpu_count(logical=False))
    
    print(f"The number of running process: {n_process}")
    if sys.platform.startswith('win'):
        freeze_support()
    with Pool(processes=n_process) as pool:
        pool.map(worker, range(n_process))