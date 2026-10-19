#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <complex.h>

#define N 16 // 2^4: Dimension of the Hilbert space for 4 qubits
#define SAMPLES 100 // Number of time steps
#define BETA_START 0.5
#define BETA_END 2.0
#define BETA_STEP 0.25

/*
IN this version the energy of the ISING model increases as the value of beta increases.
Here below some possible motivations. 

1. **Behavior of Energy with Increasing Beta**:
   - The energy increases as beta grows, which is linked to the dynamic interplay of the Hamiltonians \( H_z \) and \( H_f \), and the time-dependent coefficients \( A(s, \beta) \) and \( B(s, \beta) \).

2. **Reasons for Energy Increase**:
   - **Contribution of \( H_z \):**
     \( H_z \) is associated with the initial state in superposition. As beta increases, \( A(s, \beta) = e^{-\beta s} \) decays faster, reducing the influence of \( H_z \), which might correspond to lower-energy configurations.
   - **Contribution of \( H_f \):**
     \( H_f \) represents the Ising Hamiltonian, which dominates as \( B(s, \beta) = 1 - e^{-\beta s} \) grows with beta. If the system hasn't yet transitioned to the ground state of \( H_f \), the energy can temporarily increase as higher-energy configurations are explored.
   - **Non-Adiabatic Evolution:**
     The evolution isn't fully adiabatic (slow). Non-adiabatic transitions can lead the system to populate higher-energy states rather than smoothly converging to the ground state.
   - **Alignment of States:**
     The initial state may not perfectly align with the low-energy subspace of \( H_f \), requiring the system to explore higher-energy configurations during the evolution process.

3. **Understanding the System Behavior**:
   - This behavior aligns with practical challenges in quantum simulations and optimization, where intermediate states often exhibit higher energy.
   - Further adjustments to \( A(s, \beta) \) and \( B(s, \beta) \), as well as the dynamics of \( H_z \) and \( H_f \), can potentially mitigate this increase.

4. **Future Directions**:
   - Increasing the number of simulation steps might approximate more adiabatic evolution, ensuring smoother energy transitions.
   - Refinements to the initial state or \( H_z \) could better align the system with the low-energy subspace of \( H_f \).
*/

void initialize_superposition(complex double state[N]) {
    // Initialize the state vector with equal amplitudes for all basis states
    for (int i = 0; i < N; i++) {
        state[i] = 1.0 / sqrt(N); // Equal amplitude
    }
}

// Apply H_z operator (Pauli-X equivalent for superposition dynamics)
void apply_hz(complex double hz[N][N]) {
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) {
            hz[i][j] = (i == j) ? 0.0 : 1.0; // Off-diagonal flips
        }
    }
}

// Apply H_f operator (Ising Hamiltonian)
void apply_hf(double hf[N][N]) {
    double hf_raw[4][4] = {
        {-2.0, -6.0, -2.0, -4.0},
        { 0.0, -2.0, -2.0, -4.0},
        { 0.0,  0.0,  6.0, -4.0},
        { 0.0,  0.0,  0.0, 15.0}
    };

    // Expand the Ising H_f to match the full Hilbert space dimension
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
    fprintf(gnuplot, "set output 'quantum_evolution_ising.png'\n");
    fprintf(gnuplot, "set xlabel 's (time)'\n");
    fprintf(gnuplot, "set ylabel 'Energy'\n");
    fprintf(gnuplot, "set title 'Quantum Evolution with Ising Hamiltonian'\n");
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

    printf("Simulation complete. Energy plots saved as 'quantum_evolution_ising.png'.\n");

    return 0;
}
