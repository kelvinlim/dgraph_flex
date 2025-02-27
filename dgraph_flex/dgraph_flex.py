#! /usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import os
import glob
import sys
import json
from pathlib import Path
import textwrap
from glob import glob
import yaml

from graphviz import Digraph
import matplotlib.pyplot as plt
# import networkx as nx
# import pandas as pd
# import numpy
# import seaborn as sns


# from dotenv import dotenv_values  # pip install python-dotenv
# import yaml # pip install pyyaml

"""



"""

__version_info__ = ('0', '1', '2')
__version__ = '.'.join(__version_info__)

version_history = \
"""
0.1.2 - default resolution of 300
0.1.1 - added GENERAL|gvinit to set graph attributes
0.1.0 - initial version  
"""
    


class DgraphFlex:
    
    def __init__(self, **kwargs):
        
        # initialize the graph
        self.graph = {}
        

        # load self.config
        self.config = {}
        for key, value in kwargs.items():
            self.config[key] = value

        # load the graph description from the yaml file
        # self.load_graph()
        
        pass


    def read_yaml(self, yamlpath, version=1.0):
        "read in the yaml config file"
        with open(yamlpath, 'r') as file:
            self.graph = yaml.safe_load(file)

        if self.graph['GENERAL']['version'] > version:
            print(f"Error: Supports up to {version}, this is version {self.graph['GENERAL']['version']}")
            sys.exit(1)

        return self.graph
            
    def cmd(self, cmd):
        if cmd == 'plot':
            self.read_yaml(self.config['yamlpath'])
            self.load_graph()
            
    def load_graph(self, graph=None, index=0, plot_format='png',plot_name='dgflex'):
        """
        Load a graph definition from a yaml file into a graphviz object
        
        
        set the edge attributes starting from the first character to the third character
        
        --> == These indicate a direct causal influence. For example, A --> B means that variable A directly causes variable B
        o-> == Indicates that either A causes B, or there's an unobserved confounder affecting both A and B, or both.
        <-> == Indicates the presence of an unobserved confounder affecting both variables.
        --- == These represent a relationship between variables, but the direction of causality is uncertain.
        o-o == Indicates that either A causes B, B causes A, or there's an unobserved confounder, or any combination of these.
            
        """    
        
        
        # create the graph object
        self.dot = Digraph( format=plot_format)
        
        # set default resolution of 600 
        self.dot.format = 'png'   
        self.dot.attr(dpi='300') 
        
        # if GENERAL|gvinit is present, set the graph attributes
        if self.graph.get('GENERAL', False):
            if self.graph['GENERAL'].get('gvinit', False):
                # check for nodes
                if 'nodes' in self.graph['GENERAL']['gvinit']:
                    self.dot.node_attr.update(self.graph['GENERAL']['gvinit']['nodes'])
                pass
                # for key, value in self.graph['GENERAL']['gvinit'].items():
                #     self.dot.attr(key, value)
                
                    
        # set the node attributes
        #self.dot.attr('node', shape='oval')
        
        if graph is None:
            # use the graph from the object
            graph = self.graph
            
        # start with the edges in self.graph
        for edge in graph['GRAPHS'][index]['edges']:

            edge_attr = {
                "dir": "both",
                "label": "",
            }
            
            # set default values for arrowhead and arrowtail
            arrowhead = 'normal'
            arrowtail = 'none'
            
            # set the arrowhead and arrowtail based on the edge type
            if edge['edge_type'] == 'o->':
                arrowtail='odot'
            elif edge['edge_type'] == 'o-o':
                arrowtail='odot'
                arrowhead='odot'
                
            # create info structure to ease access to edge information
            label = ''
            color = 'black'
            
            if edge.get('properties',False):
                if edge['properties'].get('strength', None) is not None:
                    label = f"{edge['properties']['strength']}"
                # check for pvalue
                if edge['properties'].get('pvalue', None) is not None:
                    label += f"\n{edge['properties']['pvalue']}"
                
            if edge.get('gvprops', False):
                # set color    
                if edge['gvprops'].get('color', None) is not None:
                    color = edge['gvprops']['color']
                    
            # create the edge object
            self.dot.edge(  edge['source'], edge['target'],
                            arrowtail=arrowtail,
                            arrowhead=arrowhead,
                            dir='both',
                            label=label,
                            color=color,)
                            #**edge_attr)
                                    

            pass
            
        # render
        
        print(self.dot.source)
        
        # save gv source
        self.gv_source = self.dot.source
        
        self.dot.format = plot_format
        self.dot.render(filename = plot_name,
                        format=plot_format,
                        
                        )
        pass
    
    def modify_existing_edge(self, dot, from_node, to_node, **kwargs):
        """Modifies the attributes of an existing edge in a Graphviz graph.

        Args:
            dot: The Graphviz Graph object.
            from_node: The name of the starting node of the edge.
            to_node: The name of the ending node of the edge.
            **kwargs: The attributes to modify (e.g., color='blue', style='dotted').
        """

        for edge in dot.body:
            if edge.tail[0] == from_node and edge.head[0] == to_node:
                for key, value in kwargs.items():
                    edge.attr[key] = value
                return  # Exit after modifying the edge

        print(f"Edge from '{from_node}' to '{to_node}' not found.")
            
if __name__ == "__main__":
    
    # provide a description of the program with format control
    description = textwrap.dedent('''\
    
    Class to support directed graph display in support of causal structure analysis.
    
 
    ''')
    
    parser = argparse.ArgumentParser(
        description=description, formatter_class=argparse.RawTextHelpFormatter)

    # handle a single file on command line argument
    parser.add_argument('file',  type=str,  help='input file')
    

        
    parser.add_argument("--cmd", type = str,
                    help="cmd - [plot], default plot",
                    default = 'plot')
    
    parser.add_argument("-H", "--history", action="store_true", help="Show program history")
     
    # parser.add_argument("--quiet", help="Don't output results to console, default false",
    #                     default=False, action = "store_true")  
    
    parser.add_argument("--verbose", type=int, help="verbose level default 2",
                         default=2) 
        
    parser.add_argument('-V', '--version', action='version', version=f'%(prog)s {__version__}')

    args = parser.parse_args()
            
    if args.history:
        print(f"{os.path.basename(__file__) } Version: {__version__}")
        print(version_history)
        exit(0)

    obj = DgraphFlex(  yamlpath = args.file, verbose = args.verbose)

    obj.cmd('plot')