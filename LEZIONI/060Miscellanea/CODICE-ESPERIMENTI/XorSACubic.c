#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>

#define N 3 // Numero di qubit (3 per terne)
#define RUN 10
#define ANNEAL_STEPS 4 //  // temperatura
#define ALPHA 0.69
#define BETA 0.7
#define FREQ (int)pow(2,N)

double TLinear (double t) {
    return t - ALPHA;
}
double TGeometric (double t) {
    return t * ALPHA;
}

double TSlow (double t) {
    return t/(t + t * BETA);
}

int energyCubic(int E_node[N]) {
    int r =    E_node[0] //x
           +   E_node[1] //y
           +   E_node[2] //z
           - 2*E_node[0]*E_node[1] //-2xy
           - 2*E_node[0]*E_node[2] //-2xz
           - 2*E_node[1]*E_node[2] //-2yz
           + 4*E_node[0]*E_node[1]*E_node[2]; //+4xyz
    return r;
}

// Funzione di simulazione di annealing
void simulated_annealing(int E_node[N], int path[ANNEAL_STEPS][N], int *path_length) {
    double temperature = 1.0;
    double E_node_Energy = energyCubic(E_node);

    for (int t = 0; t < ANNEAL_STEPS; t++) {
        /* Il cammino si volge in una clique in cui ogni nodo è 
           un neighbour potenziale                             */
        int Neighbour[N] = {rand() % 2, rand() % 2, rand() % 2};
        double Neighbour_Energy = energyCubic(Neighbour);
        if (Neighbour_Energy <= E_node_Energy) {
            /*  Se l'energia dell'attuale E_node non è strettamente 
                inferiore a quella del neighbour, allora si assegna 
                lo stato di E_node al neighbour. 
                
                Si privilegia il cambiamento: si cambia E_node anche 
                a parità di energia.             */
            for (int i = 0; i < N; i++) {
                     E_node[i] = Neighbour[i];
                 }
        }
        if (Neighbour_Energy > E_node_Energy) {
            /*  Se l'energia dell'attuale E_node è strettamente 
                inferiore a quella del neighbour, allora occorre 
                decidere se sostituire l'attuale E_node col 
                neighbour.
                
                In questa situazione, il criterio generale è che
                più la temperatura scende, 
                meno si tende a voler usare il neighbor come prossimo 
                E_node.  */
            double threshold_upper_bound = 
                   1/(exp((Neighbour_Energy - E_node_Energy) / temperature));

            if ( ((double) rand() / RAND_MAX) < threshold_upper_bound) {
                /*  Se l'estrazione da una distribuzione uniforme fornisce
                    un valore inferiore alla soglia, allora il neighbour 
                    diventa il nuovo E_node.

                    La scelta è coerente con l'idea che se la soglia di 
                    cambiamento si abbassa per via del raffreddamento,
                    la probabilità di cambiare deve calare.      */
                for (int i = 0; i < N; i++) {
                    E_node[i] = Neighbour[i];
                }
            }
        }
        // Salva lo stato attuale nel percorso
        for (int i = 0; i < N; i++) {
                path[*path_length][i] = E_node[i];
        }
        (*path_length)++;
        
        temperature = TGeometric (temperature);
    }
}

int bin2dec(const int E_node[N]) {
    int d = 0;
    for (int i = 0; i < N; i++) {
        d = d + E_node[i] * (int)pow(2,N - i - 1);
    }
    return d;
}

int main() {
    srand(time(0));
    for (int n = 0; n < RUN; n++) {

        int E_nodeFrequency[FREQ];
        for (int i = 0; i < FREQ; i++) {
            E_nodeFrequency[i] = 0;
        }
        
        for (int times = 0; times < 100; times++) {
            int E_node[N] = {rand() % 2, rand() % 2, rand() % 2};
            // Memorizza: 
            int path[ANNEAL_STEPS][N];
            int path_length = 0;

            simulated_annealing(E_node, path, &path_length);

            // Aggiorna la frequenza degli E_node finali
            // cioè del 'Best state'
            E_nodeFrequency[bin2dec(E_node)]++;
        }
        printf("Frequenza del 'Best state': [");
        int s = 0;
        for (int i = 0; i < FREQ; i++) {
            printf("%2d", E_nodeFrequency[i]);
            s += E_nodeFrequency[i];
            if (i < FREQ - 1) {
                printf(", ");
            }
        }
        printf("] con %.2f di positivi\n", 
               (E_nodeFrequency[0]
               +E_nodeFrequency[3]
               +E_nodeFrequency[5]
               +E_nodeFrequency[6])/100.0f);
        }

    return 0;
}