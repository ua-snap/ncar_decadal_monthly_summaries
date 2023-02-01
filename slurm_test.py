import dask.distributed
import numpy as np
from dask_jobqueue import SLURMCluster


def dask_test(target, client):
    print(target)
    x = np.zeros(1000) * 3.14
    print(np.max(x))


def main():
    # Set up the Dask cluster with Slurm
    cluster = SLURMCluster(
        cores=16,
        processes=2,
        memory="16GB",
        queue="main",
        walltime="00:30:00",
        # interface="enp129s0f0",
        log_directory="/atlas_scratch/cparr4/dask_jobqueue_logs/",
        account="snap",
        scheduler_options={"dashboard_address": ":43368", "interface": "enp129s0f0"},
    )
    cluster.scale(10)
    # for target in target_dirs:
    #     create_decadal_averages(target, output_dir, cluster)
    cluster.scale(0)
    cluster.close()


if __name__ == "__main__":
    main()
