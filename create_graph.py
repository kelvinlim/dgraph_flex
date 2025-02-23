
import graphviz

# Create a Digraph object
dot = graphviz.Digraph('Simple Digraph')

# Add edges using dot.edge()
dot.edge('A', 'B')
dot.edge('B', 'C')
dot.edge('C', 'A')


# Render the graph to a PNG file
dot.render('simplegraph', format='png', view=True) 