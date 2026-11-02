import argparse
import sys
from pathlib import Path
from mpi4py import MPI

CARPETA_PADRE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(CARPETA_PADRE))
sys.path.insert(0, str(CARPETA_PADRE / "mpi_por_ramas"))
from baseline_secuencial import leer_seeds
from mpi_por_ramas import resolver_por_ramas   # se reutiliza la tarea 2


def main():
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    parser = argparse.ArgumentParser()
    parser.add_argument("--archivo", type=Path, default=CARPETA_PADRE / "seeds.txt")
    parser.add_argument("--grupo", type=int, default=2, help="procesos por grupo")
    parser.add_argument("--id")
    parser.add_argument("--all", action="store_true")
    args = parser.parse_args()

    # Dividir los procesos en grupos de tamaño G
    tam_grupo = args.grupo
    numero_grupo = rank // tam_grupo
    cantidad_grupos = (size + tam_grupo - 1) // tam_grupo
    grupo = comm.Split(numero_grupo, rank)     # comunicador solo de mi grupo
    rank_en_grupo = grupo.Get_rank()

    # El proceso 0 lee las seeds y se las manda a todos
    seleccionados = None
    if rank == 0:
        seeds = leer_seeds(args.archivo)
        if args.id:
            seleccionados = [(args.id, seeds[args.id])]
        else:
            seleccionados = list(seeds.items())
    seleccionados = comm.bcast(seleccionados, root=0)

    # Tableros que le tocan a mi grupo (round-robin entre grupos)
    mis_tableros = seleccionados[numero_grupo::cantidad_grupos]

    envios = []
    comm.Barrier()
    inicio_total = MPI.Wtime()

    # Mi grupo resuelve sus tableros uno por uno, repartiendo las ramas
    resultados_grupo = []
    for numero, (identificador, original) in enumerate(mis_tableros):
        tablero = [fila[:] for fila in original]
        inicio = MPI.Wtime()
        resuelto = resolver_por_ramas(grupo, tablero, numero, envios)
        if rank_en_grupo == 0:
            resultados_grupo.append((identificador, resuelto, MPI.Wtime() - inicio, numero_grupo))

    # El proceso 0 global recoge lo de todos los grupos
    todos = comm.gather(resultados_grupo, root=0)
    fin_total = MPI.Wtime()
    MPI.Request.Waitall(envios)

    if rank == 0:
        resultados = []
        for lista in todos:
            resultados.extend(lista)
        resultados.sort(key=lambda r: int(r[0]))
        for identificador, resuelto, segundos, g in resultados:
            print(f"\nID: {identificador}")
            print("Resuelto" if resuelto else "Sin solución")
            print(f"Tiempo parcial: {segundos:.6f} segundos (grupo {g})")
        print(f"\nIDs procesados: {len(resultados)}")
        print(f"Procesos: {size}, tamaño de grupo: {tam_grupo}, grupos: {cantidad_grupos}")
        print(f"Tiempo total (real): {fin_total - inicio_total:.6f} segundos")


if __name__ == "__main__":
    main()