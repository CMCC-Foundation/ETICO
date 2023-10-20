#!/usr/bin/env python3

class InvalidZonalDirectionError(Exception):
    def __init__(self, message="Invalid Zonal Direction detected!"):
        self.message = message
        super().__init__(self.message)