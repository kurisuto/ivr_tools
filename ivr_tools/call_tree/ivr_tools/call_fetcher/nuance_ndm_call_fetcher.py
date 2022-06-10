#!/usr/bin/env python3
import os
from os.path import join
import re

from .call_fetcher import CallFetcher


class NuanceNDMCallFetcher(CallFetcher):

    def __init__(self, start_directory):
        self.start_directory = start_directory

    def get_next_call_identifier(self):
        for root, dirs, files in os.walk(self.start_directory):
            for filename in files:
                pathname = os.path.join(root, filename)
                if (re.search("-LOG$", filename)):
                    yield(pathname)


    def get_call_record(self, call_identifier):
        with open(call_identifier, 'r') as inputfile:
            content = inputfile.read()
            return(content)
                
