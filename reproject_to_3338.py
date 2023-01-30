from rasterio.io import MemoryFile
from rasterio.enums import Resampling
from rasterio.warp import calculate_default_transform, reproject
from rasterio.crs import CRS
from contextlib import contextmanager


@contextmanager
def reproject_raster_to_3338(wrf):
    src_crs = wrf.crs
    dst_crs = CRS.from_epsg(3338)
    transform, width, height = calculate_default_transform(
        src_crs, dst_crs, wrf.width, wrf.height, *wrf.bounds
    )
    kwargs = wrf.meta.copy()

    kwargs.update(
        {"crs": dst_crs, "transform": transform, "width": width, "height": height}
    )

    with MemoryFile() as memfile:
        with memfile.open(**kwargs) as dst:
            reproject(
                source=wrf,
                destination=dst,
                src_transform=wrf.transform,
                src_crs=wrf.crs,
                dst_transform=transform,
                dst_crs=dst_crs,
                resampling=Resampling.nearest,
            )
        with memfile.open() as dataset:  # Reopen as DatasetReader
            yield dataset  # Note yield not return as we're a contextmanager


# # Update the CRS in the profile
# ak_albers_profile = wrf_profile.copy()
# ak_albers_profile.update(crs="EPSG:3338")
# # Update the affine transform in the profile
# ak_albers_profile.update(
#     transform=rasterio.warp.calculate_default_transform(
#         src_crs=wrf_profile["crs"],
#         dst_crs="EPSG:3338",
#         width=reprojected_data.shape[2],
#         height=reprojected_data.shape[1],
#         left=0,
#         bottom=0,
#         right=1,
#         top=1,
# with rio.io.MemoryFile() as memfile:
#     with memfile.open(**wrf_profile) as mem_src:
#         mem_src.write(data, 1)
#         reprojected_data, aff = rio.warp.reproject(
#             mem_src.read(1),
#             mem_src.transform,
#             src_crs=wrf_profile["crs"],
#             dst_crs="EPSG:3338",
#         )
#         ak_albers_profile = wrf_profile.copy()
#         ak_albers_profile.update(crs="EPSG:3338")
#         ak_albers_profile.update(transform=aff)
