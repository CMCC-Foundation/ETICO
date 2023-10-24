# EstuarIO_thalweg
A python software to identify the thalweg in a river

## Preparation

Before running the script, you have to (create and) activate the proper environment. The creation can be done with:

```
$ conda create -f environment.yml --name myEnv
```

Then, activate the environment with:

```
$ conda activate myEnv
```


## Invoking the script

To invoke the script:

```
$ python customThalweg.py <BATHYMETRY_FILE> <CONFIG_FILE>
```

Please remember to check that settings in the config file are correct. See `sample.conf` for an example.

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
└── sample.conf                           # an example of configuration file

```

## Error codes

The script fails with an error code that should help the user to discover what's wrong:

1. Not enough parameters. You need to provide the bathymetry file and the configuration file
2. Incomplete configuration file. Missing "MaxSearchAlgo" in section "Algorithm"
3. Incomplete configuration file. Missing section "Algorithm"
4. Incomplete configuration file. Missing "WindowSize" in section "Algorithm"
5. Wrong setting in configuration file. "MaxSearchAlgo" can only be "Zonal" or "Classic" (no quotes)
6. Incomplete configuration file. Missing section "Plot"
7. Incomplete configuration file. Missing "PointSparsity" in section "Plot"
8. Incomplete configuration file. Missing "PointsEnabled" in section "Plot"
9. Incomplete configuration file. Missing "LablesEnabled" in section "Plot"
10. Incomplete configuration file. Missing "PointsSize" in section "Plot"
11. Incomplete configuration file. Missing "LabelsSize" in section "Plot"

## Next steps
1. Implementation of automatic identification of starting point
2. Implementation of window enlargement on stopping criteria
3. Adding configuration file for plots
4. Support >9 windows
5. Add an export to NetCDF or other formats
