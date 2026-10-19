#include <stdio.h>
#include <math.h>
#include <stdlib.h>

int main() {
    FILE *dataFile, *gnuplotFile;
    double delta;
    double t;
    int i;

    // Create a data file to store values
    dataFile = fopen("data.txt", "w");
    if (!dataFile) {
        perror("Failed to open data file");
        return 1;
    }

    // Write the data for plotting
    for (delta = 0; delta <= 10; delta += 0.5) {
        for (t = 1.0; t > 0; t -= 0.10) {
            double value = 1.0 / exp(delta / t);
            fprintf(dataFile, "%.1f %.2f %.5f\n", delta, t, value);
        }
        fprintf(dataFile, "\n"); // Blank line for gnuplot to distinguish sets
    }
    fclose(dataFile);

    // Generate four images with different rotations
    for (i = 0; i < 4; i++) {
        char filename[50];
        sprintf(filename, "plot%d.gnuplot", i);

        gnuplotFile = fopen(filename, "w");
        if (!gnuplotFile) {
            perror("Failed to open gnuplot script file");
            return 1;
        }

        fprintf(gnuplotFile, 
            "set terminal pngcairo size 800,600\n"
            "set output 'plot%d.png'\n"
            "set title '1/exp(delta / t) Function Plots'\n"
            "set xlabel 'delta'\n"
            "set ylabel 't'\n"
            "set zlabel '1/exp(delta / t)'\n"
            "set grid\n"
            "set view %d, 30\n" // Rotate view horizontally
            "splot 'data.txt' using 1:2:3 with linespoints title '1/exp(delta / t)'\n",
            i, 60 - (i * 10)
        );
        fclose(gnuplotFile);

        // Execute gnuplot
        char command[100];
        sprintf(command, "gnuplot plot%d.gnuplot", i);
        if (system(command) != 0) {
            fprintf(stderr, "Error: Failed to execute gnuplot\n");
            return 1;
        }
    }

    printf("Generated 4 plots with varying horizontal rotations. Check the output images.\n");

    return 0;
}
