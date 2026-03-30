from __future__ import annotations
import csv
import networkx as nx
from typing import Any

class _WeightedVertex:
    """A vertex in a weighted book review graph, used to represent a user or a book.

        Same documentation as _Vertex from Part 1, except now neighbours is a dictionary mapping
        a neighbour vertex to the weight of the edge to from self to that neighbour.

        Instance Attributes:
            - item: The data stored in this vertex, representing a disease name, symptom, or treatment.
            - kind: The type of this vertex: 'disease', 'symptom', or 'book'.
            - neighbours: The vertices that are adjacent to this vertex, and their corresponding
                edge weights.

        Representation Invariants:
            - self not in self.neighbours
            - all(self in u.neighbours for u in self.neighbours)
            - self.kind in {'disease', 'symptom', 'treatment'}
    """
    item: str
    kind: str
    neighbours: dict[_WeightedVertex, float]

    def __init__(self, item: Any, kind: str) -> None:
        """Initialize a new vertex with the given item and kind.

        This vertex is initialized with no neighbours.

        Preconditions:
            - kind in {'symptom', 'disease', 'treatment'}
        """
        self.item = item
        self.kind = kind
        self.neighbours = {}

    def degree(self) -> int:
        """Return the degree of this vertex."""
        return len(self.neighbours)


class WeightedGraph:
    """A weighted graph used to represent a disease-symptom network or a disease-treament network that keeps track of
    the probability of having a disease if you have the symptom, and the probability a certain drug can be used to treat
    a disease.
    """
    # Private Instance Attributes:
    #     - _vertices:
    #         A collection of the vertices contained in this graph.
    #         Maps item to _WeightedVertex object.
    _vertices: dict[Any, _WeightedVertex]

    def __init__(self) -> None:
        """Initialize an empty graph (no vertices or edges)."""
        self._vertices = {}

    def add_vertex(self, item: Any, kind: str) -> None:
        """Add a vertex with the given item and kind to this graph.

        The new vertex is not adjacent to any other vertices.
        Do nothing if the given item is already in this graph.

        Preconditions:
            - kind in {'user', 'book'}
        """
        if item not in self._vertices:
            self._vertices[item] = _WeightedVertex(item, kind)

    def add_edge(self, item1: Any, item2: Any, weight: float) -> None:
        """Add an edge between the two vertices with the given items in this graph,
        with the given weight.

        Raise a ValueError if item1 or item2 do not appear as vertices in this graph.

        Preconditions:
            - item1 != item2
        """
        if item1 in self._vertices and item2 in self._vertices:
            v1 = self._vertices[item1]
            v2 = self._vertices[item2]

            # Add the new edge
            v1.neighbours[v2] = weight
            v2.neighbours[v1] = weight
        else:
            # We didn't find an existing vertex for both items.
            raise ValueError

    def get_weight(self, item1: Any, item2: Any) -> float:
        """Return the weight of the edge between the given items.

        Return 0 if item1 and item2 are not adjacent.

        Preconditions:
            - item1 and item2 are vertices in this graph
        """
        v1 = self._vertices[item1]
        v2 = self._vertices[item2]
        return v1.neighbours.get(v2, 0)

    def average_weight(self, item: Any) -> float:
        """Return the average weight of the edges adjacent to the vertex corresponding to item.

        Raise ValueError if item does not corresponding to a vertex in the graph.
        """
        if item in self._vertices:
            v = self._vertices[item]
            return sum(v.neighbours.values()) / len(v.neighbours)
        else:
            raise ValueError

    def adjacent(self, item1: Any, item2: Any) -> bool:
        """Return whether item1 and item2 are adjacent vertices in this graph.

        Return False if item1 or item2 do not appear as vertices in this graph.
        """
        if item1 in self._vertices and item2 in self._vertices:
            v1 = self._vertices[item1]
            return any(v2.item == item2 for v2 in v1.neighbours)
        else:
            return False

    def get_neighbours(self, item: Any) -> set:
        """Return a set of the neighbours of the given item.

        Note that the *items* are returned, not the _Vertex objects themselves.

        Raise a ValueError if item does not appear as a vertex in this graph.
        """
        if item in self._vertices:
            v = self._vertices[item]
            return {neighbour.item for neighbour in v.neighbours}
        else:
            raise ValueError

    def get_all_vertices(self, kind: str = '') -> set:
        """Return a set of all vertex items in this graph.

        If kind != '', only return the items of the given vertex kind.

        Preconditions:
            - kind in {'', 'symptom', 'treatment', 'disease'}
        """
        if kind != '':
            return {v.item for v in self._vertices.values() if v.kind == kind}
        else:
            return set(self._vertices.keys())

    def to_networkx(self, max_vertices: int = 5000, symptoms: set = set()) -> nx.Graph:
        """Convert this graph into a networkx Graph.

        max_vertices specifies the maximum number of vertices that can appear in the graph.
        (This is necessary to limit the visualization output for large graphs.)
        """
        graph_nx = nx.Graph()
        for v in self._vertices.values():
            if v.item in symptoms or symptoms == set():
                graph_nx.add_node(v.item, kind=v.kind)

                for u in v.neighbours:
                    if graph_nx.number_of_nodes() < max_vertices:
                        graph_nx.add_node(u.item, kind=u.kind)

                    if u.item in graph_nx.nodes and self.get_weight(u.item, v.item) != 0:
                        graph_nx.add_edge(v.item, u.item, weight=self.get_weight(u.item, v.item))

                if graph_nx.number_of_nodes() >= max_vertices:
                    break

        return graph_nx

    def get_disease_probability(self, disease: str, symptoms: set[str]) -> float:
        """Return the probability of having the given disease provided the patient has the given symptoms.

        Probability is calculated by finding the product of the probabilities that the patient has the disease given
        each symptom. Note that this calculation ignores comorbidity and assumes all probabilities are independent.

        Raise a ValueError if disease or any elements of symptoms do not appear as vertices in this graph.
        """
        if disease in self._vertices and all({symptom in self._vertices for symptom in symptoms}):
            disease_probability = 1.0
            for symptom in symptoms:
                disease_probability *= self.get_weight(disease, symptom)
            return disease_probability
        else:
            raise ValueError

    def predict_diseases(self, symptoms: set[str], limit: int) -> list[tuple[str, float]]:
        """Return a list of up to <limit> disease and probability pairs based on likelihood based on the given symptoms.

        The return value is a list of disease and probability pairs, sorted in *descending order* of probability.
        Probability is calculated based on the above method.

        The returned list does NOT contain:
            - any disease with a probability of 0.0
            - any duplicates
            - any vertices that represents a symptom (instead of a disease)

        Up to <limit> pairs are returned, starting with the disease with the highest probability,
        then the second-highest probability, etc. Fewer than <limit> pairs are returned if
        and only if there aren't enough pairs that meet the above criteria.

        Preconditions:
            - diseases in self._vertices
            - self._vertices[disease].kind == 'disease'
            - all({symptom in self._vertices for symptom in symptoms})
            - all({self._vertices[symptom].kind == 'symptom' for symptom in symptoms})
            - limit >= 1
        """
        diseases = {}  # mapping of diseases to the probability of having that disease
        for vertex in self._vertices:
            if self._vertices[vertex].kind == 'disease':
                diseases[vertex] = self.get_disease_probability(vertex, symptoms)
        probable_diseases = []
        for i in range(limit):
            if len(diseases) != 0:
                most_probable_so_far = list(diseases.keys())[0]
                for disease in diseases:
                    if diseases[disease] > diseases[most_probable_so_far]:
                        most_probable_so_far = disease
                if diseases[most_probable_so_far] != 0.0:
                    probable_diseases.append((most_probable_so_far, diseases[most_probable_so_far]))
                    diseases.pop(most_probable_so_far)
                else:
                    break
            else:
                break
        return probable_diseases

