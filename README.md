# ETICO -- EstuarIO Thalweg Identification Code
_A python software to identify the thalweg in a river_

<p align="center">
<img src="./doc/img/etico_logo.png" width="50%">
</p>

## Preparation

Before running the script, you have to (create and) activate the proper environment. The creation can be done with:

```
$ conda create -n etico
$ conda activate etico
$ conda install python xarray cartopy termcolor matplotlib scipy
$ conda install -c conda-forge geopy
```

Then, activate the environment with:

```
$ conda activate myEnv
```


## Invoking the script

To invoke the script:

```
$ python etico.py <BATHYMETRY_FILE> <CONFIG_FILE>
```

Please remember to check that settings in the config file are correct. See `sample_tolle.conf` for an example.

## Code structure

If you want to investigate the code, or implement your changes, the following information about the structure may be helpful:

```
.
├── customThalweg.py                      # our main starting point
├── dataset                               # a collection of datasets to test the application
│   ├── GORO_100m_reg.nc                  # a section of the Po Goro branch with 100m resolution
│   └── GORO_10m_reg.nc                   # a section of the Po Goro branch with 10m resolution
├── __init__.py
├── libs                                  # the folder hosting the main code modules
│   ├── config_utilities.py               # the module taking care of the configuration
│   ├── exceptions.py                     # the module defining our custom exceptions
│   ├── __init__.py
│   ├── matrix_utilities.py               # the module hosting functions to deal with matrices
│   ├── plot_utilities.py                 # the module taking care of plot functionalities
│   ├── print_utilities.py                # a collection of print helpers
│   └── stopping_criteria.py              # where to implement the stopping criteria
├── logs                                  # a (currently not used) folder to automatically store logs
├── plots                                 # a (currently not used) fodler to automatically store plots
├── README.md
└── sample_goro.conf                      # an example of configuration file for a section of Po Goro
└── sample_goro_full.conf                 # an example of configuration file for the whole Po Goro
└── sample_tolle.conf                     # an example of configuration file for the whole Po Tolle
```

## Error codes

The script fails with an **error code** that should help the user to discover what's wrong:

1. Not enough parameters. You need to provide the bathymetry file and the configuration file

### Errors 2* -- Section "Algorithm" in config file
20. Incomplete configuration file. Missing section `Algorithm`
21. Incomplete configuration file. Missing `StartDir` in section `Algorithm`
22. Incomplete configuration file. Missing `WindowSize` in section `Algorithm`
23. Incomplete configuration file. Missing `StartLat` in section `Algorithm`
24. Incomplete configuration file. Missing `StartLon` in section `Algorithm`
25. Incomplete configuration file. Missing `EndLat` in section `Algorithm`
26. Incomplete configuration file. Missing `EndLon` in section `Algorithm`
27. Wrong setting in configuration file. `MaxSearchAlgo` can only be `Zonal` or `Classic`

### Errors 3* -- Section "Plot" in config file
30. Incomplete configuration file. Missing section `Plot`
31. Incomplete configuration file. Missing `PointSparsity` in section `Plot`
32. Incomplete configuration file. Missing `PointsEnabled` in section `Plot`
33. Incomplete configuration file. Missing `LablesEnabled` in section `Plot`
34. Incomplete configuration file. Missing `PointsSize` in section `Plot`
35. Incomplete configuration file. Missing `LabelsSize` in section `Plot`
36. Incomplete configuration file. Missing `LatMin` in section `Plot`
37. Incomplete configuration file. Missing `LatMax` in section `Plot`
38. Incomplete configuration file. Missing `LonMin` in section `Plot`
39. Incomplete configuration file. Missing `LonMax` in section `Plot`
40. Incomplete configuration file. Missing `PlotSteps` in section `Plot`

### Errors 5* -- Section "Output" in config file
50. Incomplete configuration file. Missing section `Output`
51. Incomplete configuration file. Missing `PlotDirectory` in section `Output`
52. Incomplete configuration file. Missing `BaselinePlotName` in section `Output`
53. Incomplete configuration file. Missing `LogFile` in section `Output`
54. Incomplete configuration file. Missing `OutputDirectory` in section `Output`
55. Incomplete configuration file. Missing `ThalwegFile` in section `Output`

### Errors 6* -- Section "Debug" in config file
60. Incomplete configuration file. Missing section `Debug`
61. Incomplete configuration file. Missing `PlotStartPoint` in section `Debug`
62. Incomplete configuration file. Missing `PlotEndPoint` in section `Debug`
63. Incomplete configuration file. Missing `ThalwegStop` option in `Debug` section of configuration file!

### Errors 1** - Working errors
100. Not enough parameters
101. Invalid zonal direction detected.


## Next steps
1. Switch to logging module
2. Increase the test cases
