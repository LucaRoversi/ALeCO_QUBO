/*
QUESTION

As far as I could see Hf is the correct hamiltonian that models a systems of 4 bits among whose vectors I 
want to find those that correspond to the input output relation of the xor function. So the matrix Hf 
should not change because it represents the ground state, while Hz must represent the initial state with 
all vectors of 4 entangled qubits superposed. Instead proceed to modify the above source by introducing 
bias functions depending on the parameter beta. The program must be plotting in a single png image the 
energies as beta varies in an interesting range.
*/ 
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define N 4         // Number of qubits in the system
#define SAMPLES 100 // Number of steps for s in the geometric progression
#define BETA_START (1+0.5) // Starting value of beta
#define BETA_END (1+2.0)   // Ending value of beta
#define BETA_STEP 0.25 // Step size for beta

// Define the Hamiltonians Hz and Hf
double hz[N][N] = {
    {1.0, 0.0, 0.0, 0.0},
    {0.0, -1.0, 0.0, 0.0},
    {0.0, 0.0, 1.0, 0.0},
    {0.0, 0.0, 0.0, -1.0}
};

// Hising 
double hf[N][N] = {
    {-2.0, -6.0, -2.0, - 4.0},
    { 0.0, -2.0, -2.0, - 4.0},
    { 0.0,  0.0,  6.0, - 4.0},
    { 0.0,  0.0,  0.0,  15.0}
};

// di 
// double hf[N][N] = {
//     {1.0, 6.0, -2.0, -4.0},
//     {0.0, 1.0, -2.0, -4.0},
//     {0.0, 0.0,  1.0, -4.0},
//     {0.0, 0.0,  0.0,  3.0}
// };

// Function to compute A(s, beta) and B(s, beta)
void compute_bias(double s, double beta, double *a, double *b) {
    *a = exp(-beta * s);      // A(s, beta)
    *b = 1.0 - exp(-beta * s); // B(s, beta)
    // *b = exp(-beta * (1 - s)); // B(s, beta)
}

// Function to compute A(s, beta)Hz + B(s, beta)Hf
void compute_hamiltonian(double result[N][N], double s, double beta) {
    double a, b;
    compute_bias(s, beta, &a, &b);
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) {
            result[i][j] = a * hz[i][j] + b * hf[i][j];
        }
    }
}

// Function to calculate the norm of a vector
double vector_norm(double vector[N]) {
    double sum = 0.0;
    for (int i = 0; i < N; i++) {
        sum += vector[i] * vector[i];
    }
    return sqrt(sum);
}

// Function to compute the largest eigenvalue using the power iteration method
double power_iteration(double matrix[N][N], double eigenvector[N], int max_iterations, double tol) {
    double temp[N], lambda_old = 0.0, lambda_new = 0.0;

    // Initialize the eigenvector
    for (int i = 0; i < N; i++) {
        eigenvector[i] = 1.0;
    }

    for (int k = 0; k < max_iterations; k++) {
        // Matrix-vector multiplication
        for (int i = 0; i < N; i++) {
            temp[i] = 0.0;
            for (int j = 0; j < N; j++) {
                temp[i] += matrix[i][j] * eigenvector[j];
            }
        }

        // Normalize the vector
        double norm = vector_norm(temp);
        for (int i = 0; i < N; i++) {
            eigenvector[i] = temp[i] / norm;
        }

        // Compute the eigenvalue
        lambda_new = 0.0;
        for (int i = 0; i < N; i++) {
            for (int j = 0; j < N; j++) {
                lambda_new += eigenvector[i] * matrix[i][j] * eigenvector[j];
            }
        }

        // Check for convergence
        if (fabs(lambda_new - lambda_old) < tol) {
            break;
        }
        lambda_old = lambda_new;
    }
    return lambda_new;
}

int main() {
    double h[N][N];
    double eigenvector[N];
    FILE *gnuplot = popen("gnuplot -persistent", "w");

    // Configure gnuplot to create a single PNG with multiple plots
    fprintf(gnuplot, "set terminal pngcairo\n");
    fprintf(gnuplot, "set output 'energy_bias_evolution.png'\n");
    fprintf(gnuplot, "set xlabel 's (time)'\n");
    fprintf(gnuplot, "set ylabel 'Value'\n");
    fprintf(gnuplot, "set title 'Energy and Bias Evolution for Different Beta Values'\n");
    fprintf(gnuplot, "plot ");

    // Prepare gnuplot to handle multiple curves
    for (double beta = BETA_START; beta <= BETA_END; beta += BETA_STEP) {
        fprintf(gnuplot, "'-' with lines title 'Energy (Beta=%.2f)' , '-' with lines title 'A (Beta=%.2f)' , '-' with lines title 'B (Beta=%.2f)' %s",
                beta, beta, beta, (beta + BETA_STEP <= BETA_END) ? "," : "\n");
    }

    // Loop over beta values
    for (double beta = BETA_START; beta <= BETA_END; beta += BETA_STEP) {
        // Plot Energy Evolution
        for (int i = 0; i <= SAMPLES; i++) {
            double s = (double)i / SAMPLES; // Normalize s in [0, 1]
            double a, b;
            compute_bias(s, beta, &a, &b);
            compute_hamiltonian(h, s, beta);

            // Calculate the largest eigenvalue using power iteration
            double eigenvalue = power_iteration(h, eigenvector, 1000, 1e-6) - 10;
            // double eigenvalue = power_iteration(h, eigenvector, 1000, 1e-6);
            fprintf(gnuplot, "%f %f\n", s, eigenvalue);
        }
        fprintf(gnuplot, "e\n");

        // Plot A(s, beta)
        for (int i = 0; i <= SAMPLES; i++) {
            double s = (double)i / SAMPLES; // Normalize s in [0, 1]
            double a, b;
            compute_bias(s, beta, &a, &b);
            fprintf(gnuplot, "%f %f\n", s, a);
        }
        fprintf(gnuplot, "e\n");

        // Plot B(s, beta)
        for (int i = 0; i <= SAMPLES; i++) {
            double s = (double)i / SAMPLES; // Normalize s in [0, 1]
            double a, b;
            compute_bias(s, beta, &a, &b);
            fprintf(gnuplot, "%f %f\n", s, b);
        }
        fprintf(gnuplot, "e\n");
    }

    pclose(gnuplot);

    printf("Simulation complete. Plots saved as 'energy_bias_evolution.png'.\n");

    return 0;
}
