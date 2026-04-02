"""Contains the WeightedGraph dataclass used to represent the disease-treatment-symptom system of the datasets."""

from __future__ import annotations
from typing import Any
import networkx as nx


class _WeightedVertex:
    """A vertex in a weighted diagnosis graph, used to represent a symptom, a disease or a treatment.

    Each vertex item is the name of a symptom, a disease, or a treatment. All are represented as strings.
    Here, neighbours is a dictionary mapping a neighbour vertex to the weight of the edge to from self to that
    neighbour.

    Instance Attributes:
        - item: The data stored in this vertex, representing a disease name, symptom, or treatment.
        - kind: The type of this vertex: 'disease', 'symptom', or 'treatment'.
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
    """A weighted graph used to represent a symptom-disease-treatment network that keeps track of the probability of
    having a disease if the symptom is observed, and the probability a certain drug can be used to treat a disease.
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
            - kind in {'symptom', 'disease', 'treatment'}
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
            - kind in {'symptom', 'treatment', 'disease'}
        """
        if kind != '':
            return {v.item for v in self._vertices.values() if v.kind == kind}
        else:
            return set(self._vertices.keys())

    def to_networkx(self, max_vertices: int = 1000, symptoms: set = None) -> nx.Graph:
        """Convert this graph into a networkx Graph.

        max_vertices specifies the maximum number of vertices that can appear in the graph.
        (This is necessary to limit the visualization output for large graphs.)
        """
        graph_nx = nx.Graph()
        for v in self._vertices.values():
            if symptoms is None or v.item in symptoms:
                graph_nx.add_node(v.item, kind=v.kind)

                for u in v.neighbours:
                    if graph_nx.number_of_nodes() < max_vertices:
                        graph_nx.add_node(u.item, kind=u.kind)
                        for w in u.neighbours:
                            if graph_nx.number_of_nodes() < max_vertices and w.kind == 'treatment':
                                graph_nx.add_node(w.item, kind=w.kind)

                            if w.item in graph_nx.nodes and self.get_weight(u.item, w.item) != 0:
                                graph_nx.add_edge(u.item, w.item, weight=self.get_weight(w.item, u.item))

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

    def predict_diseases(self, symptoms: set[str], limit: int = None) -> list[tuple[str, float]]:
        """Return a list of up to <limit> disease and probability pairs based on likelihood based on the given symptoms.

        The return value is a list of disease and probability pairs, sorted in *descending order* of probability.
        Probability is calculated based on the above method.

        The returned list does NOT contain:
            - any disease with a probability of 0.0
            - any duplicates
            - any vertices that do not represent a disease

        The probabilities are normalized so that they sum to 1.

        Up to <limit> pairs are returned, starting with the disease with the highest probability,
        then the second-highest probability, etc. Fewer than <limit> pairs are returned if
        and only if there aren't enough pairs that meet the above criteria.

        Preconditions:
            - diseases in self._vertices
            - self._vertices[disease].kind == 'disease'
            - all({symptom in self._vertices for symptom in symptoms})
            - all({self._vertices[symptom].kind == 'symptom' for symptom in symptoms})
            - limit >= 1 or limit is None

        If <limit> is None, then all eligible disease and probability pairs are returned.
        """
        diseases = {}  # mapping of diseases to the probability of having that disease
        for vertex in self._vertices:
            if self._vertices[vertex].kind == 'disease':
                diseases[vertex] = self.get_disease_probability(vertex, symptoms)
        probable_diseases = [(disease, diseases[disease]) for disease in diseases]
        probable_diseases.sort(key=lambda disease_pair: disease_pair[1], reverse=True)
        if limit is None:
            limit = len(diseases)
        cutoff = 0
        while cutoff < len(probable_diseases) and cutoff < limit and probable_diseases[cutoff][1] != 0.0:
            cutoff += 1
        return normalize_probabilities(probable_diseases[:cutoff])

    def predict_treatments(self, symptoms: set[str], limit: int = None) -> list[tuple[str, float]]:
        """Return a list of up to <limit> treatment and probability pairs based on likelihood based on the given
        symptoms.

        The return value is a list of treatment and probability pairs, sorted in *descending order* of probability.
        Probability is calculated by first calculating disease probabilities based on the method described in the
        docstring for predict diseases and then finding the sum of the products of the probability the patient has some
        disease and the probability that the treatment will be used in treating that disease. Note that this
        calculation ignores potential side effects the treatment may have with diseases it does not treat.

        The returned list does NOT contain:
            - any treatment with a probability of 0.0
            - any duplicates
            - any vertices that do not represent a treatment

        Up to <limit> pairs are returned, starting with the treatment with the highest probability,
        then the second-highest probability, etc. Fewer than <limit> pairs are returned if
        and only if there aren't enough pairs that meet the above criteria.

        Preconditions:
            - treatment in self._vertices
            - self._vertices[treatment].kind == 'treatment'
            - all({symptom in self._vertices for symptom in symptoms})
            - all({self._vertices[symptom].kind == 'symptom' for symptom in symptoms})
            - limit >= 1 or limit is None

        If <limit> is None, then all eligible treatment and probability pairs are returned.
        """
        treatments = {}
        probable_diseases = self.predict_diseases(symptoms)
        for disease, probability in probable_diseases:
            for treatment in self.get_neighbours(disease):
                if self._vertices[treatment].kind == 'treatment':
                    if treatment in treatments:
                        treatments[treatment] += probability * self.get_weight(disease, treatment)
                    else:
                        treatments[treatment] = probability * self.get_weight(disease, treatment)
        probable_treatments = [(treatment, treatments[treatment]) for treatment in treatments]
        probable_treatments.sort(key=lambda treatment_pair: treatment_pair[1], reverse=True)
        if limit is None:
            limit = len(treatments)
        cutoff = 0
        while cutoff < len(probable_treatments) and cutoff < limit and probable_treatments[cutoff][1] != 0.0:
            cutoff += 1
        return probable_treatments[:cutoff]


def normalize_probabilities(probable: list[tuple[str, float]]) -> list[tuple[str, float]]:
    """Returns a list that is the same list as given, but with the floats normalized.

    Normalization indicates that the floats now add up to 1.0, and relative proportions are preserved.

    >>> probable = [('abc', 0.2), ('def', 0.3)]
    >>> normalize_probabilities(probable)
    [('abc', 0.4), ('def', 0.6)]
    """
    total = 0.0
    for item, prob in probable:
        total += prob
    normalized_probable = []
    for item, prob in probable:
        normalized_probable.append((item, prob / total))
    return normalized_probable


if __name__ == '__main__':
    import python_ta

    python_ta.check_all(config={
        'max-line-length': 120,
        'disable': ['static_type_checker'],
        'allow-local-imports': True,
        'max-nested-blocks': 4
    })

    import doctest
    doctest.testmod()
