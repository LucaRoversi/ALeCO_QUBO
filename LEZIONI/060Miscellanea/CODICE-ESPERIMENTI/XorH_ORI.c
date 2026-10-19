#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <complex.h>
#include <time.h>

#define N 3 // Numero di qubit
#define ITERATIONS 1000 // Numero di iterazioni per l'evoluzione temporale
#define DT 0.01 // Passo temporale

// Funzione per moltiplicare matrici 3x3 complesse
void matrix_multiply(complex double result[N][N], complex double a[N][N], complex double b[N][N]) {
    complex double temp[N][N];
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) {
            temp[i][j] = 0;
            for (int k = 0; k < N; k++) {
                temp[i][j] += a[i][k] * b[k][j];
            }
        }
    }
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) {
            result[i][j] = temp[i][j];
        }
    }
}

// Funzione per evolvere lo stato nel tempo e calcolare l'energia
double evolve_state(complex double state[N], complex double hamiltonian[N][N], double dt) {
    complex double i_hamiltonian[N][N];
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) {
            i_hamiltonian[i][j] = -I * hamiltonian[i][j] * dt;
        }
    }

    complex double temp_state[N];
    for (int i = 0; i < N; i++) {
        temp_state[i] = 0;
        for (int j = 0; j < N; j++) {
            temp_state[i] += i_hamiltonian[i][j] * state[j];
        }
    }

    for (int i = 0; i < N; i++) {
        state[i] += temp_state[i];
    }

    // Calcolo dell'energia
    complex double energy = 0;
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) {
            energy += conj(state[i]) * hamiltonian[i][j] * state[j];
        }
    }
    return creal(energy);
}

int main() {
    srand(time(0));

    // Matrice di Pauli sigma_z di dimensione 3x3 (estensione di Pauli per qubit multipli)
    complex double sigma_z[N][N] = {
        {1, 0, 0},
        {0, -1, 0},
        {0, 0, 1}
    };

    // Hamiltoniana Hx (matrice triangolare superiore)
    complex double Hx[N][N] = {
        {0, 1, 1},
        {0, 0, 1},
        {0, 0, 0}
    };

    // Stato iniziale (superposizione)
    complex double state[N] = {1.0 / sqrt(3), 1.0 / sqrt(3), 1.0 / sqrt(3)};

    // Parametri dell'Hamiltoniana
    double A = 1.0, B = 0.1;

    // File per memorizzare l'evoluzione dell'energia
    FILE *energy_file = fopen("energy_evolution.dat", "w");
    if (energy_file == NULL) {
        fprintf(stderr, "Errore nell'apertura del file.\n");
        return 1;
    }

    for (int iter = 0; iter < ITERATIONS; iter++) {
        // Aggiorna i parametri A e B
        double s = (double)iter / ITERATIONS;
        double a_s = A * (1.0 - s);
        double b_s = B * s;

        // Hamiltoniana combinata
        complex double hamiltonian[N][N];
        for (int i = 0; i < N; i++) {
            for (int j = 0; j < N; j++) {
                hamiltonian[i][j] = a_s * sigma_z[i][j] + b_s * Hx[i][j];
            }
        }

        // Evoluzione dello stato e calcolo dell'energia
        double energy = evolve_state(state, hamiltonian, DT);
        fprintf(energy_file, "%d %lf\n", iter, energy);
    }

    fclose(energy_file);

    // Risultato finale
    printf("Stato finale: [");
    for (int i = 0; i < N; i++) {
        printf("%lf + %lfi", creal(state[i]), cimag(state[i]));
        if (i < N - 1) {
            printf(", ");
        }
    }
    printf("]\n");

    printf("L'evoluzione dell'energia è stata salvata nel file 'energy_evolution.dat'.\n");

    return 0;
}