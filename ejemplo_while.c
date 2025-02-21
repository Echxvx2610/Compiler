#include <stdio.h>

int main() {
    int i = 0;
    while (i < 5) {
        printf("El valor de i es: %d\n", i);
        i++;  // Incrementamos i para evitar un bucle infinito
    }

    return 0;
}
