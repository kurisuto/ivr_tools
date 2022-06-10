#!/usr/bin/env python3
from copy import deepcopy
from datetime import datetime, timedelta
import random
from pprint import pprint

from ._node_artificial import ArtificialNode

class Node(ArtificialNode):

    def __init__(self, node_level, state_type=None):
        self.values = {}
        self.daughters = []

        if node_level not in {'call', 'state', 'step'}:
            raise ValueError(f"Invalid node level: '{node_level}'")

        if node_level == 'state':
            if state_type is None:
                raise ValueError("If node_level is 'state', state_type cannot be None.")
            if state_type not in {'dialog', 'prompt', 'database', 'decision'}:
                raise ValueError(f"Invalid state type: '{state_type}'")

        self.set_value('node_level', node_level)
        if node_level == 'state':
            self.set_value('state_type', state_type)



    def set_value(self, key, value):
        self.values[key] = value

    def get_value(self, key):
        return self.values[key]

    def increment_counter(self, key):
        self.values[key] += 1
    
    def key_exists(self, key):
        return key in self.values

    # TO-DO: The artificial node creator wasn't originally using this.
    # I should revise that code to use it, and possibly make append_daughter
    # a private method.
    def create_and_return_daughter(self, node_level, state_type=None):
        daughter = Node(node_level, state_type=state_type)
        self.append_daughter(daughter)
        return daughter
    
    def append_daughter(self, daughter):
        self.daughters.append(daughter)

    def get_daughters(self):
        for daughter in self.daughters:
            yield daughter

    def get_daughter_list(self):
        return self.daughters



    def dump_values(self):
        pprint(self.values)
        pprint(self.daughters)


    def prepare_to_serialize(self):
        values = deepcopy(self.values)

        # Convert datetimes to strings.  The reason we have to do this
        # is to prevent YAML from being too smart and printing duplicate
        # datetime objects as *id001, etc.
        for key, value in values.items():
            if isinstance(value, datetime):
                values[key] = str(value)

        daughters = []
        for daughter in self.daughters:
            daughter_serialized = daughter.prepare_to_serialize()
            daughters.append(daughter_serialized)

        record = {
            'values': values,
            'daughters': daughters
            }

        return record


    def study_other_fields(self):
        record = {}

        for member in self.__dict__:
            if member in {'values', 'daughters'}:
                continue

            value = self.__dict__[member]
            record[member] = value

        daughters = []
        for daughter in self.daughters:
            daughter_serialized = daughter.study_other_fields()
            daughters.append(daughter_serialized)
        record['daughters'] = daughters


        return record

