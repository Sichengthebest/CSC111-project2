from load_data import load_weighted_disease_graph
from visualization import visualize_graph

def interface():
    print('Hello, this is your disease diagnosis tool.')
    print('... loading graph ...')
    g = load_weighted_disease_graph('symptoms.csv')
    print('What symptoms do you have?')
    done = False
    symptoms = set()
    while not done:
        symptom = input('Insert symptom: If you are done, type "done".\n')
        if symptom == 'done':
            done = True
        elif symptom in g.get_all_vertices(kind='symptom'):
            symptoms.add(symptom)
        else:
            print('Sorry, that is not a symptom in our dataset.')

    complete = False
    while not complete:
        choice = input('If you would like to view a visualization of your possible diseases, '
                       'insert "visualize". Otherwise, to see the chances of having a certain disease,'
                       'type "diagnosis". If you wish to exit, type "exit".\n')
        if choice == 'visualize':
            visualize_graph(g, symptoms=symptoms)
        elif choice == 'diagnosis':
            num_out = int(input('How many possible diseases do you want?'))
            diseases = g.predict_diseases(symptoms, num_out)
            if diseases == set():
                print('There are no diseases matching your symptoms.')
            for disease in diseases:
                print(str(round(disease[1] * 100, 2)) + '% chance of ' + disease[0])
        elif choice == 'exit':
            complete = True
        else:
            print('Invalid choice.')
