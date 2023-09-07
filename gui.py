import tkinter as tk
import tkinter.ttk as ttk

# Classe pour gérer chaque onglet
class Onglet:
    def __init__(self, parent, nom):
        self.nom = nom
        self.frame = ttk.Frame(parent)
        self.tableau = ttk.Treeview(self.frame)  # Création d'un tableau (Treeview) dans l'onglet
        self.tableau.pack(fill='both', expand=True)  # Configuration du tableau pour remplir l'onglet

        # Configuration des colonnes du tableau
        self.tableau["columns"] = (
            "Colonne 1", "Colonne 2", "Colonne 3", "Colonne 4", "Colonne 5",
            "Colonne 6", "Colonne 7", "Colonne 8", "Colonne 9"
        )
        
        
        for colonne in self.tableau["columns"]:
            self.tableau.column(colonne, anchor=tk.W)
        self.tableau.column("#0", width=0, stretch=tk.NO)

        # Configuration des en-têtes de colonnes
        self.tableau.heading("#0", text="", anchor=tk.W)
        self.tableau.heading("Colonne 1", text="Localisation", anchor=tk.W)
        self.tableau.heading("Colonne 2", text="Type de bien", anchor=tk.W)
        self.tableau.heading("Colonne 3", text="Prix", anchor=tk.W)
        self.tableau.heading("Colonne 4", text="Surface", anchor=tk.W)
        self.tableau.heading("Colonne 5", text="Pièces", anchor=tk.W)
        self.tableau.heading("Colonne 6", text="DPE", anchor=tk.W)
        self.tableau.heading("Colonne 7", text="Balcon", anchor=tk.W)
        self.tableau.heading("Colonne 8", text="Jardin", anchor=tk.W)
        self.tableau.heading("Colonne 9", text="Garage", anchor=tk.W)

# Classe principale de l'application
class App(tk.Tk):
    def __init__(self):
        super(App, self).__init__()

        # Création du widget Notebook pour les onglets
        self.onglets = ttk.Notebook(self)
        self.onglets.pack(fill='both', expand=True)

        # Crée l'onglet initial
        self.creer_onglet_initial()

        # Crée un bouton pour ajouter des onglets
        self.bouton_ajout = tk.Button(self, text="Ajouter un onglet", command=self.ajouter_onglet)
        self.bouton_ajout.pack()

    def creer_onglet_initial(self):
        # Crée l'onglet initial avec l'instance de la classe Onglet
        self.onglet1 = Onglet(self.onglets, "Onglet 1")
        self.onglets.add(self.onglet1.frame, text=self.onglet1.nom)

    def ajouter_onglet(self):
        # Ajoute un nouvel onglet avec un nom incrémenté
        nouvel_onglet = Onglet(self.onglets, f'Onglet {self.onglets.index("end") + 1}')
        self.onglets.add(nouvel_onglet.frame, text=nouvel_onglet.nom)

# Point d'entrée de l'application
if __name__ == '__main__':
    App().mainloop()
