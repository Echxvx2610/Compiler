#include <stdio.h>

int main() {
    int numero = 10;

    if (numero > 15) {
        printf("El número es mayor que 15\n");
    }
    else if (numero > 5) {
        printf("El número es mayor que 5 pero menor o igual a 15\n");
    }
    else {
        printf("El número es 5 o menor\n");
    }

    return 0;
}
