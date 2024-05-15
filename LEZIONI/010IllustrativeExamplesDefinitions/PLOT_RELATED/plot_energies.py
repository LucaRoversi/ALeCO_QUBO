# Importiamo le librerie necessarie
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Definiamo la funzione plot_energies
def plot_energies(sample_set):
    # Prepariamo i dati
    data = []
    for sample, energy in zip(sample_set.samples(), sample_set.record.energy):
        # Valori di tutte le colonne
        values = [sample[var_label] for var_label in sample_set.variables]
        # Aggiunge valori e energia alla lista dei dati
        values.append(energy)
        data.append(values)

    # Conversione della lista dei dati in un DataFrame
    df = pd.DataFrame(data, columns=list(sample_set.variables) + ['E'])

    # Nuova colonna che combina i valori di tutte le colonne tranne l'ultima
    df['combined'] = df[df.columns[:-1]].apply(lambda row: ', '.join(row.values.astype(str)), axis=1)

    # Nuova figura con una dimensione specifica
    plt.figure(figsize=(10,5))
    # Grafico a dispersione con l'energia sull'asse x e le combinazioni di variabili sull'asse y
    plt.scatter(df['E'], df['combined'])
    # Etichetta asse x: 'Energy'
    plt.xlabel('Energy')
    # Etichetta sse y: 'Combinations of Variables'
    plt.ylabel('Combinations of Variables')
    # Titolo del grafico: 'Scatter Plot'
    plt.title('Scatter Plot')
    plt.show()
