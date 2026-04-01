"""Uses tkinter to generate a window for the user to interactively add symptoms and view possible diseases and treatments."""

from load_data import load_weighted_disease_graph
from visualization import visualize_graph
from tkinter import *
from tkinter import ttk

g = load_weighted_disease_graph('symptoms.csv', 'treatment.csv')
symptoms_lst = list(g.get_all_vertices(kind='symptom'))
user_symptoms = set()


class Interface:
    def __init__(self, root):
        self.root = root
        self.start_screen()

    def search(self, event):
        combo_box = event.widget
        value = event.widget.get()
        if value == '':
            combo_box['values'] = symptoms_lst
        else:
            filtered_symptoms = []
            for item in symptoms_lst:
                if value.lower() in item:
                    filtered_symptoms.append(item)
            combo_box['values'] = filtered_symptoms

    def show_value(self, event):
        value = event.widget.get()
        if value in symptoms_lst:
            if value not in user_symptoms:
                label2 = Label(self.root, text='Selected symptom: ' + value)
                label2.pack()
                user_symptoms.add(value)
            else:
                label2 = Label(self.root, text='You already selected ' + value + '!')
                label2.pack()
                self.root.after(3000, label2.destroy)
        else:
            label2 = Label(self.root, text='Error: Symptom not found.')
            label2.pack()
            self.root.after(3000, label2.destroy)
        event.widget.delete(0, 'end')

    def done(self):
        if user_symptoms == set():
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
            button4 = Button(self.root, text='Exit', command=self.root.destroy)
            button4.pack()

    def visualize(self):
        visualize_graph(g, symptoms=user_symptoms)

    def diagnosis(self):
        for w in self.root.winfo_children():
            w.destroy()
        e1 = Entry(self.root)
        e1.insert(0,'How many possible diseases?')
        e1.pack()
        b1 = Button(self.root, text='Diagnose me!', command=lambda: self.show_diagnosis(e1))
        b1.pack()

    def show_diagnosis(self, e1):
        num = e1.get()
        if num.isnumeric() and int(num) > 0:
            for w in self.root.winfo_children():
                w.destroy()
            diseases = g.predict_diseases(user_symptoms, int(num))
            for disease in diseases:
                lb = Label(self.root, text=str(round(disease[1] * 100, 2)) + '% chance of ' + disease[0])
                lb.pack()
            b = Button(self.root, text='Back', command=self.done)
            b.pack()
        else:
            lb = Label(self.root, text='Error: Number of possible diseases must be a number.')
            lb.pack()

    def treatment(self):
        for w in self.root.winfo_children():
            w.destroy()
        e1 = Entry(self.root)
        e1.insert(0, 'How many possible treatments?')
        e1.pack()
        b1 = Button(self.root, text='Treat me!', command=lambda: self.show_treatment(e1))
        b1.pack()

    def show_treatment(self, e1):
        num2 = e1.get()
        if num2.isnumeric() and int(num2) > 0:
            for w in self.root.winfo_children():
                w.destroy()
            treatments = g.predict_treatments(user_symptoms, int(num2))
            for treatment in treatments:
                lb = Label(self.root, text=str(round(treatment[1] * 100, 2)) + '% chance of ' + treatment[0])
                lb.pack()
            b = Button(self.root, text='Back', command=self.done)
            b.pack()
        else:
            lb = Label(self.root, text='Error: Number of possible treatments must be a number.')
            lb.pack()

    def start_screen(self):
        label = Label(self.root, text='Search your symptoms')
        label.pack()

        combo_box = ttk.Combobox(self.root, values=symptoms_lst)

        combo_box.set('Search')
        combo_box.pack()
        combo_box.bind('<KeyRelease>', self.search)
        combo_box.bind('<Return>', self.show_value)

        button = Button(self.root, text='I have finished entering symptoms.', command=self.done)
        button.pack()


if __name__ == '__main__':
    import python_ta

    python_ta.check_all(config={
        'max-line-length': 120,
        'disable': ['static_type_checker'],
        'allow-local-imports': True,
        'max-nested-blocks': 4
    })
