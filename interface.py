"""Uses tkinter to generate a window for the user to interactively add symptoms
and view possible diseases and treatments."""

from typing import Any
from tkinter import *
from tkinter import ttk
from load_data import load_weighted_disease_graph
from visualization import visualize_graph

G = load_weighted_disease_graph('symptoms.csv', 'treatment.csv')
SYMPTOMS_LST = list(G.get_all_vertices(kind='symptom'))


class Interface:
    """A tkinter interface the user can interactively add symptoms, as well as view possible diseases
    and treatments.

    Instance Attributes:
        - root: The data stored in this vertex, representing a disease name, symptom, or treatment.
        - user_symptoms: The set of symptoms the user has inputted.

    Representation Invariants:
        - all(symptom in SYMPTOMS_LST for symptom in self.user_symptoms)
    """
    root: Tk
    user_symptoms: set

    def __init__(self, root: Tk) -> None:
        self.root = root
        self.user_symptoms = set()
        self.start_screen()

    def start_screen(self) -> None:
        """Create the start screen layout."""
        for w in self.root.winfo_children():
            w.destroy()
        self.user_symptoms.clear()
        label = Label(self.root, text='Search your symptoms')
        label.pack()

        combo_box = ttk.Combobox(self.root, values=SYMPTOMS_LST)

        combo_box.set('Search')
        combo_box.pack()
        combo_box.bind('<KeyRelease>', self.search)
        combo_box.bind('<Return>', self.show_value)

        button = Button(self.root, text='I have finished entering symptoms.', command=self.menu)
        button.pack()

    def show_value(self, event: Event) -> None:
        """Display the symptoms entered by the user and handles invalid inputs."""
        value = event.widget.get()
        if value in SYMPTOMS_LST:
            if value not in self.user_symptoms:
                frame = Frame(self.root)
                frame.pack(fill='x')

                label2 = Label(frame, text='Selected symptom: ' + value)
                label2.pack(side='left')
                self.user_symptoms.add(value)
                button2 = Button(frame, text='Delete', command=lambda: self.delete_symptom(frame, value))
                button2.pack(side='right')
            else:
                label2 = Label(self.root, text='You already selected ' + value + '!')
                label2.pack()
                self.root.after(3000, label2.destroy)
        else:
            label2 = Label(self.root, text='Error: Symptom not found.')
            label2.pack()
            self.root.after(3000, label2.destroy)
        event.widget.delete(0, 'end')

    def menu(self) -> None:
        """Display the menu screen after the user entered symptoms."""
        if self.user_symptoms == set():
            label3 = Label(self.root, text='You have not selected any symptoms.')
            label3.pack()
            self.root.after(3000, label3.destroy)
        else:
            for w in self.root.winfo_children():
                w.destroy()
            button1 = Button(self.root, text='Visualize graph', command=self.visualize)
            button1.pack()
            button2 = Button(self.root, text='Diagnose possible diseases', command=self.diagnosis)
            button2.pack()
            button3 = Button(self.root, text='See possible treatments', command=self.treatment)
            button3.pack()
            button4 = Button(self.root, text='Enter different symptoms', command=self.start_screen)
            button4.pack()

    def search(self, event: Event) -> None:
        """Filter the search box for the user to interactively add symptoms."""
        combo_box = event.widget
        value = event.widget.get()
        if value == '':
            combo_box['values'] = SYMPTOMS_LST
        else:
            filtered_symptoms = []
            for item in SYMPTOMS_LST:
                if value.lower() in item:
                    filtered_symptoms.append(item)
            combo_box['values'] = filtered_symptoms

    def delete_symptom(self, frame: Frame, symptom: Any) -> None:
        """Deletes a symptoms from the user's list of symptoms."""
        self.user_symptoms.remove(symptom)
        frame.destroy()

    def visualize(self) -> None:
        """Call the graph visualization function."""
        visualize_graph(G, symptoms=self.user_symptoms)

    def diagnosis(self) -> None:
        """Show the screen for the user to input the number of possible diseases they want displayed."""
        for w in self.root.winfo_children():
            w.destroy()
        e1 = Entry(self.root)
        e1.insert(0, 'How many possible diseases?')
        e1.pack()
        b1 = Button(self.root, text='Diagnose me!', command=lambda: self.show_diagnosis(e1))
        b1.pack()

    def show_diagnosis(self, e1: Entry) -> None:
        """Displays the possible diseases the user may have."""
        num = e1.get()
        if num.isnumeric() and int(num) > 0:
            for w in self.root.winfo_children():
                w.destroy()
            diseases = G.predict_diseases(self.user_symptoms, int(num))
            for disease in diseases:
                lb = Label(self.root, text=str(round(disease[1] * 100, 2)) + '% chance of ' + disease[0])
                lb.pack()
            if not diseases:
                lb = Label(self.root, text='There are no diseases with those symptoms.')
                lb.pack()
            b = Button(self.root, text='Back', command=self.menu)
            b.pack()
        else:
            lb = Label(self.root, text='Error: Number of possible diseases must be a number.')
            lb.pack()
            self.root.after(3000, lb.destroy)

    def treatment(self) -> None:
        """Show the screen for the user to input the number of possible treatments they want displayed."""
        for w in self.root.winfo_children():
            w.destroy()
        e1 = Entry(self.root)
        e1.insert(0, 'How many possible treatments?')
        e1.pack()
        b1 = Button(self.root, text='Treat me!', command=lambda: self.show_treatment(e1))
        b1.pack()

    def show_treatment(self, e1: Entry) -> None:
        """Display the possible treatments the user may use."""
        num2 = e1.get()
        if num2.isnumeric() and int(num2) > 0:
            for w in self.root.winfo_children():
                w.destroy()
            treatments = G.predict_treatments(self.user_symptoms, int(num2))
            for treatment in treatments:
                lb = Label(self.root, text=str(round(treatment[1] * 100, 2)) + '% chance of ' + treatment[0])
                lb.pack()
            if not treatments:
                lb = Label(self.root, text='There are no treatments for your diseases.')
                lb.pack()
            b = Button(self.root, text='Back', command=self.menu)
            b.pack()
        else:
            lb = Label(self.root, text='Error: Number of possible treatments must be a number.')
            lb.pack()
            self.root.after(3000, lb.destroy)


if __name__ == '__main__':
    import python_ta

    python_ta.check_all(config={
        'max-line-length': 120,
        'disable': ['static_type_checker'],
        'allow-local-imports': True,
        'max-nested-blocks': 4
    })
