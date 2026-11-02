# Tarea 2: repartir ramas de cada tablero

Implementa una versión MPI en esta carpeta. Con `--all`, el proceso coordinador lee los 30 IDs de `seeds.txt` en orden. Para cada tablero, crea tareas a partir de opciones válidas de las primeras casillas vacías y reparte esas ramas entre procesos. Espera a que termine ese tablero antes de comenzar el siguiente: **los tableros se procesan secuencialmente y las ramas de cada tablero en paralelo**.

Cada proceso explora su rama con backtracking y comunica el resultado. Cuando se encuentra una solución, los demás deben dejar de buscar ese tablero. Muestra el estado y el tiempo parcial de cada ID al terminarlo, además del tiempo total de los 30. Conserva la opción `--id` para resolver un solo tablero.

Añade aquí los comandos para ejecutar `--id` y `--all` con el contenedor. Incluye `--allow-run-as-root --use-hwthread-cpus --oversubscribe` en `mpiexec`, como en la calibración. Compara el tiempo total de `--all` con la versión secuencial y registra los resultados en `../INFORME.md`.


## Implementacion

Los tableros se resuelven en orden, uno por uno. Para cada tablero, el coordinador llena las 3 primeras casillas vacías con todos los valores posibles; cada combinación es un camino distinto (una rama), y las ramas se reparten entre los procesos. El primero que encuentra la solución les avisa a los demás para que dejen de buscar, y solo entonces se pasa al siguiente tablero.


## Comandos para ejecutar (desde la carpeta raíz del proyecto)

### macOS (Terminal)

Un solo tablero (ejemplo, ID 7):

```bash
docker run --rm -v "$(pwd):/app" augustosalazar/slim-mpi:2 mpiexec --allow-run-as-root --use-hwthread-cpus --oversubscribe -n 8 python /app/mpi_por_ramas/mpi_por_ramas.py --id 7
```

Todos los tableros:

```bash
docker run --rm -v "$(pwd):/app" augustosalazar/slim-mpi:2 mpiexec --allow-run-as-root --use-hwthread-cpus --oversubscribe -n 8 python /app/mpi_por_ramas/mpi_por_ramas.py --all
```

### Windows (PowerShell)

Un solo tablero (ejemplo, ID 7):

```powershell
docker run --rm -v "${PWD}:/app" augustosalazar/slim-mpi:2 mpiexec --allow-run-as-root --use-hwthread-cpus --oversubscribe -n 8 python /app/mpi_por_ramas/mpi_por_ramas.py --id 7
```

Todos los tableros:

```powershell
docker run --rm -v "${PWD}:/app" augustosalazar/slim-mpi:2 mpiexec --allow-run-as-root --use-hwthread-cpus --oversubscribe -n 8 python /app/mpi_por_ramas/mpi_por_ramas.py --all
```

## Resultado (N = 8)

- IDs procesados: 30 / 30
- Tiempo total `--all` (mediana de las 3 mediciones): 15,26 s
- Tiempo total del secuencial (mediana de las 3 mediciones): 43,34 s
- La versión por ramas fue 28,08 s más rápida que la secuencial. Detalle y justificación en `../INFORME.md`.