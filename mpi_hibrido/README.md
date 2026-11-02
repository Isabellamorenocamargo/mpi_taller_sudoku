# Tarea 3: combinar tableros y ramas

Implementa una versión MPI en esta carpeta. Reparte los IDs entre grupos de procesos y permite que los procesos de cada grupo exploren ramas distintas del tablero asignado.

Registra el tiempo total de los 30 IDs y explica cómo elegiste el tamaño de los grupos. Añade aquí el comando para ejecutar tu implementación con el contenedor. Incluye `--allow-run-as-root --use-hwthread-cpus --oversubscribe` en `mpiexec`, como en la calibración.


---

## Implementacion y cómo funciona

Los 8 procesos se dividen en grupos, y los tableros se reparten por turnos entre los grupos. Dentro de cada grupo, cada tablero se resuelve como en la versión por ramas: los procesos del grupo se reparten los caminos posibles y el primero que encuentra la solución avisa a sus compañeros.



## Elección del tamaño de grupo (N = 8)

G = número de procesos por grupo

Se probaron G = 2 (4 grupos de 2 procesos) y G = 4 (2 grupos de 4 procesos) con el mismo N, las únicas divisiones parejas de 8 que combinan ambas ideas (G = 1 equivale a por tableros y G = 8 a por ramas):

- G = 2: 11,75 s
- G = 4: 12,51 s

Se eligió G = 2 porque fue más rápido: con 4 grupos hay más tableros resolviéndose al mismo tiempo.




## Comandos para ejecutar (desde la carpeta raíz del proyecto)

macOS (Terminal):

```bash
docker run --rm -v "$(pwd):/app" augustosalazar/slim-mpi:2 mpiexec --allow-run-as-root --use-hwthread-cpus --oversubscribe -n 8 python /app/mpi_hibrido/mpi_hibrido.py --all --grupo 2
```

Windows (PowerShell):

```powershell
docker run --rm -v "${PWD}:/app" augustosalazar/slim-mpi:2 mpiexec --allow-run-as-root --use-hwthread-cpus --oversubscribe -n 8 python /app/mpi_hibrido/mpi_hibrido.py --all --grupo 2
```

## Resultado (N = 8, G = 2)

- IDs procesados: 30 / 30
- Mediciones G=2: 11,75 s, 11,75 s, 11,90 s
- Tiempo total (mediana de 3 mediciones): 11,75 s