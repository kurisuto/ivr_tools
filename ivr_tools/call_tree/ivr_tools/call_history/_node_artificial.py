#!/usr/bin/env python3
import random
from datetime import datetime, timedelta

# This class adds to the Node class, adding some methods and
# functionality for use when we're randomly generating artificial
# calls from an imaginary application.


class ArtificialNode:

    def __init__(self, node_level, state_type=None):
        return
        
        # super().__init__(node_level, state_type=state_type)

        if node_level == 'state':
            self.set_value('state_outcome', '')
            self.set_value('state_value', '')
        if node_level == 'step':
            self.set_value('step_outcome', '')
            self.set_value('step_value', '')

        
    def set_value_from_generator(self, key, value_generator):
        value = value_generator.generate_value()
        self.values[key] = value

        
    def compute_timestamps(self, start_time):
        self.set_value('START_TIME', start_time)  # Must be set before we compute END_TIME

        end_time = self._compute_endtime()        
        self.set_value('END_TIME', end_time)

        slop_milliseconds = random.randint(0, 20)
        slop_timedelta = timedelta(milliseconds=slop_milliseconds)
        return end_time + slop_timedelta


    # This could be coded more succinctly, but I covered all the bases
    # so that this also serves as an integrity check on the node_level
    # and state_type fields.
    def _compute_endtime(self):
        node_level = self.get_value('node_level')
        if node_level == 'state':
            state_type = self.get_value('state_type')

        if node_level == 'call':
            return self._compute_times_from_daughters()
        elif node_level == 'state':
            if state_type == 'dialog':
                return self._compute_times_from_daughters()
            elif state_type in {'prompt', 'database', 'decision'}:
                return self._compute_times_from_duration()
        elif node_level == 'step':
            return self._compute_times_from_duration()

        raise Exception('Internal error: invalid node_level/state_type')

    
    def _compute_times_from_daughters(self):
        start_time = self.get_value('START_TIME')

        last_daughter_timestamp = start_time
        for daughter in self.get_daughters():
            last_daughter_timestamp = daughter.compute_timestamps(last_daughter_timestamp)

        return last_daughter_timestamp


    def _compute_times_from_duration(self):
        start_time = self.get_value('START_TIME')
        duration = self.get_value('DURATION')
        duration_timedelta = timedelta(milliseconds=duration)
        return start_time + duration_timedelta
