#!/usr/bin/env python3
import yaml

from .node import Node


class CallHistory:

    def __init__(self):
        self.call_node = Node('call')
        pass
    
    def get_call_node(self):
        return(self.call_node)
    
    def dump(self):
        structure = self.call_node.prepare_to_serialize()
        print(yaml.dump(structure))
