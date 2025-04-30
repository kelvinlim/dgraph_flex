from  dgraph_flex import DgraphFlex

obj = DgraphFlex()
# add edges to graph object
obj.add_edge('A', '-->', 'B', color='green', strength=-0.5, pvalue=0.01)
obj.add_edge('B', '-->', 'C', color='red', strength=-.5, pvalue=0.001)
obj.add_edge('C', 'o->', 'E', color='green', strength=0.5, pvalue=0.005)
obj.add_edge('D', 'o-o', 'B')



# modify an existing edge
obj.modify_existing_edge('A', 'B', color='blue', strength=0.2, pvalue=0.0001)

# load into graphviz object
#obj.load_graph(res=96)  # set resolution for the graph
# save the graph to a file

obj.save_graph(plot_format='png', plot_name='dgflex_add')