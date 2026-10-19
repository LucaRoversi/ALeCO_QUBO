/*
QUESTION
I am interested to C a program X.
The C program X must define two hamiltonian.
The hamiltonian Hx must be
    double hx[N][N] = {
        {1.0, 0.0, 0.0, 0.0},
        {0.0, -1.0, 0.0, 0.0},
        {0.0, 0.0, 1.0, 0.0},
        {0.0, 0.0, 0.0, -1.0}
    };
The hamiltonian Hf must be:

    double hf[N][N] = {
        {1.0, 6.0, -2.0, -4.0},
        {0.0, 1.0, -2.0, -4.0},
        {0.0, 0.0,  1.0, -4.0},
        {0.0, 0.0,  0.0,  3.0}
    };
First the C program X must compute and plot using gnuplot the evolution of the energy represented by  A(s)Hx+B(s)Hf where 𝐴(𝑠)=1−𝑠, (𝑠=𝑠) with s from 0 to 1.
Second the C program X must compute the eigenvalues of the Hamiltonian matrix without relying on the external LAPACK library.
The C program X must use simple numerical methods like the power iteration algorithm.
Third the C program X must include a section that plots eigenvectors and eigenvalues, possibly in separated plots, according to some standard visualization methods for eigenvalues and eigenvectors possibly by means of gnuplot.
The explanation about how the C program X works must be inserted in the source as comments.
*/

#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define N 4 // Size of the Hamiltonian matrix
#define SAMPLES 100 // Number of samples for plotting
// #define ALPHA 0.69
#define ALPHA 0.6

double TGeometric (double t, double alpha) {
    return t * alpha;
}

// Define the Hamiltonians
double hx[N][N] = {
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

// double hf[N][N] = {
//     {1.0, 1.0,  1.0, 1.0},
//     {0.0, 1.0,  1.0, 1.0},
//     {0.0, 0.0,  1.0, 1.0},
//     {0.0, 0.0,  0.0, 1.0}
// };



// Function to compute A(s)Hx + B(s)Hf
void compute_hamiltonian(double result[N][N], double s) {
    double a = s; // A(s)
    double b = 1.0 - s;       // B(s)
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) {
            result[i][j] = a * hx[i][j] + b * hf[i][j];
        }
    }
}

// Power iteration algorithm to find the largest eigenvalue
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
        double norm = 0.0;
        for (int i = 0; i < N; i++) {
            norm += temp[i] * temp[i];
        }
        norm = sqrt(norm);
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
    FILE *gnuplot = popen("\"C:\\Program Files\\gnuplot\\bin\\gnuplot.exe\" -persistent", "w");
    // FILE *gnuplot = _popen("gnuplot -persistent", "w");

    // Compute and plot the evolution of the energy
    fprintf(gnuplot, "set terminal pngcairo\n");
    fprintf(gnuplot, "set output 'energy_evolution.png'\n");
    fprintf(gnuplot, "set xlabel 's'\n");
    fprintf(gnuplot, "set ylabel 'Energy'\n");
    fprintf(gnuplot, "plot '-' with lines title 'Energy Evolution'\n");
    
    double s = 1;
    for (int i = 0; i <= SAMPLES; i++) {
        // double s = (double)i / SAMPLES;
        s = TGeometric (s, ALPHA);
        compute_hamiltonian(h, s);

        // Calculate the largest eigenvalue
        double eigenvector[N];
        double eigenvalue = power_iteration(h, eigenvector, 1000, 1e-6);
        fprintf(gnuplot, "%f %f\n", s, eigenvalue);
    }

    fprintf(gnuplot, "e\n");
    pclose(gnuplot);
    return 0;
}

/*
Hamiltonian Calculation: Combines Hx and Hf using the interpolation factor A(s) and B(s).

Energy Evolution: Computes and visualizes the energy changes as s varies from 0 to 1.

Eigenvalue Calculation: Implements the power iteration method for eigenvalue computation.
*/