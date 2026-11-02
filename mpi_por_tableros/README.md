# Tarea 1: repartir tableros

Implementa una versión MPI en esta carpeta. Al ejecutar todos los tableros, cada ID debe ser una tarea que pueda asignarse a un proceso. Reutiliza el resolvedor de `../sudoku.py` y reúne los estados en el proceso coordinador.

Registra el tiempo total de ejecución y confirma que se procesaron los 30 IDs. Añade aquí el comando para ejecutar tu implementación con el contenedor. Incluye `--allow-run-as-root --use-hwthread-cpus --oversubscribe` en `mpiexec`, como en la calibración.

---

## Implementacion 

El proceso coordinador lee los 30 tableros y los reparte por turnos entre los procesos. Cada proceso resuelve sus tableros con el mismo resolvedor de `sudoku.py`, y al final le devuelve los resultados al coordinador, que los muestra junto con el tiempo total.

## Comando para ejecutar (desde la carpeta raíz del proyecto)

macOS (Terminal):

```bash
docker run --rm -v "$(pwd):/app" augustosalazar/slim-mpi:2 mpiexec --allow-run-as-root --use-hwthread-cpus --oversubscribe -n 8 python /app/mpi_por_tableros/mpi_por_tableros.py --all
```

Windows (PowerShell):

```powershell
docker run --rm -v "${PWD}:/app" augustosalazar/slim-mpi:2 mpiexec --allow-run-as-root --use-hwthread-cpus --oversubscribe -n 8 python /app/mpi_por_tableros/mpi_por_tableros.py --all
```

## Resultado (N = 8)

- IDs procesados: 30 / 30
- Mediciones: 11,20 s, 11,25 s y 10,96 s
- Tiempo total (mediana de 3 mediciones): 11,20 s 

