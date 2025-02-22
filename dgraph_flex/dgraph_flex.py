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

# from dotenv import dotenv_values  # pip install python-dotenv
# import yaml # pip install pyyaml

"""



"""

__version_info__ = ('0', '1', '0')
__version__ = '.'.join(__version_info__)

version_history = \
"""
0.1.0 - initial version  
"""
    


class DgraphFlex:
    
    def __init__(self, **kwargs):
        
        # load self.config
        self.config = {}
        for key, value in kwargs.items():
            self.config[key] = value

        # load the graph description from the yaml file
        self.load_graph()
        
        pass


    def read_yaml(self, version=1.0):
        "read in the yaml config file"
        with open(self.yamlpath, 'r') as file:
            self.graph = yaml.safe_load(file)

        if self.graph['GENERAL']['version'] > version:
            print(f"Error: Supports up to {version}, this is version {self.cfg['GENERAL']['version']}")
            sys.exit(1)

        return self.graph
            
    def cmd(self, cmd):
        if cmd == 'plot':
            self.plot()
            
            
    
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