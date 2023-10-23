#!/usr/bin/env python3

class InvalidZonalDirectionError(Exception):
    def __init__(self, message="Invalid Zonal Direction detected!"):
        self.message = message
        super().__init__(self.message)
        
class UnsupportedMaxSearchAlgoError(Exception):
    def __init__(self, message="Unsupported max search algorithm requested! Use Zonal or Classic"):
        self.message = message
        super().__init__(self.message)

class IncompleteConfigFileError(Exception):
    def __init__(self, message="Check your config file!"):
        self.message = message
        super().__init__(self.message)