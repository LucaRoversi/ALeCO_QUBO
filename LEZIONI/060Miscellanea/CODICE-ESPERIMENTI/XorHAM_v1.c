#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define N 4         // Number of qubits in the system
#define SAMPLES 100 // Number of steps for s in the geometric progression
#define ALPHA_START 0.6 // Starting value of ALPHA
#define ALPHA_END 0.8   // Ending value of ALPHA
#define ALPHA_STEP 0.05 // Step size for ALPHA

// Key Changes and Features:
// 1. Geometric Function for s: Instead of a linear progression, s now follows a geometric progression defined by s = 1 - alpha^i,
//    where alpha is a parameter controlling the progression.
// 2. Multi-Curve Plotting: The program generates a single PNG plot that contains the energy evolution curves for all alpha values in the interval [0.6, 0.8].
// 3. Power Iteration Algorithm: Uses a basic numerical method (power iteration) to find the largest eigenvalue of the Hamiltonian at each step,
//    avoiding the need for external libraries like LAPACK.
// 4. Gnuplot Integration: Outputs a plot of the energy evolution, labeling each curve with its corresponding alpha value.

// Define the Hamiltonians Hz and Hf
double hz[N][N] = {
    {1.0, 0.0, 0.0, 0.0},
    {0.0, -1.0, 0.0, 0.0},
    {0.0, 0.0, 1.0, 0.0},
    {0.0, 0.0, 0.0, -1.0}
};

double hf[N][N] = {
    {1.0, 6.0, -2.0, -4.0},
    {0.0, 1.0, -2.0, -4.0},
    {0.0, 0.0,  1.0, -4.0},
    {0.0, 0.0,  0.0,  3.0}
};

// Function to compute A(s)Hz + B(s)Hf
void compute_hamiltonian(double result[N][N], double s) {
    double a = 1.0 - s; // A(s)
    double b = s;       // B(s)
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
    double temp[N], lambda_old = 0.0, lambda_new  = 0.0;

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
    fprintf(gnuplot, "set output 'energy_evolution_multiple_alpha.png'\n");
    fprintf(gnuplot, "set xlabel 's (geometric progression)'\n");
    fprintf(gnuplot, "set ylabel 'Energy (Eigenvalue)'\n");
    fprintf(gnuplot, "set title 'Energy Evolution for Different ALPHA Values'\n");
    fprintf(gnuplot, "plot ");

    // Prepare gnuplot to handle multiple curves
    for (double alpha = ALPHA_START; alpha <= ALPHA_END; alpha += ALPHA_STEP) {
        fprintf(gnuplot, "'-' with lines title 'ALPHA=%.2f'%s ", alpha, (alpha + ALPHA_STEP <= ALPHA_END) ? "," : "\n");
    }

    // Loop over ALPHA values
    for (double alpha = ALPHA_START; alpha <= ALPHA_END; alpha += ALPHA_STEP) {
        // Compute the geometric progression of s
        for (int i = 0; i <= SAMPLES; i++) {
            double s = 1.0 - pow(alpha, i); // Geometric progression formula

            // Ensure s is clamped to the range [0, 1]
            if (s > 1.0) s = 1.0;
            if (s < 0.0) s = 0.0;

            compute_hamiltonian(h, s);

            // Calculate the largest eigenvalue using power iteration
            double eigenvalue = power_iteration(h, eigenvector, 1000, 1e-6);

            // Output the results to gnuplot
            fprintf(gnuplot, "%f %f\n", s, eigenvalue);
        }
        fprintf(gnuplot, "e\n");
    }

    pclose(gnuplot);

    printf("Simulation complete. Energy plots saved as 'energy_evolution_multiple_alpha.png'.\n");

    // How It Works:
    // 1. For each alpha in [0.6, 0.8], the program simulates Hamiltonian evolution using a geometric progression for s.
    // 2. For every s value, it computes the Hamiltonian and determines its largest eigenvalue using the power iteration method.
    // 3. Results are plotted in a single PNG, showing energy evolution curves for different alpha values.

    return 0;
}
