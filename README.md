# dgraph_flex

Package to support flexible storage of directed graphs, specifically for the support of 
directed graphs and causal structure analysis.



## sample usage

Here is a sample yaml file describing a graph
```yaml

GENERAL:
  version: 1.0
  framework: dgraph_flex
  gvinit:  # global graphviz initialization
    nodes: 
      shape: oval
      color: black

GRAPHS:
  - name: graph1
    edges:
      - name: edge1
        source: A
        target: B
        edge_type: -->
        properties:
          strength: 0.5
          pvalue: 0.01
        gvprops: # graphviz properties
          color: green
      - name: edge2
        source: B
        target: C
        edge_type: -->
        properties:
          strength: -0.5
          pvalue: 0.001
        gvprops: # graphviz properties
          color: red
      - name: edge3
        source: C
        target: E
        edge_type: o->
        properties:
          strength: 0.5
          pvalue: 0.0005
        gvprops: # graphviz properties
          color: green
      - name: edge4
        source: B
        target: D
        edge_type: o-o
        properties:


```
Here is python code that reads in the graph and outputs a png

```python

from dgraph_flex import DgraphFlex

obj = DgraphFlex(yamlpath='graph_sample.yaml')
obj.read_yaml(self.config['yamlpath'])
obj.load_graph()



```

## unit tests

```
python -m unittest tests/*.py
```

## build

```
python -m build

# upload
twine upload dist/*

```