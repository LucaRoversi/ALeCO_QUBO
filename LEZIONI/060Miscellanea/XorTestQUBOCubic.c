#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>

#define N 3 // Numero di qubit (3 per terne)

int energyCubic(int E_node[N+1]) {
    int r =    E_node[0] 
           +   E_node[1] 
           +   E_node[2] 
           - 2*E_node[0]*E_node[1] 
           - 2*E_node[0]*E_node[2] 
           - 2*E_node[1]*E_node[2]
           + 4*E_node[0]*E_node[1]*E_node[2];
    return r;
}

int P(int E_node[N+1]) {
    int r = 
     2*( 
         E_node[0]*E_node[1]               //  xy
        -2*(E_node[0]+E_node[1])*E_node[3] //-2(x+y)w
        +3*E_node[3]                       // 3w
       );
    return r;
}

int energyQUBO(int E_node[N+1]) {
    int r =    
        E_node[0]           //x
    +   E_node[1]           //y
    +   E_node[2]           //z
    - 2*E_node[0]*E_node[1] //-2xy
    - 2*E_node[0]*E_node[2] //-2xz
    - 2*E_node[1]*E_node[2] //-2yz
    + 4*( 
           E_node[3]*E_node[2] //wz
         + P(E_node)           //P
        ) 
    ;
    return r;
}


int main() {
    int E_node[N+1];
    int i = 0;
    printf("x, y, z, xyz, w, zw+P, EQUBO, ECubic\n");
    for (int x = 0; x < 2; x++) {
        for (int y = 0; y < 2; y++) {
            for (int z = 0; z < 2; z++) {
                for (int w = 0; w < 2; w++) {
                    E_node[0] = x;
                    E_node[1] = y;
                    E_node[2] = z;
                    E_node[3] = w;
                    printf("%d, %d, %d, %3d, %d, %4d, %5d, %6d\n"
                          , E_node[0]
                          , E_node[1]
                          , E_node[2]
                          , E_node[0]*E_node[1]*E_node[2]
                          , E_node[3]
                          , E_node[3]*E_node[2] + P(E_node)
                          , energyQUBO(E_node)
                          , energyCubic(E_node)
                          );
                }
            }
        }    
    }
}