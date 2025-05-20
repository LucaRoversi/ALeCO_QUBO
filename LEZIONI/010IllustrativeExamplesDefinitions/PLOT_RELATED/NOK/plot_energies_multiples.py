import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def plot_energies_multiples(sample_sets, titles):
    fig, axs = plt.subplots(len(sample_sets), figsize=(10,5*len(sample_sets)))

    for ax, sample_set, title in zip(axs, sample_sets, titles):
        # Prepare the data
        data = []
        for sample, energy in zip(sample_set.samples(), sample_set.record.energy):
            # Get the values of all columns
            values = [sample[var_label] for var_label in sample_set.variables]
            # Append the values and the energy to the data list
            values.append(energy)
            data.append(values)

        # Convert the data list to a DataFrame
        df = pd.DataFrame(data, columns=list(sample_set.variables) + ['E'])

        # Create a new column for all combinations of the values from all columns except the last one
        df['combined'] = df[df.columns[:-1]].apply(lambda row: ', '.join(row.values.astype(str)), axis=1)

        # Create a scatter plot with the energy on the x-axis and the combinations of variables on the y-axis
        ax.scatter(df['E'], df['combined'])
        ax.set_xlabel('Energy')
        ax.set_ylabel('Combinations of Variables')
        ax.set_title(title)

    # Display the figure
    plt.tight_layout()
    plt.show()
