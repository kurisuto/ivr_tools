#!/usr/bin/env python3
import re
import inspect

from .call_parser import CallParser

from ..call_history.call_history import CallHistory


# IMPORTANT:
# Create a new instance of NuanceNDMCallParser for each call you
# parse.  The code uses instance variables to maintain the state of
# the parse.  So, for example, you can't use a single
# NuanceNDMCallParser instance to concurrently process two call
# records.


class NuanceNDMCallParser(CallParser):


    

    def __init__(self):

        # Set up a dispatch table for handling events.
        # We use object introspection.
        # If a method in this class starts with "event_", 
        self.dispatch_table = {}        
        for member in inspect.getmembers(self, predicate=inspect.ismethod):
            method_name = member[0]
            if not method_name.startswith("event_"):
                continue
            event_name = re.sub("^event_", "", method_name)
            self.dispatch_table[event_name] = member[1]


    # --------------------------------------------------------------

    # INITIAL CALL PROCESSING
    # Take the file blob and turn it into an array of event dictionaries.

    
    # ----------------
    
    # With very few exceptions, each key can exist in an
    # event only once.  The known exceptions are:
    # SWIstst/GRNM 
    # SWIstst/CONFSLOT 
    # SWItyst/AVOID 
    # SWItyst/SLOT 

    # We normally store a value as a scalar.  If the key
    # exists more than once in event, though, then the
    # value is a list of scalars.


    def line_event_to_dict(self, event_line):
        event_dict = {}
        fields = event_line.split("|")

        for field in fields:
            # The value is allowed to contain =, so we have to
            # split the key from the value in a special way.
            match = re.search("^([^=]*)=(.*)$", field)

            if not match:
                print(event_line)
            
            key = match.group(1)
            value = match.group(2)

            # If we haven't seen this key before, store the value as a scalar.
            if key not in event_dict:
                event_dict[key] = value
                continue

            # If we've seen this key just once before, convert the field into a list.
            previous_value = event_dict[key]
            if isinstance(previous_value, list):
                event_dict[key].append(value)
                continue

            # If we've seen it more than once before, then it's already a list.
            # Append the next value to the end of the list.
            new_list = [previous_value]
            new_list.append(value)
            event_dict[key] = new_list

        return(event_dict)
    
    
    def call_record_to_event_dict_list(self, call_record):
        call_record = call_record.strip()
        event_lines = call_record.split("\n")

        event_list = []
        for line in event_lines:
            event_dict = self.line_event_to_dict(line)
            event_list.append(event_dict)

        return event_list

    
    def event_list_to_call_record(self, event_list):
    
        self.call_history = CallHistory()
        self.call_node = self.call_history.get_call_node()
        

        for event in event_list:
            event_type = event['EVNT']
            if event_type in self.dispatch_table:
                self.dispatch_table[event_type](event)
            else:
                if event_type not in ('UIndst', 'UIndnd'):
                    print(event_type)
        
        return self.call_history

    
    def parse_call(self, call_record):
        event_list = self.call_record_to_event_dict_list(call_record)
        call_record = self.event_list_to_call_record(event_list)
        return call_record


    
    
    # ----------------------------------------------------

    def map_SWIdbrx_RSLT(self, value):
        if value == 'SUCC':
            return 'success'
        if value == 'FAIL':
            return 'failure'
        if value == 'UNKN':
            return 'unknown'
    

    # ----------------------------------------------------

    
    def copy_field_to_node(self, event_field_name, node_field_name, event, node):
        if event_field_name not in event:
            return
        value = event[event_field_name]
        node.set_value(node_field_name, value)

    def map_field_to_node(self, event_field_name, node_field_name, event, node, map_function):
        if event_field_name not in event:
            return
        value = event[event_field_name]
        value = map_function(value)
        node.set_value(node_field_name, value)
        
    # TO-DO: Time format conversion
    def copy_start_time_to_node(self, event, node):
        value = event['TIME']
        node.set_value('START_TIME', value)
        
    # TO-DO: Time format conversion
    def copy_end_time_to_node(self, event, node):
        value = event['TIME']
        node.set_value('END_TIME', value)

    def start_state(self, event, state_type, state_name_field):
        self.current_state = self.call_node.create_and_return_daughter('state', state_type)
        self.copy_start_time_to_node(event, self.current_state)
        self.copy_field_to_node(state_name_field, 'STATE_NAME', event, self.current_state)
        
    def end_state(self, event):
        self.copy_end_time_to_node(event, self.current_state)


    # ----------------------------------------------------
        
        
    def event_SWIclst(self, event):
        self.copy_start_time_to_node(event, self.call_node)
        self.copy_field_to_node('ANI', 'ANI', event, self.call_node)
        self.copy_field_to_node('DNIS', 'DNIS', event, self.call_node)


    def event_SWIsvst(self, event):
        self.copy_field_to_node('SVNM', 'SERVICE_NAME', event, self.call_node)

    def event_SWIunid(self, event):
        self.copy_field_to_node('UNID', 'CALL_ID', event, self.call_node)

    def event_SWIlang(self, event):
        self.copy_field_to_node('LANG', 'LANGUAGE', event, self.call_node)
        
        
    def event_SWIclnd(self, event):
        self.copy_end_time_to_node(event, self.call_node)

    def event_SWIdmst(self, event):
        self.start_state(event, 'dialog', 'DMNM')
                
    def event_SWIdmnd(self, event):
        self.end_state(event)        

    def event_SWIdbtx(self, event):
        self.start_state(event, 'database', 'NAME')
        
    def event_SWIdbrx(self, event):
        self.map_field_to_node('RSLT', 'STATE_OUTCOME', event, self.current_state, self.map_SWIdbrx_RSLT)
        self.end_state(event)

    def event_SWIppst(self, event):
        self.start_state(event, 'prompt', 'PPNM')
                
    def event_SWIppnd(self, event):
        self.end_state(event)

    def event_SWIdsst(self, event):
        self.start_state(event, 'decision', 'DSNM')

    def event_SWIdsnd(self, event):
        self.end_state(event)



    def event_SWIphst(self, event):
        pass
    def event_SWIphnd(self, event):
        pass
    def event_SWIstst(self, event):
        pass
    def event_SWIstnd(self, event):
        pass
    def event_SWIapps(self, event):
        pass
    def event_SWIprst(self, event):
        pass

        
    def event_SWIcllr(self, event):
        pass
    def event_SWIendcall(self, event):
        pass
    def event_SWIsurvey(self, event):
        pass
    def event_SWItrfr(self, event):
        pass
    def event_SWItynd(self, event):
        pass
    def event_SWItyst(self, event):
        pass
    def event_modulend(self, event):
        pass
    def event_modulest(self, event):
        pass
        
        
    # ----------------------------------------------------

    

    # TO-DO (maybe):
    # Print out all the events and fields I'm not using
    # There needs to be a list of things I'm ignoring on purpose, e.g. UIndst


# SWIphst
# SWIphnd
#     
# SWItyst
# SWItynd
# 
# SWIstst
# SWIstnd
# 
# SWIapps
# 
# SWIprst
# 
# SWIsvst
# SWIunid
# SWIlang
# SWIcllr
# SWIendcall




