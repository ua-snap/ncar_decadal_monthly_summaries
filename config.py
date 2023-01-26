import calendar
import numpy as np

months = list(range(1, 13))  # xr indexes months 1 to 12 after `groupby('time.month')`
mo_names = [x.lower() for x in calendar.month_abbr]

variable_di = {
    "met": {"met": {"pcp": np.sum, "tmax": np.mean, "tmin": np.mean}},
    "vic_hydro": {
        "wf": {
            "SNOW_MELT": np.sum,
            "EVAP": np.sum,
            "GLACIER_MELT": np.sum,
            "RUNOFF": np.sum,
        },
        "ws": {
            "IWE": np.max,
            "SWE": np.max,
            "SM1": np.mean,
            "SM2": np.mean,
            "SM3": np.mean,
        },
    },
}

unit_di = {
    "pcp": "mm",
    "tmax": "degC",
    "tmin": "degC",
    "SNOW_MELT": "mm",
    "EVAP": "mm",
    "GLACIER_MELT": "mm",
    "RUNOFF": "mm",
    "IWE": "mm",
    "SWE": "mm",
    "SM1": "mm",
    "SM2": "mm",
    "SM3": "mm",
}

summary_di = {
    "pcp": "total",
    "tmax": "mean",
    "tmin": "mean",
    "SNOW_MELT": "total",
    "EVAP": "total",
    "GLACIER_MELT": "total",
    "RUNOFF": "total",
    "IWE": "max",
    "SWE": "max",
    "SM1": "mean",
    "SM2": "mean",
    "SM3": "mean",
}
