import argparse
import sys
from pathlib import Path
from mpi4py import MPI

# Para importar sudoku.py y baseline_secuencial.py de la carpeta de arriba
CARPETA_PADRE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(CARPETA_PADRE))
from sudoku import resolver_con_tiempo
from baseline_secuencial import leer_seeds


def main():
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    parser = argparse.ArgumentParser()
    parser.add_argument("--archivo", type=Path, default=CARPETA_PADRE / "seeds.txt")
    parser.add_argument("--id")
    parser.add_argument("--all", action="store_true")
    args = parser.parse_args()

    # El proceso 0 lee las seeds y arma un paquete por proceso (round-robin)
    paquetes = None
    if rank == 0:
        seeds = leer_seeds(args.archivo)
        if args.id:
            seleccionados = [(args.id, seeds[args.id])]
        else:
            seleccionados = list(seeds.items())
        paquetes = []
        for p in range(size):
            paquetes.append([])
        for i, tarea in enumerate(seleccionados):
            paquetes[i % size].append(tarea)

    # Todos arrancan juntos y se toma el tiempo inicial
    comm.Barrier()
    inicio = MPI.Wtime()

    # Repartir: cada proceso recibe su lista de tableros
    mis_tareas = comm.scatter(paquetes, root=0)

    # 4) Cada proceso resuelve sus tableros con el resolvedor normal
    mis_resultados = []
    for identificador, original in mis_tareas:
        tablero = [fila[:] for fila in original]
        resuelto, segundos = resolver_con_tiempo(tablero)
        mis_resultados.append((identificador, resuelto, segundos, rank))

    #  El proceso 0 recoge todos los resultados
    todos = comm.gather(mis_resultados, root=0)
    fin = MPI.Wtime()

    if rank == 0:
        resultados = []
        for lista in todos:
            resultados.extend(lista)
        resultados.sort(key=lambda r: int(r[0]))
        for identificador, resuelto, segundos, quien in resultados:
            print(f"\nID: {identificador}")
            print("Resuelto" if resuelto else "Sin solución")
            print(f"Tiempo parcial: {segundos:.6f} segundos (proceso {quien})")

        print("\nCarga por proceso:")
        for p in range(size):
            carga = sum(r[2] for r in resultados if r[3] == p)
            print(f"  proceso {p}: {carga:.3f} s")

        print(f"\nIDs procesados: {len(resultados)}")
        print(f"Procesos: {size}")
        print(f"Tiempo total (real): {fin - inicio:.6f} segundos")


if __name__ == "__main__":
    main()