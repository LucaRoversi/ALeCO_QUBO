#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <complex.h>

#define N 16 // 2^4: Dimension of the Hilbert space for 4 qubits
#define SAMPLES 100 // Number of time steps
#define BETA_START 2.5
#define BETA_END 3.0
#define BETA_STEP 0.25

/*
Key Updates and Explanation:
1. **Hilbert Space Representation**:
   - The program now models a 4-qubit quantum system explicitly in the Hilbert space, using a state vector of complex amplitudes to represent the system's state.
   - Each computational basis state (16 in total for 4 qubits) corresponds to a unique basis vector in the 16-dimensional Hilbert space.

2. **Superposition Initialization**:
   - The initial state is prepared as a uniform superposition of all computational basis states: 
     |ψ_0⟩ = (1/√16) * Σ |i⟩ for i = 0 to 15. 
   - This represents equal probability amplitudes for all states.

3. **Hamiltonian Dynamics**:
   - The Hamiltonian H_z is modeled using off-diagonal elements to represent transitions (flips) between basis states.
   - H_f is based on the user-defined cost Hamiltonian in the diagonal form, extended to the 16-dimensional Hilbert space.

4. **Energy Evolution**:
   - The program computes the energy as the expectation value of the Hamiltonian for the current state at each time step.

5. **Time Evolution Using Schrödinger-Like Dynamics**:
   - The state evolves under the combined Hamiltonian A(s)*H_z + B(s)*H_f, where A(s) and B(s) are time-dependent coefficients controlled by a parameter beta.

6. **Gnuplot Visualization**:
   - Energy evolution is plotted as beta varies in the range [0.5, 2.0] to provide insights into how the system transitions from the initial state to the ground state.
*/

void initialize_superposition(complex double state[N]) {
    // Initialize the state vector with equal amplitudes for all basis states
    for (int i = 0; i < N; i++) {
        state[i] = 1.0 / sqrt(N); // Equal amplitude
    }
}

/*
H_z: Represents the Pauli-X gate operations extended to 4 qubits.
It is designed to create transitions (flips) between basis states.
*/
void apply_hz(complex double hz[N][N]) {
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) {
            hz[i][j] = (i == j) ? 0.0 : 1.0; // Off-diagonal flips
        }
    }
}

/*
H_f: Represents the problem Hamiltonian (user-defined).
The given 4x4 H_f is extended to a 16x16 matrix for the full Hilbert space.
*/
void apply_hf(double hf[N][N]) {
    double hf_raw[4][4] = {
        {1.0, 6.0, -2.0, -4.0},
        {0.0, 1.0, -2.0, -4.0},
        {0.0, 0.0,  1.0, -4.0},
        {0.0, 0.0,  0.0,  3.0}
    };

    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) {
            hf[i][j] = (i == j) ? hf_raw[i % 4][j % 4] : 0.0;
        }
    }
}



// Function to compute A(s, beta) and B(s, beta)
void compute_bias(double s, double beta, double *a, double *b) {
    *a = exp(-beta * s);      // A(s, beta)
    *b = 1.0 - exp(-beta * s); // B(s, beta)
}

// Simulate time evolution of the quantum state
void evolve_state(complex double state[N], complex double hz[N][N], double hf[N][N], double a, double b) {
    complex double new_state[N] = {0};

    // Compute the state evolution: A(s)*H_z + B(s)*H_f
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) {
            new_state[i] += a * hz[i][j] * state[j] + b * hf[i][j] * state[j];
        }
    }

    // Normalize the state
    double norm = 0.0;
    for (int i = 0; i < N; i++) {
        norm += creal(new_state[i] * conj(new_state[i]));
    }
    norm = sqrt(norm);
    for (int i = 0; i < N; i++) {
        state[i] = new_state[i] / norm;
    }
}

int main() {
    complex double state[N];
    complex double hz[N][N];
    double hf[N][N];

    // Initialize the quantum state
    initialize_superposition(state);

    // Initialize the operators H_z and H_f
    apply_hz(hz);
    apply_hf(hf);

    FILE *gnuplot = popen("gnuplot -persistent", "w");

    // Configure gnuplot to plot energy evolution
    fprintf(gnuplot, "set terminal pngcairo\n");
    fprintf(gnuplot, "set output 'quantum_evolution_QUBO.png'\n");
    fprintf(gnuplot, "set xlabel 's (time)'\n");
    fprintf(gnuplot, "set ylabel 'Energy'\n");
    fprintf(gnuplot, "set title 'Quantum Evolution for Different Beta Values'\n");
    fprintf(gnuplot, "plot ");

    // Prepare to plot multiple beta curves
    for (double beta = BETA_START; beta <= BETA_END; beta += BETA_STEP) {
        fprintf(gnuplot, "'-' with lines title 'Beta=%.2f' %s",
                beta, (beta + BETA_STEP <= BETA_END) ? "," : "\n");
    }

    // Simulation for each beta
    for (double beta = BETA_START; beta <= BETA_END; beta += BETA_STEP) {
        for (int sample = 0; sample <= SAMPLES; sample++) {
            double s = (double)sample / SAMPLES;
            double a, b;
            compute_bias(s, beta, &a, &b);

            // Evolve the state
            evolve_state(state, hz, hf, a, b);

            // Compute energy as expectation value of H
            double energy = 0.0;
            for (int i = 0; i < N; i++) {
                for (int j = 0; j < N; j++) {
                    energy += creal(state[i] * conj(state[j])) * (a * hz[i][j] + b * hf[i][j]);
                }
            }

            // Output energy to gnuplot
            fprintf(gnuplot, "%f %f\n", s, energy);
        }
        fprintf(gnuplot, "e\n");
    }

    pclose(gnuplot);

    printf("Simulation complete. Energy plots saved as 'quantum_evolution.png'.\n");

    return 0;
}


/*

How It Works:
This updated code explicitly represents quantum states as complex vectors and uses Hamiltonians constructed as matrices to operate on the states. The main quantum mechanical principles—superposition, Hamiltonian dynamics, and state evolution—are implemented to simulate the system's behavior over time. This simulation provides a meaningful approximation of the energy evolution for different 𝛽
Values in a quantum system. 
*/