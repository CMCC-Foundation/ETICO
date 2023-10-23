# EstuarIO_thalweg
A python software to identify the thalweg in a river

## Invoking the script

To invoke the script:

```
$ python customThalweg.py <BATHYMETRY_FILE> <CONFIG_FILE>
```

Please remember to check that settings in the config file are correct. See `sample.conf` for an example.

## Error codes

The script fails with an error code that should help the user to discover what's wrong:

1. Not enough parameters. You need to provide the bathymetry file and the configuration file
2. Incomplete configuration file. Missing "MaxSearchAlgo" in section "Algorithm"
3. Incomplete configuration file. Missing section "Algorithm"
4. Incomplete configuration file. Missing "WindowSize" in section "Algorithm"
5. Wrong setting in configuration file. "MaxSearchAlgo" can only be "Zonal" or "Classic" (no quotes)


## Next steps
1. Implementation of automatic identification of starting point
2. Implementation of window enlargement on stopping criteria
3. Adding configuration file for plots
4. Support >9 windows
5. Add an export to NetCDF or other formats
