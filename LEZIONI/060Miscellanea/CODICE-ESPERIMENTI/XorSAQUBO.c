#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>

#define N 3 // Numero di qubit (3 per terne)
#define TRIALS 10
#define ANNEAL_STEPS 3 // temperatura
#define ALPHA 0.69
#define BETA 0.7
#define FREQ (int)pow(2,N+1)

double TLinear (double t) {
    return t - ALPHA;
}
double TGeometric (double t, double alpha) {
    return t * alpha;
}

double TSlow (double t) {
    return t/(t + t * BETA);
}

int P(int E_node[N+1]) {
    int r = 
     2*( 
         E_node[0]*E_node[1]               // xy
        -2*(E_node[0]+E_node[1])*E_node[3] //-2(x+y)w
        +3*E_node[3]                       //+3w
       );
    return r;
}

int energyQUBO(int E_node[N+1]) {
    int r =    
        E_node[0]              //x
    +   E_node[1]              //y
    +   E_node[2]              //z
    - 2*E_node[0]*E_node[1]    //-2xy
    - 2*E_node[0]*E_node[2]    //-2xz
    - 2*E_node[1]*E_node[2]    //-2yz
    + 4*( 
           E_node[3]*E_node[2] //wz
         + P(E_node)           //P
        ) 
    ;
    return 2*r;
}

void simulated_annealing( int E_node[N+1]
                        , FILE *pathFile) {
    double temperature = 1.0;
    double E_node_Energy = energyQUBO(E_node);

    for (int t = 0; t < ANNEAL_STEPS; t++) {
        /* Il cammino si volge in una clique in cui ogni nodo è 
           un neighbour potenziale.
           Occorre porre attenzione al fatto che la variabile
           z_{xy} deve sempre rappresentare il prodotto xy, quindi
           deve dipendere dalla scelta casuale dei valori in x e y */
        int Neighbour[N+1];
        Neighbour[0] = rand() % 2;                   //x
        Neighbour[1] = rand() % 2;                   //y
        Neighbour[2] = rand() % 2;                   //z
        Neighbour[3] = Neighbour[0] * Neighbour[1];  //z_{xy}

        double Neighbour_Energy = energyQUBO(Neighbour);
        double delta = Neighbour_Energy - E_node_Energy;
        double threshold_upper_bound 
                       = 1/exp(delta / temperature);

        fprintf( pathFile
               , "%d%d%d%d %.3f %.3f %.3f %.3f %.3f\n"
               , E_node[0], E_node[1], E_node[2], E_node[3]
               , temperature
               , E_node_Energy
               , Neighbour_Energy
               , delta
               , threshold_upper_bound 
              );

        if (delta <= 0) {
            /*  Se l'energia dell'attuale E_node non è strettamente 
                inferiore a quella del neighbour, allora si assegna 
                lo stato di E_node al neighbour. 
                
                Si privilegia il cambiamento: si cambia E_node anche 
                a parità di energia.  */
            for (int i = 0; i < N+1; i++) {
                E_node[i] = Neighbour[i];
            }
        }
        if (delta > 0) {
            /*  Se l'energia dell'attuale E_node è strettamente 
                inferiore a quella del neighbour, allora occorre 
                decidere se sostituire l'attuale E_node col 
                neighbour.
                
                In questa situazione, il criterio generale è che
                più la temperatura scende, 
                meno si tende a voler usare il neighbor come prossimo 
                E_node.  */
            if ( ((double) rand() / RAND_MAX) < threshold_upper_bound) {
                for (int i = 0; i < N+1; i++) {
                    E_node[i] = Neighbour[i];
                }
            }
        }
        temperature = TGeometric (temperature, ALPHA);
    }
}

int bin2dec(const int E_node[N+1]) {
    int d = 0;
    for (int i = 0; i < N+1; i++) {
        d = d + E_node[i] * (int)pow(2,(N+1) - i - 1);
    }
    return d;
}

int main() {
    FILE *dataFile;
    srand(time(0));

    for (int n = 0; n < 10; n++) {

        int E_nodeFrequency[FREQ];
        for (int i = 0; i < FREQ; i++) {
            E_nodeFrequency[i] = 0;
        }

        char filename[50];
        sprintf(filename, "./DATA/dataFile%d.txt", n);
        dataFile = fopen(filename, "w");
        if (!dataFile) {
            perror("Failed to open dataFile");
            return 1;
        }
        
        for (int times = 0; times < TRIALS; times++) {
            int E_node[N+1];
            E_node[0] = rand() % 2;
            E_node[1] = rand() % 2;
            E_node[2] = rand() % 2;
            E_node[3] = E_node[0] * E_node[1];

            simulated_annealing( E_node, dataFile);

            E_nodeFrequency[bin2dec(E_node)]++;
        }
        fclose(dataFile);

        printf("Frequenza stati: [");
        int s = 0;
        for (int i = 0; i < FREQ; i++) {
            if (i==0 || i==6 || i==10 || i==13) {
                printf("*%2d", E_nodeFrequency[i]);
            } else {
                printf("%2d", E_nodeFrequency[i]);
            }
            s += E_nodeFrequency[i];
            if (i < FREQ - 1) {
                printf(", ");
            }
        }
        printf("] con %.0f%% di positivi\n", 
               100*
               (E_nodeFrequency[0]
               +E_nodeFrequency[6]
               +E_nodeFrequency[10]
               +E_nodeFrequency[13])/(double)TRIALS);
        }

    return 0;
}