def load_weighted_disease_graph(disease_file: str) -> WeightedGraph:
    g = WeightedGraph()
    symptom_index = []
    symptom_count = {}
    symptoms_disease = {}

    with open(disease_file) as file:
        reader = csv.reader(file)
        header = next(reader)
        for symptom in header[1:]:
            symptom_index.append(symptom)
            symptoms_disease[symptom] = {}
            symptom_count[symptom] = 0
        for row in reader:
            disease = row[0]
            for i in range(1, len(row)):
                if disease in symptoms_disease[symptom_index[i-1]]:
                    symptoms_disease[symptom_index[i-1]][disease] += int(row[i])
                else:
                    symptoms_disease[symptom_index[i-1]][disease] = int(row[i])
                symptom_count[symptom_index[i-1]] += int(row[i])

    for symptom in symptoms_disease:
        g.add_vertex(symptom, 'symptom')
        for disease in symptoms_disease[symptom]:
            if symptom == disease:
                print(symptom)
            g.add_vertex(disease, 'disease')
            if symptom_count[symptom] != 0 and symptoms_disease[symptom][disease] != 0:
                g.add_edge(symptom, disease, symptoms_disease[symptom][disease] / symptom_count[symptom])
    return g

if __name__ == '__main__':
    g = load_weighted_disease_graph('symptoms.csv')
