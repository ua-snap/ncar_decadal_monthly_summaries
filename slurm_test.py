import dask
import dask.distributed
import numpy as np
from dask_jobqueue import SlurmCluster
from config import (
    target_dirs,
    mo_names,
)


def dask_test(target, client):
    print(target)
    x = np.zeros(1000) * 3.14
    print(np.max(x))


def main():
    # Set up the Dask cluster with Slurm
    cluster = SlurmCluster(cores=32, memory="16GB", job_extra=["--partition=main"])
    cluster.adapt(minimum_jobs=0, maximum_jobs=10)
    client = Client(cluster)

    for target in target_dirs:
        dask_test(target, client)


if __name__ == "__main__":
    main()
