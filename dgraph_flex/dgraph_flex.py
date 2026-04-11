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

__version_info__ = ('0', '1', '12')
__version__ = '.'.join(__version_info__)

version_history = \
"""
0.1.12 - add Excalidraw integration: to_excalidraw(), show_excalidraw(), save_excalidraw()
        Interactive graph visualization in Jupyter notebooks with no new dependencies.
0.1.11 - in modify_existing_edge, if edge doesn't exist skip instead of raising an error.
        This is to support using a subset of edges in graph (e.g. ancestors) but
        still use the full graph SEM results to modify the edges.
0.1.10 - add directed_only boolean to load_image, save_image, show_image to only load directed edges
0.1.9 - change the handling of arguments for save_graph
0.1.8 - add exclude option to add_edges method to exclude certain edge types
        add support for --- edge in load_graph method
0.1.7 - add add_edges method to add multiple edges at once
0.1.6 - fixed bug with adding the <-> edge type
0.1.5 - change modify_existing_edge to use self.dot object 
0.1.4 - add show_graph method to display graph in jupyter notebook

from dgraph_flex import DgraphFlex

obj = DgraphFlex()
# add edges to graph object
obj.add_edge('A', '-->', 'B', color='green', strength=-0.5, pvalue=0.01)
obj.add_edge('B', '-->', 'C', color='red', strength=-.5, pvalue=0.001)
obj.add_edge('C', 'o->', 'E', color='green', strength=0.5, pvalue=0.005)
obj.add_edge('D', 'o->', 'B', color='purple')
# load into graphviz object and render to window
obj.show_graph()

0.1.3 - have __init__ create the graph dict, new format for graph structure

Example of the new format:
GENERAL:
  version: 2.0
  framework: dgraph_flex
  gvinit:  # global graphviz initialization
    nodes:
      shape: oval
      color: black

GRAPH:
  edges: # Use indentation for the dictionary under 'edges'
    "A --> B": # Key for the first edge
      properties: # Indent for the 'properties' dictionary
        strength: 0.5
        pvalue: 0.01
      gvprops: # Indent for the 'gvprops' dictionary
        color: green
    "B --> C": # Key for the second edge
      properties: # Indent for 'properties'
        strength: -0.5
        pvalue: 0.001
      gvprops: # Indent for 'gvprops'
        color: red
    "C o-> E": # Key for the third edge
      properties: # Indent for 'properties'
        strength: 0.5
        pvalue: 0.0005
      gvprops: # Indent for 'gvprops'
        color: green
    "B o-o D": # Key for the fourth edge
      properties: # Indent for 'properties'
        strength: 0.5
        pvalue: 0.0005
      gvprops: # Indent for 'gvprops'
        color: black

Example of how to use the object:

from dgraph_flex import DgraphFlex

# create the graph object
obj = DgraphFlex(verbose=args.verbose)
# add edges to graph object
obj.add_edge('A', '-->', 'B', color='green', strength=-0.5, pvalue=0.01)
obj.add_edge('B', '-->', 'C', color='red', strength=-.5, pvalue=0.001)
obj.add_edge('C', 'o->', 'E', color='green', strength=0.5, pvalue=0.005)
obj.add_edge('B', 'o-o', 'D')
# load into graphviz object
obj.load_graph()
# save the graph to a file
obj.save_graph(plot_format='png', plot_name='dgflex2')


0.1.2 - default resolution of 300
0.1.1 - added GENERAL|gvinit to set graph attributes
0.1.0 - initial version  
"""
    


