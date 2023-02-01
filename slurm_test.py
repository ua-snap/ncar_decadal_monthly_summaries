import dask
import dask.distributed
import numpy as np
from dask_jobqueue import SLURMCluster
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
    cluster = SLURMCluster(
        cores=32, memory="16GB", job_extra_directives=["--partition=main"]
    )
    cluster.adapt(minimum_jobs=0, maximum_jobs=10)
    client = dask.distributed.Client(cluster)
    client.become_default()

    for target in target_dirs:
        dask_test(target, client)


if __name__ == "__main__":
    main()
