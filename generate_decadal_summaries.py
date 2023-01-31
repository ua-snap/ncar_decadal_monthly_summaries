import argparse
import glob
import xarray as xr
import numpy as np
import rasterio as rio
import pickle
import logging
import warnings
from pathlib import Path
from config import mo_names, months, unit_di, summary_di, variable_di, precision_di
from wrf_raster_profile import create_wrf_raster_profile


def create_decadal_averages(input_dir, output_dir, dry_run):

    if "met" in input_dir:
        src_type = "met"
    else:
        src_type = "vic_hydro"

    for met_or_wf_or_ws in variable_di[src_type].keys():

        paths = [Path(x) for x in glob.glob(f"{input_dir}*") if met_or_wf_or_ws in x]
        scenario = paths[0].parent.name
        model = paths[0].parent.parent.name

        log_tag = f"{model}_{scenario}_{src_type}_{met_or_wf_or_ws}"
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
                logging.info(f"Processing data between {start_year} and {end_year}...")
                logging.info(f"Processing data for {met_or_wf_or_ws}...")
                for climvar in variable_di[src_type][met_or_wf_or_ws].keys():
                    logging.info(f"Processing data for variable {climvar}...")
                    summary_func = variable_di[src_type][met_or_wf_or_ws][climvar]
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
                        data = np.flipud(dec_mean_monthly_summary.sel(month=mo).data)
                        # round to sensible precision levels
                        data = round(data, precision_di[climvar])
                        # set output filename
                        units = unit_di[climvar]
                        mo_summary_func = summary_di[climvar]
                        out_filename = f"{climvar.lower()}_{units}_{model}_{scenario}_{mo_names[mo]}_{mo_summary_func}_{start_year}-{end_year}_mean.tif"
                        logging.info("Output file: %s", out_filename)
                        # reproject data to EPSG:3338
                        out_crs = rio.crs.CRS.from_epsg(3338).to_proj4()

                        (
                            out_transform,
                            out_width,
                            out_height,
                        ) = rio.warp.calculate_default_transform(
                            wrf_profile["crs"].to_proj4(),
                            out_crs,
                            data.shape[1],
                            data.shape[0],
                            left=-1794000.000,
                            bottom=-4046424.205,
                            right=1794000.000,
                            top=-1538424.205,
                        )
                        dst_arr = np.empty((out_height, out_width), dtype=data.dtype)
                        reprojected_data, _ = rio.warp.reproject(
                            data,
                            destination=dst_arr,
                            src_transform=wrf_profile["transform"],
                            src_crs=wrf_profile["crs"],
                            src_nodata=wrf_profile["nodata"],
                            dst_crs=out_crs,
                            dst_transform=out_transform,
                            dst_nodata=wrf_profile["nodata"],
                            height=out_height,
                            width=out_width,
                        )
                        ak_albers_profile = wrf_profile.copy()
                        ak_albers_profile["crs"] = out_crs
                        ak_albers_profile["transform"] = out_transform
                        ak_albers_profile["height"] = out_height
                        ak_albers_profile["width"] = out_width

                        # write to disk
                        with rio.open(
                            Path(output_dir) / out_filename, "w", **ak_albers_profile
                        ) as dst:
                            dst.write(reprojected_data, 1)
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

    # ignore warning - we have to convert the WRF CRS to a string format
    # it is needed to compute the transform to 3338
    warnings.filterwarnings(
        "ignore",
        message="You will likely lose important projection information when converting to a PROJ string",
    )
    create_decadal_averages(args.input_dir, args.output_dir, args.dry_run)
