"""Visualize the graph with networkx and plotly"""

import networkx as nx
from plotly.graph_objs import Scatter, Figure
from graph import WeightedGraph

VERTEX_BORDER_COLOUR = 'rgb(50, 50, 50)'
DISEASE_COLOUR = 'rgb(209, 9, 9)'
COMMON_DISEASE_COLOUR = 'rgb(224, 173, 2)'
SYMPTOM_COLOUR = 'rgb(8, 105, 205)'
TREATMENT_COLOUR = 'rgb(25, 143, 10)'
COMMON_TREATMENT_COLOUR = 'rgb(224, 2, 213)'


def visualize_graph(graph: WeightedGraph,
                    layout: str = 'spring_layout',
                    max_vertices: int = 1000,
                    symptoms: set = None,
                    output_file: str = '') -> None:
    """Use plotly and networkx to visualize the given graph.

    Optional arguments:
        - layout: which graph layout algorithm to use
        - max_vertices: the maximum number of vertices that can appear in the graph
        - symptoms: the symptoms to include in the graph
        - output_file: a filename to save the plotly image to (rather than displaying
            in your web browser)
    """
    graph_nx = graph.to_networkx(max_vertices, symptoms)

    pos = getattr(nx, layout)(graph_nx)

    x_values = [pos[k][0] for k in graph_nx.nodes]
    y_values = [pos[k][1] for k in graph_nx.nodes]
    labels = list(graph_nx.nodes)

    colours = set_colours(graph_nx, symptoms)

    edge_traces = []
    for edge in graph_nx.edges:
        weight = 0.1 + graph_nx.edges[edge]['weight'] * 3
        weight_rgb = 100 - graph_nx.edges[edge]['weight'] * 100
        edge_traces.append(
            Scatter(
                x=[pos[edge[0]][0], pos[edge[1]][0], None],
                y=[pos[edge[0]][1], pos[edge[1]][1], None],
                mode='lines',
                name='edges',
                line=dict(color=f'rgb({weight_rgb}, {weight_rgb}, {weight_rgb})', width=weight),  # width set per edge
                hoverinfo='none',
                showlegend=False
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
                     hoverlabel={'namelength': 0},
                     showlegend=False
                     )

    unique_colours = {
        "Symptoms": SYMPTOM_COLOUR,
        "Diseases": DISEASE_COLOUR,
        "Common diseases": COMMON_DISEASE_COLOUR,
        "Treatments": TREATMENT_COLOUR,
        "Common treatments": COMMON_TREATMENT_COLOUR
    }

    legend_traces = [
        Scatter(
            x=[None], y=[None],
            mode='markers',
            name=category,
            marker=dict(symbol='circle-dot', size=8, color=colour,
                        line=dict(color=VERTEX_BORDER_COLOUR, width=0.5)),
            showlegend=True,
        )
        for category, colour in unique_colours.items()
    ]

    data1 = edge_traces + [trace4] + legend_traces
    fig = Figure(data=data1)
    fig.update_layout(
        showlegend=True,
        legend=dict(
            title='Node Colour',
            itemsizing='constant',
            bgcolor='rgba(255,255,255,0.8)',
            bordercolor='lightgrey',
            borderwidth=1,
        )
    )
    fig.update_xaxes(showgrid=False, zeroline=False, visible=False)
    fig.update_yaxes(showgrid=False, zeroline=False, visible=False)

    if output_file == '':
        fig.show()
    else:
        fig.write_image(output_file)


def set_colours(graph_nx: nx.Graph, symptoms: set | None) -> list[str]:
    """Return a list of the colour of each node in the graph, where:

        - Symptoms use SYMPTOM_COLOUR
        - Diseases common to all symptoms use COMMON_DISEASE_COLOUR
        - Other diseases use DISEASE_COLOUR
        - Treatments common to all common diseases use COMMON_TREATMENT_COLOUR
        - Other treatments use TREATMENT_COLOUR
    """
    common_diseases = set()
    if symptoms is not None:
        all_poss_diseases = [set(graph_nx.neighbors(s)) for s in symptoms]
        common_diseases = set.intersection(*all_poss_diseases)

    all_poss_treatments = []
    for k in common_diseases:
        all_poss_treatments.append(set())
        for n in graph_nx.neighbors(k):
            if graph_nx.nodes[n]['kind'] == 'treatment':
                all_poss_treatments[-1].add(n)
    common_treatments = set()
    if all_poss_treatments:
        common_treatments = set.intersection(*all_poss_treatments)

    colours = []
    for k in graph_nx.nodes:
        if k in common_diseases:
            colours.append(COMMON_DISEASE_COLOUR)
        elif k in common_treatments:
            colours.append(COMMON_TREATMENT_COLOUR)
        elif graph_nx.nodes[k]['kind'] == 'symptom':
            colours.append(SYMPTOM_COLOUR)
        elif graph_nx.nodes[k]['kind'] == 'disease':
            colours.append(DISEASE_COLOUR)
        else:
            colours.append(TREATMENT_COLOUR)
    return colours


if __name__ == '__main__':
    # g = load_weighted_disease_graph('symptoms.csv', 'treatment.csv')
    # visualize_graph(g, symptoms={'anxiety and nervousness'})

    import python_ta

    python_ta.check_all(config={
        'max-line-length': 120,
        'disable': ['static_type_checker'],
        'allow-local-imports': True,
        'max-nested-blocks': 4
    })
