"""Contains the functions used for loading the graphs from csv files."""

from __future__ import annotations
import csv
from graph import WeightedGraph


def load_weighted_disease_graph(disease_file: str, treatment_file: str) -> WeightedGraph:
    """Loads a WeightedGraph from two csv files, one for the symptom-disease edges and one for the treatment-disease
    edges.

    The graph stores one vertex for each disease, symptom, and treatment in the datasets.

    Edges represent the chance of having a disease given a symptom, and the chance of a disease being able to be treated
    by a certain treatment."""
    g = WeightedGraph()

    symptoms_disease, symptom_count = load_disease_file(disease_file)
    for symptom in symptoms_disease:
        g.add_vertex(symptom, 'symptom')
        for disease in symptoms_disease[symptom]:
            if disease in symptom_count:  # if the disease has the same name as a symptom
                g.add_vertex(disease + ' (disease)', 'disease')
                if symptom_count[symptom] != 0 and symptoms_disease[symptom][disease] != 0:
                    g.add_edge(symptom, disease + ' (disease)',
                               symptoms_disease[symptom][disease] / symptom_count[symptom])
            else:
                g.add_vertex(disease, 'disease')
                if symptom_count[symptom] != 0 and symptoms_disease[symptom][disease] != 0:
                    g.add_edge(symptom, disease, symptoms_disease[symptom][disease] / symptom_count[symptom])

    disease_treatment, disease_count = load_treatment_file(treatment_file)
    for disease in disease_treatment:
        if (disease in g.get_all_vertices(kind='disease')
                or (disease + ' (disease)') in g.get_all_vertices(kind='disease')):
            disease_name = disease
            if disease not in g.get_all_vertices(kind='disease'):
                disease_name += ' (disease)'
            for treatment in disease_treatment[disease]:
                g.add_vertex(treatment, 'treatment')
                g.add_edge(treatment, disease_name, disease_treatment[disease][treatment] / disease_count[disease])
    return g


def load_disease_file(disease_file: str) -> tuple[dict, dict]:
    """Loads two dictionaries about the relationship between diseases and symptoms."""
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
                if disease in symptoms_disease[symptom_index[i - 1]]:
                    symptoms_disease[symptom_index[i - 1]][disease] += int(row[i])
                else:
                    symptoms_disease[symptom_index[i - 1]][disease] = int(row[i])
                symptom_count[symptom_index[i - 1]] += int(row[i])

    return symptoms_disease, symptom_count


def load_treatment_file(treatment_file: str) -> tuple[dict, dict]:
    """Loads two dictionaries about the relationship between diseases and treatments."""
    disease_treatment = {}
    disease_count = {}
    with open(treatment_file) as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            disease = row[1].lower()
            if disease in disease_treatment:
                for treatment in row[2].split(' / '):
                    if treatment in disease_treatment[disease]:
                        disease_treatment[disease][treatment] += 1
                    else:
                        disease_treatment[disease][treatment] = 1
                disease_count[disease] += 1
            else:
                disease_treatment[disease] = {}
                for treatment in row[2].split(' / '):
                    disease_treatment[disease][treatment] = 1
                disease_count[disease] = 1
    return disease_treatment, disease_count


if __name__ == '__main__':
    # g = load_weighted_disease_graph('symptoms.csv', 'treatment.csv')
    import python_ta

    python_ta.check_all(config={
        'max-line-length': 120,
        'disable': ['static_type_checker'],
        'allow-local-imports': True,
        'max-nested-blocks': 4
    })
