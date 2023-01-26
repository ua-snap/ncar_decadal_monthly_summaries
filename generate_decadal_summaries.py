import argparse
import glob
import xarray as xr
import numpy as np
import rasterio as rio
import pickle
import logging
from pathlib import Path
from config import mo_names, months, unit_di, summary_di, variable_di
from wrf_raster_profile import create_wrf_raster_profile


def create_decadal_averages(input_dir, output_dir, dry_run):

    if "met" in input_dir:
        src_type = "met"
    else:
        src_type = "vic_hydro"

    for file_set in variable_di[src_type].keys():

        paths = [Path(x) for x in glob.glob(f"{input_dir}*") if file_set in x]
        scenario = paths[0].parent.name
        model = paths[0].parent.parent.name

        log_tag = f"{model}_{scenario}_{src_type}_{file_set}"
        logging.basicConfig(filename=f"{log_tag}.log", level=logging.INFO)
        logging.info("Input directory: %s", input_dir)
        logging.info("Output directory: %s", output_dir)
        logging.info("Input files: %s", [x.name for x in paths])

        try:
            with open("wrf_profile.pickle", "rb") as handle:
                wrf_profile = pickle.load(handle)
        except:
            wrf_profile = create_wrf_raster_profile(paths[0])

        if dry_run:
            logging.info("Dry run: no data will be written to disk.")
        else:
            data_di = {}
            for file in paths:
                ds = xr.open_dataset(file)
                year = int(file.name.split("_")[-1].split(".")[0])
                data_di[year] = ds

            for i in range(1950, 2100, 10):
                start_year = i
                end_year = i + 9
                ds_decadal = xr.concat(
                    [data_di[j] for j in range(start_year, end_year + 1)], dim="time"
                )

                for file_type in variable_di[src_type].keys():
                    for climvar in variable_di[src_type][file_type].keys():
                        summary_func = variable_di[src_type][file_type][climvar]
                        out = (
                            ds_decadal[climvar]
                            .resample(time="1M")
                            .reduce(summary_func)
                            .groupby("time.month")
                            .reduce(np.mean)
                        )
                        dec_mean_monthly_summary = out.compute()

                        for mo in months:
                            # we lose the orientation from xr and it flips upside down
                            data = np.flipud(
                                dec_mean_monthly_summary.sel(month=mo).data
                            )
                            # set the output filename
                            units = unit_di[climvar]
                            mo_summary_func = summary_di[climvar]
                            out_filename = f"{climvar}_{units}_{model}_{scenario}_{mo_names[mo]}_{mo_summary_func}_{start_year}-{end_year}.tif"
                            logging.info("Output file: %s", out_filename)

                            # TODO Can we 3338 these right here, before writing them to disk?

                            with rio.open(
                                Path(output_dir) / out_filename, "w", **wrf_profile
                            ) as dst:
                                dst.write(data, 1)
            for k in data_di:
                data_di[k].close()


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("input_dir", help="directory containing input netCDF files")
    parser.add_argument("output_dir", help="directory to save output GeoTIFF files")
    parser.add_argument(
        "-d",
        "--dry-run",
        action="store_true",
        help="Dry run mode, no data will be written to disk.",
    )
    args = parser.parse_args()

    create_decadal_averages(args.input_dir, args.output_dir, args.dry_run)
