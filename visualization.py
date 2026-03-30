import networkx as nx
from pyvis.network import Network
from plotly.graph_objs import Scatter, Figure
import load_data

COLOUR_SCHEME = [
    '#2E91E5', '#E15F99', '#1CA71C', '#FB0D0D', '#DA16FF', '#222A2A', '#B68100',
    '#750D86', '#EB663B', '#511CFB', '#00A08B', '#FB00D1', '#FC0080', '#B2828D',
    '#6C7C32', '#778AAE', '#862A16', '#A777F1', '#620042', '#1616A7', '#DA60CA',
    '#6C4516', '#0D2A63', '#AF0038'
]

LINE_COLOUR = 'rgb(0,0,0)'
VERTEX_BORDER_COLOUR = 'rgb(50, 50, 50)'
DISEASE_COLOUR = 'rgb(209, 9, 9)'
COMMON_DISEASE_COLOUR = 'rgb(245, 112, 29)'
SYMPTOM_COLOUR = 'rgb(8, 105, 205)'
TREATMENT_COLOUR = 'rgb(25, 143, 10)'

def visualize_graph(graph: load_data.WeightedGraph,
                    layout: str = 'spring_layout',
                    max_vertices: int = 200,
                    symptoms: set = set(),
                    output_file: str = '') -> None:
    """Use plotly and networkx to visualize the given graph.

    Optional arguments:
        - layout: which graph layout algorithm to use
        - max_vertices: the maximum number of vertices that can appear in the graph
        - output_file: a filename to save the plotly image to (rather than displaying
            in your web browser)
    """
    graph_nx = graph.to_networkx(max_vertices, symptoms)

    pos = getattr(nx, layout)(graph_nx)

    x_values = [pos[k][0] for k in graph_nx.nodes]
    y_values = [pos[k][1] for k in graph_nx.nodes]
    labels = list(graph_nx.nodes)

    all_neighbours = [set(graph_nx.neighbors(k)) for k in symptoms]
    common_diseases = set.intersection(*all_neighbours)

    colours = []
    for k in graph_nx.nodes:
        if k in common_diseases:
            colours.append(COMMON_DISEASE_COLOUR)
        elif graph_nx.nodes[k]['kind'] == 'symptom':
            colours.append(SYMPTOM_COLOUR)
        elif graph_nx.nodes[k]['kind'] == 'disease':
            colours.append(DISEASE_COLOUR)
        else:
            colours.append(TREATMENT_COLOUR)

    edge_traces = []
    for edge in graph_nx.edges:
        weight = 0.1 + graph_nx.edges[edge]['weight'] * 3
        edge_traces.append(
            Scatter(
                x=[pos[edge[0]][0], pos[edge[1]][0], None],
                y=[pos[edge[0]][1], pos[edge[1]][1], None],
                mode='lines',
                name='edges',
                line=dict(color=LINE_COLOUR, width=weight),  # width set per edge
                hoverinfo='none',
            )
        )
    trace4 = Scatter(x=x_values,
                     y=y_values,
                     mode='markers',
                     name='nodes',
                     marker=dict(symbol='circle-dot',
                                 size=5,
                                 color=colours,
                                 line=dict(color=VERTEX_BORDER_COLOUR, width=0.5)
                                 ),
                     text=labels,
                     hovertemplate='%{text}',
                     hoverlabel={'namelength': 0}
                     )

    data1 = edge_traces + [trace4]
    fig = Figure(data=data1)
    fig.update_layout({'showlegend': False})
    fig.update_xaxes(showgrid=False, zeroline=False, visible=False)
    fig.update_yaxes(showgrid=False, zeroline=False, visible=False)

    if output_file == '':
        fig.show()
    else:
        fig.write_image(output_file)


if __name__ == '__main__':
    g = load_data.load_weighted_disease_graph('symptoms.csv')
    visualize_graph(g, symptoms={'anxiety and nervousness'})