class DgraphFlex:
    
    def __init__(self, **kwargs):
        
        # initialize the graph
        self.graph = {
            "GENERAL": {
                "version": 2.0,
                "framework": "dgraph_flex",
                "gvinit": {
                    "nodes": {
                        "shape": "oval",
                        "color": "black",
                    },
                    # "edges": {
                    #     "color": "black",
                    #     "style": "solid",
                    # }
                }
            },
            "GRAPH": {
                "edges": {
                }
            }   
        }
        

        # load self.config
        self.config = {}
        for key, value in kwargs.items():
            self.config[key] = value

        # load the graph description from the yaml file
        # self.load_graph()
        
        # expose the edges 
        self.edges = self.graph['GRAPH']['edges']

        pass


    def read_yaml(self, yamlpath, version=2.0):
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
            self.load_graph(res=100)
            self.save_graph(plot_format='png', plot_name='dgflex')
            
    def load_graph(self, graph=None, plot_format='png',res=300, directed_only=False):
        """
        Load a graph definition from a yaml file into a graphviz object
        
        
        set the edge attributes starting from the first character to the third character
        
        --> == These indicate a direct causal influence. For example, A --> B means that variable A directly causes variable B
        o-> == Indicates that either A causes B, or there's an unobserved confounder affecting both A and B, or both.
        <-> == Indicates the presence of an unobserved confounder affecting both variables.
        --- == These represent a relationship between variables, but the direction of causality is uncertain.
        o-o == Indicates that either A causes B, B causes A, or there's an unobserved confounder, or any combination of these.
        
        args:
            graph: The graph object to load. If None, uses the graph from the object.
            plot_format: The format to save the graph in (e.g., 'png', 'pdf').
            res: The resolution of the plot.
            directed_only: if True only load directed_edges e.g. -->, o->
        """    
        
        
        # create the graph object
        self.dot = Digraph( format=plot_format)
        
        # set default resolution of 600 
        self.dot.format = plot_format   
        self.dot.attr(dpi=str(res)) 
        
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
            
        edges = graph['GRAPH']['edges']
        # start with the edges in self.graph
        for name, edge in edges.items():
            
            # extract the source, edge_type and target from the key
            source, edge_type, target = name.split(' ')
            
            # check if directed_only
            if directed_only and edge_type not in ['-->', 'o->']:
                continue
            
            # edge is a tuple of (key, value)
            edge_attr = {
                "dir": "both",
                "label": "",
            }
            
            # set default values for arrowhead and arrowtail
            arrowhead = 'normal'
            arrowtail = 'none'
            

            # set the arrowhead and arrowtail based on the edge type
            if edge_type == 'o->':
                arrowtail='odot'
            elif edge_type == 'o-o':
                arrowtail='odot'
                arrowhead='odot'
            elif edge_type == '<->':
                arrowtail='normal'
            elif edge_type == '---':
                arrowhead='none'
                arrowtail='none'

                
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
            self.dot.edge(  source, target,
                            arrowtail=arrowtail,
                            arrowhead=arrowhead,
                            dir='both',
                            label=label,
                            color=color,)
                            #**edge_attr)
                                    

            pass
            
        # render
        
        # print(self.dot.source)
    
    def show_graph(self,format='png',res=72, directed_only=False):
        """
        Display the graph in a Jupyter notebook.
        """
        # Set the desired output format for Jupyter to PNG
        import graphviz
        # Set the format to PNG for Jupyter
        graphviz.set_jupyter_format(format)
        # load the graph into the graphviz object
        self.load_graph(res=res,directed_only=directed_only)
        return self.dot
        

    def to_excalidraw(self, directed_only=False):
        """
        Convert the graph to Excalidraw JSON format.

        Returns a dict compatible with Excalidraw's initialData format,
        containing ellipse elements for nodes and arrow elements for edges.

        Args:
            directed_only: if True only include directed edges (-->, o->)

        Returns:
            dict with 'elements' list in Excalidraw format
        """
        import math
        import random

        elements = []
        edges = self.graph['GRAPH']['edges']

        # extract unique nodes from edges
        nodes = set()
        for name in edges:
            source, edge_type, target = name.split(' ')
            if directed_only and edge_type not in ['-->', 'o->']:
                continue
            nodes.add(source)
            nodes.add(target)
        nodes = sorted(nodes)

        if not nodes:
            return {"type": "excalidraw", "version": 2, "elements": []}

        # layout nodes in a circle
        node_width = 120
        node_height = 60
        radius = max(150, len(nodes) * 60)
        center_x = 400
        center_y = 400

        node_positions = {}
        node_ids = {}

        for i, node_name in enumerate(nodes):
            angle = (2 * math.pi * i / len(nodes)) - math.pi / 2
            x = center_x + radius * math.cos(angle) - node_width / 2
            y = center_y + radius * math.sin(angle) - node_height / 2
            node_positions[node_name] = (x, y)

            node_id = f"node-{node_name}"
            text_id = f"text-{node_name}"
            node_ids[node_name] = node_id
            seed = random.randint(1, 2**31)

            # create ellipse element for node
            elements.append({
                "type": "ellipse",
                "id": node_id,
                "x": x,
                "y": y,
                "width": node_width,
                "height": node_height,
                "strokeColor": "#1e1e1e",
                "backgroundColor": "transparent",
                "fillStyle": "solid",
                "strokeWidth": 2,
                "roughness": 1,
                "opacity": 100,
                "angle": 0,
                "seed": seed,
                "version": 1,
                "isDeleted": False,
                "boundElements": [{"type": "text", "id": text_id}],
                "groupIds": [],
                "frameId": None,
                "roundness": {"type": 2},
            })

            # create bound text label for node
            elements.append({
                "type": "text",
                "id": text_id,
                "x": x + node_width / 2 - len(node_name) * 5,
                "y": y + node_height / 2 - 10,
                "width": len(node_name) * 10,
                "height": 20,
                "text": node_name,
                "fontSize": 20,
                "fontFamily": 1,
                "textAlign": "center",
                "verticalAlign": "middle",
                "strokeColor": "#1e1e1e",
                "backgroundColor": "transparent",
                "fillStyle": "solid",
                "strokeWidth": 2,
                "roughness": 1,
                "opacity": 100,
                "angle": 0,
                "seed": seed + 1,
                "version": 1,
                "isDeleted": False,
                "containerId": node_id,
                "originalText": node_name,
                "boundElements": None,
                "groupIds": [],
                "frameId": None,
            })

        # map edge types to excalidraw arrowheads
        arrowhead_map = {
            '-->': (None, "arrow"),
            'o->': ("dot", "arrow"),
            '<->': ("arrow", "arrow"),
            '---': (None, None),
            'o-o': ("dot", "dot"),
        }

        # create arrow elements for edges
        for name, edge in edges.items():
            source, edge_type, target = name.split(' ')

            if directed_only and edge_type not in ['-->', 'o->']:
                continue

            src_x, src_y = node_positions[source]
            tar_x, tar_y = node_positions[target]

            # arrow starts/ends at center of nodes
            start_cx = src_x + node_width / 2
            start_cy = src_y + node_height / 2
            end_cx = tar_x + node_width / 2
            end_cy = tar_y + node_height / 2

            dx = end_cx - start_cx
            dy = end_cy - start_cy

            # get color from edge properties
            color = "#1e1e1e"
            if edge.get('gvprops') and edge['gvprops'].get('color'):
                gv_color = edge['gvprops']['color']
                color_map = {
                    'red': '#e03131',
                    'green': '#2f9e44',
                    'blue': '#1971c2',
                    'purple': '#9c36b5',
                    'orange': '#e8590c',
                    'black': '#1e1e1e',
                }
                color = color_map.get(gv_color, gv_color)

            start_arrowhead, end_arrowhead = arrowhead_map.get(edge_type, (None, "arrow"))

            # build label from properties
            label = ''
            if edge.get('properties'):
                parts = []
                if edge['properties'].get('strength') is not None:
                    parts.append(str(edge['properties']['strength']))
                if edge['properties'].get('pvalue') is not None:
                    parts.append(str(edge['properties']['pvalue']))
                label = '\n'.join(parts)

            arrow_id = f"arrow-{source}-{edge_type}-{target}"
            seed = random.randint(1, 2**31)

            arrow_element = {
                "type": "arrow",
                "id": arrow_id,
                "x": start_cx,
                "y": start_cy,
                "width": abs(dx),
                "height": abs(dy),
                "strokeColor": color,
                "backgroundColor": "transparent",
                "fillStyle": "solid",
                "strokeWidth": 2,
                "roughness": 1,
                "opacity": 100,
                "angle": 0,
                "seed": seed,
                "version": 1,
                "isDeleted": False,
                "points": [[0, 0], [dx, dy]],
                "startBinding": {
                    "elementId": node_ids[source],
                    "focus": 0,
                    "gap": 5,
                },
                "endBinding": {
                    "elementId": node_ids[target],
                    "focus": 0,
                    "gap": 5,
                },
                "startArrowhead": start_arrowhead,
                "endArrowhead": end_arrowhead,
                "boundElements": [],
                "groupIds": [],
                "frameId": None,
                "roundness": {"type": 2},
            }

            # add label as bound text if present
            if label:
                label_id = f"label-{arrow_id}"
                arrow_element["boundElements"] = [{"type": "text", "id": label_id}]
                elements.append(arrow_element)

                # label text positioned at midpoint of arrow
                mid_x = start_cx + dx / 2
                mid_y = start_cy + dy / 2
                elements.append({
                    "type": "text",
                    "id": label_id,
                    "x": mid_x - 30,
                    "y": mid_y - 15,
                    "width": 60,
                    "height": 30,
                    "text": label,
                    "fontSize": 14,
                    "fontFamily": 1,
                    "textAlign": "center",
                    "verticalAlign": "middle",
                    "strokeColor": color,
                    "backgroundColor": "transparent",
                    "fillStyle": "solid",
                    "strokeWidth": 1,
                    "roughness": 1,
                    "opacity": 100,
                    "angle": 0,
                    "seed": seed + 1,
                    "version": 1,
                    "isDeleted": False,
                    "containerId": arrow_id,
                    "originalText": label,
                    "boundElements": None,
                    "groupIds": [],
                    "frameId": None,
                })
            else:
                elements.append(arrow_element)

        return {
            "type": "excalidraw",
            "version": 2,
            "elements": elements,
        }

    def show_excalidraw(self, width="100%", height="500px",
                        view_mode=False, directed_only=False):
        """
        Display the graph as an interactive SVG canvas in a Jupyter notebook.

        Renders the graph inline using an srcdoc iframe with a self-contained
        SVG canvas (no external CDN dependencies). The canvas supports pan,
        zoom (scroll wheel), and draggable nodes unless view_mode is True.

        Args:
            width: Width of the iframe (CSS value). Defaults to "100%".
            height: Height of the iframe (CSS value). Defaults to "500px".
            view_mode: If True, render in read-only mode. Defaults to False.
            directed_only: If True, only include directed edges (-->, o->).

        Returns:
            IPython.display.HTML object for inline notebook rendering.
        """
        import math
        import uuid
        from IPython.display import display, HTML

        excalidraw_data = self.to_excalidraw(directed_only=directed_only)
        elements = excalidraw_data.get("elements", [])

        # separate nodes, node labels, arrows, and arrow labels
        nodes = {}       # id -> element
        node_texts = {}  # containerId -> element
        arrows = []
        arrow_labels = {}  # containerId -> element

        for el in elements:
            if el["type"] == "ellipse":
                nodes[el["id"]] = el
            elif el["type"] == "text" and el.get("containerId", "").startswith("node-"):
                node_texts[el["containerId"]] = el
            elif el["type"] == "arrow":
                arrows.append(el)
            elif el["type"] == "text" and el.get("containerId", "").startswith("arrow-"):
                arrow_labels[el["containerId"]] = el

        # build SVG elements
        svg_defs = """
    <defs>
      <marker id="arrowhead" markerWidth="10" markerHeight="7"
              refX="10" refY="3.5" orient="auto" fill="context-stroke">
        <polygon points="0 0, 10 3.5, 0 7" />
      </marker>
      <marker id="dot" markerWidth="8" markerHeight="8"
              refX="4" refY="4" orient="auto" fill="context-stroke">
        <circle cx="4" cy="4" r="3" />
      </marker>
    </defs>"""

        svg_nodes = []
        for node_id, node in nodes.items():
            cx = node["x"] + node["width"] / 2
            cy = node["y"] + node["height"] / 2
            rx = node["width"] / 2
            ry = node["height"] / 2
            label = node_texts.get(node_id, {}).get("text", "")
            svg_nodes.append(
                f'<g class="node" data-id="{node_id}">'
                f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" '
                f'stroke="#1e1e1e" stroke-width="2" fill="white" />'
                f'<text x="{cx}" y="{cy}" text-anchor="middle" '
                f'dominant-baseline="central" font-size="20" '
                f'font-family="sans-serif" fill="#1e1e1e">{label}</text>'
                f'</g>'
            )

        svg_edges = []
        for arrow in arrows:
            src_id = arrow.get("startBinding", {}).get("elementId")
            tgt_id = arrow.get("endBinding", {}).get("elementId")
            if not src_id or not tgt_id or src_id not in nodes or tgt_id not in nodes:
                continue

            src = nodes[src_id]
            tgt = nodes[tgt_id]
            src_cx = src["x"] + src["width"] / 2
            src_cy = src["y"] + src["height"] / 2
            tgt_cx = tgt["x"] + tgt["width"] / 2
            tgt_cy = tgt["y"] + tgt["height"] / 2

            # compute intersection with ellipse boundary
            def ellipse_border(cx, cy, rx, ry, target_x, target_y):
                dx = target_x - cx
                dy = target_y - cy
                if dx == 0 and dy == 0:
                    return cx + rx, cy
                angle = math.atan2(dy, dx)
                return cx + rx * math.cos(angle), cy + ry * math.sin(angle)

            src_rx = src["width"] / 2
            src_ry = src["height"] / 2
            tgt_rx = tgt["width"] / 2
            tgt_ry = tgt["height"] / 2

            x1, y1 = ellipse_border(src_cx, src_cy, src_rx, src_ry, tgt_cx, tgt_cy)
            x2, y2 = ellipse_border(tgt_cx, tgt_cy, tgt_rx, tgt_ry, src_cx, src_cy)

            color = arrow.get("strokeColor", "#1e1e1e")
            start_ah = arrow.get("startArrowhead")
            end_ah = arrow.get("endArrowhead")

            marker_start = ""
            if start_ah == "arrow":
                marker_start = ' marker-start="url(#arrowhead)"'
            elif start_ah == "dot":
                marker_start = ' marker-start="url(#dot)"'

            marker_end = ""
            if end_ah == "arrow":
                marker_end = ' marker-end="url(#arrowhead)"'
            elif end_ah == "dot":
                marker_end = ' marker-end="url(#dot)"'

            svg_edges.append(
                f'<line class="edge" data-src="{src_id}" data-tgt="{tgt_id}" '
                f'x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                f'stroke="{color}" stroke-width="2"'
                f'{marker_start}{marker_end} />'
            )

            # add label at midpoint
            label_el = arrow_labels.get(arrow["id"])
            if label_el:
                mid_x = (x1 + x2) / 2
                mid_y = (y1 + y2) / 2
                label_lines = label_el["text"].split('\n')
                text_els = []
                for i, line in enumerate(label_lines):
                    dy_offset = (i - (len(label_lines) - 1) / 2) * 16
                    text_els.append(
                        f'<text class="edge-label" data-src="{src_id}" data-tgt="{tgt_id}" '
                        f'x="{mid_x:.1f}" y="{mid_y + dy_offset:.1f}" '
                        f'text-anchor="middle" dominant-baseline="central" '
                        f'font-size="14" font-family="sans-serif" fill="{color}">'
                        f'{line}</text>'
                    )
                svg_edges.extend(text_els)

        nodes_svg = "\n    ".join(svg_nodes)
        edges_svg = "\n    ".join(svg_edges)
        view_mode_js = "true" if view_mode else "false"
        uid = uuid.uuid4().hex[:8]

        html_content = f"""
<div id="container-{uid}" style="width: {width}; height: {height};
     border: 1px solid #e0e0e0; border-radius: 4px; overflow: hidden;
     position: relative; background: #fff;">
  <svg id="canvas-{uid}" width="100%" height="100%"
       xmlns="http://www.w3.org/2000/svg"
       style="display: block;">
    {svg_defs}
    <g id="panZoom-{uid}">
      {edges_svg}
      {nodes_svg}
    </g>
  </svg>
</div>
<style>
  #container-{uid} .node {{ cursor: {"default" if view_mode else "grab"}; }}
  #container-{uid} .node:active {{ cursor: {"default" if view_mode else "grabbing"}; }}
</style>
<script>
(function() {{
  const svg = document.getElementById('canvas-{uid}');
  const g = document.getElementById('panZoom-{uid}');
  const viewMode = {view_mode_js};
  let pan = {{x: 0, y: 0}};
  let zoom = 1;
  let isPanning = false;
  let panStart = {{x: 0, y: 0}};
  let dragNode = null;
  let dragOffset = {{x: 0, y: 0}};

  function updateTransform() {{
    g.setAttribute('transform', 'translate(' + pan.x + ',' + pan.y + ') scale(' + zoom + ')');
  }}

  function svgPoint(e) {{
    const rect = svg.getBoundingClientRect();
    return {{ x: (e.clientX - rect.left - pan.x) / zoom,
              y: (e.clientY - rect.top - pan.y) / zoom }};
  }}

  svg.addEventListener('wheel', function(e) {{
    e.preventDefault();
    const rect = svg.getBoundingClientRect();
    const factor = e.deltaY < 0 ? 1.1 : 0.9;
    const px = e.clientX - rect.left;
    const py = e.clientY - rect.top;
    pan.x = px - (px - pan.x) * factor;
    pan.y = py - (py - pan.y) * factor;
    zoom *= factor;
    updateTransform();
  }});

  svg.addEventListener('mousedown', function(e) {{
    if (!viewMode && e.target.closest('.node')) {{
      const nodeG = e.target.closest('.node');
      dragNode = nodeG;
      const ellipse = nodeG.querySelector('ellipse');
      const cx = parseFloat(ellipse.getAttribute('cx'));
      const cy = parseFloat(ellipse.getAttribute('cy'));
      const pt = svgPoint(e);
      dragOffset.x = pt.x - cx;
      dragOffset.y = pt.y - cy;
      e.preventDefault();
      return;
    }}
    isPanning = true;
    panStart.x = e.clientX - pan.x;
    panStart.y = e.clientY - pan.y;
    e.preventDefault();
  }});

  svg.addEventListener('mousemove', function(e) {{
    if (dragNode) {{
      const pt = svgPoint(e);
      const newCx = pt.x - dragOffset.x;
      const newCy = pt.y - dragOffset.y;
      const ellipse = dragNode.querySelector('ellipse');
      ellipse.setAttribute('cx', newCx);
      ellipse.setAttribute('cy', newCy);
      const text = dragNode.querySelector('text');
      text.setAttribute('x', newCx);
      text.setAttribute('y', newCy);
      const nodeId = dragNode.dataset.id;
      g.querySelectorAll('.edge, .edge-label').forEach(function(el) {{
        if (el.dataset.src === nodeId || el.dataset.tgt === nodeId) {{
          const srcNode = g.querySelector('[data-id="' + el.dataset.src + '"] ellipse');
          const tgtNode = g.querySelector('[data-id="' + el.dataset.tgt + '"] ellipse');
          if (!srcNode || !tgtNode) return;
          const scx = parseFloat(srcNode.getAttribute('cx'));
          const scy = parseFloat(srcNode.getAttribute('cy'));
          const srx = parseFloat(srcNode.getAttribute('rx'));
          const sry = parseFloat(srcNode.getAttribute('ry'));
          const tcx = parseFloat(tgtNode.getAttribute('cx'));
          const tcy = parseFloat(tgtNode.getAttribute('cy'));
          const trx = parseFloat(tgtNode.getAttribute('rx'));
          const try_ = parseFloat(tgtNode.getAttribute('ry'));
          function eBorder(cx,cy,rx,ry,tx,ty) {{
            const a = Math.atan2(ty-cy, tx-cx);
            return [cx+rx*Math.cos(a), cy+ry*Math.sin(a)];
          }}
          const [x1,y1] = eBorder(scx,scy,srx,sry,tcx,tcy);
          const [x2,y2] = eBorder(tcx,tcy,trx,try_,scx,scy);
          if (el.tagName === 'line') {{
            el.setAttribute('x1', x1); el.setAttribute('y1', y1);
            el.setAttribute('x2', x2); el.setAttribute('y2', y2);
          }} else if (el.tagName === 'text') {{
            el.setAttribute('x', (x1+x2)/2);
            el.setAttribute('y', (y1+y2)/2);
          }}
        }}
      }});
      return;
    }}
    if (isPanning) {{
      pan.x = e.clientX - panStart.x;
      pan.y = e.clientY - panStart.y;
      updateTransform();
    }}
  }});

  svg.addEventListener('mouseup', function() {{
    dragNode = null;
    isPanning = false;
  }});

  svg.addEventListener('mouseleave', function() {{
    dragNode = null;
    isPanning = false;
  }});

  updateTransform();
}})();
</script>"""

        display(HTML(html_content))

    def save_excalidraw(self, filepath, directed_only=False):
        """
        Save the graph as an Excalidraw JSON file (.excalidraw).

        The saved file can be opened directly in Excalidraw (excalidraw.com)
        or any tool that supports the Excalidraw format.

        Args:
            filepath: Output file path (will add .excalidraw extension if not present).
            directed_only: If True, only include directed edges (-->, o->).
        """
        if not filepath.endswith('.excalidraw'):
            filepath += '.excalidraw'

        data = self.to_excalidraw(directed_only=directed_only)
        data["appState"] = {"viewBackgroundColor": "#ffffff"}
        data["files"] = {}

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

    def save_graph(self,
                   plot_pathname: str,
                   plot_format: str ='png',
                   res: int =300, 
                   cleanup:bool =True,
                   directed_only = False):
        """
        Save the graph to a specified file in the specified format.
        
        This method renders the graph to a file with the specified pathname and format.
        Both a graphics file ('png') and a Graphviz source file ('dot') are saved. The 
        graphviz source file can be useful for further editing or inspection of the graph structure.
        
        Args:
            plot_pathname: The pathname of the output file (without extension).
            plot_format: The format to save the graph in (e.g., 'png', 'pdf'). Defaults to 'png'.
            res: The resolution of the plot. Defaults to 300.
            cleanup: Whether to clean up the intermediate files after rendering. Defaults to True.

        """
        
        self.load_graph(res=res, directed_only=directed_only)
        # save gv source
        self.gv_source = self.dot.source
        # save to a file with a .dot extension
        with open(f"{plot_pathname}.dot", 'w') as f:
            f.write(self.gv_source)



        self.dot.format = plot_format
        self.dot.render(filename = plot_pathname,
                        format=plot_format,
                        cleanup=cleanup,
                        
                        )
        pass
    
    def add_edge_lowlevel(self, src, edge_type, tar, **kwargs):
        """Adds an edge to dgraph object.

        Args:
            src: The source node name.
            edge_type: The type of edge (e.g., '-->', 'o->', 'o-o', '<->','---').
            tar: The target node name.
            **kwargs: Additional attributes for the edge (e.g., color='blue', style='dotted').
        """
        # Check if the edge already exists
        if f"{src} {edge_type} {tar}" in self.edges:
            print(f"Edge '{src} {edge_type} {tar}' already exists.")
            raise ValueError(f"Edge '{src} {edge_type} {tar}' already exists.")
            return
        
        # add the edge to the graph dictionary
        # Check if the edge type is valid
        if edge_type not in ['o->', 'o-o', '<->', '---','-->']:
            print(f"Invalid edge type '{edge_type}'.")
            raise ValueError(f"Invalid edge type '{edge_type}'.")
            return
        # Add the edge to the graph dictionary
        if 'properties' not in kwargs:
            kwargs['properties'] = {}
        if 'gvprops' not in kwargs:
            kwargs['gvprops'] = {}
  

        # Create the edge
        self.edges[f"{src} {edge_type} {tar}"] = kwargs

        pass

    def add_edge(self, src, edge_type, tar,  **kwargs):
        """Adds an edge to the graph with the specified attributes.

        Args:
            src: The source node name.
            edge_type: The type of edge (e.g., 'o->', 'o-o', '<->').
            tar: The target node name.
            **kwargs: Additional attributes for the edge (e.g., color='blue', style='dotted').
        """
        newargs = {
            "gvprops": {
                "color": "black",
            },
            "properties": {
                "strength": None,
                "pvalue": None,
            }
        }

        # check if color is in kwargs
        if 'color' in kwargs:
            # set the color
            newargs['gvprops']['color'] = kwargs['color']
        # check if strength is in kwargs
        if 'strength' in kwargs:
            # set the strength
            newargs['properties']['strength'] = kwargs['strength']
        # check if pvalue is in kwargs
        if 'pvalue' in kwargs:
            # set the pvalue
            newargs['properties']['pvalue'] = kwargs['pvalue']
        self.add_edge_lowlevel(src, edge_type, tar, **newargs)
        

        
        pass

    def add_edges(self, edges, exclude=[]):
        """
        Adds multiple edges to the graph.

        Args:
            edges: A list of strings, where each string contains 
                the src edge and tar.  For example: ['A --> B', 'B o-> C', 'C o-o D']
            exclude: A list of edge types to exclude (e.g., ['<->', '---']).
        """
        for edge in edges:
            src, edge_type, tar = edge.split()
            if edge_type not in exclude:
                kwargs = {}
                self.add_edge(src, edge_type, tar, **kwargs)
            
        pass
    def modify_existing_edge(self, from_node, to_node,
                             format: str="0.3f",**kwargs):
        """Modifies the attributes of an existing edge in a Graphviz graph.

        Args:
            from_node: The name of the starting node of the edge.
            to_node: The name of the ending node of the edge.
            format: The format for the strength and  pvalue (default is "0.3f").
            **kwargs: The attributes to modify (e.g., color='blue', style='dotted').
        """

        for edge in self.graph['GRAPH']['edges'].keys():
            # split the edge into its components
            source, type, target = edge.split()

            # check if the edge matches the from_node and to_node
            if source == from_node and target == to_node:
                # modify the edge attributes in kwargs
                for key, value in kwargs.items():
                    if key == 'color':
                        self.graph['GRAPH']['edges'][edge]['gvprops']['color'] = value
                    elif key == 'strength':
                        strength = value
                        if isinstance(strength,float) and format:
                           # convert to string with 3 decimal places
                            strength = f"{strength:.3f}"
                        self.graph['GRAPH']['edges'][edge]['properties']['strength'] = strength
                    elif key == 'pvalue':
                        pvalue = value
                        if isinstance(pvalue,float) and format:
                            # convert to string with 3 decimal places
                            pvalue = f"{pvalue:.3f}"
                        self.graph['GRAPH']['edges'][edge]['properties']['pvalue'] = pvalue

                return
        
        # instead of raising an error, just skip if edge not found and give a warning
        print(f"Warning: Edge '{from_node} {type} {to_node}' not found. Skipping modification.")
        
        #raise ValueError(f"Edge '{from_node} {type} {to_node}' not found.")

        pass
            
if __name__ == "__main__":
    
    # provide a description of the program with format control
    description = textwrap.dedent('''\
    
    Class to support directed graph display in support of causal structure analysis.
    
 
    ''')
    
    parser = argparse.ArgumentParser(
        description=description, formatter_class=argparse.RawTextHelpFormatter)

    # handle a single file on command line argument
    parser.add_argument('--file',  type=str,  help='input file')
    

        
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

    # create the graph object
    obj = DgraphFlex()
    # add edges to graph object
    obj.add_edge('A', '-->', 'B', color='green', strength=-0.5, pvalue=0.01)
    obj.add_edge('B', '-->', 'C', color='red', strength=-.5, pvalue=0.001)
    obj.add_edge('C', 'o->', 'E', color='green', strength=0.5, pvalue=0.005)
    obj.add_edge('B', 'o-o', 'D')
    # save the graph to a file
    obj.save_graph(plot_format='png', plot_name='dgflex2',res=300)
    pass

