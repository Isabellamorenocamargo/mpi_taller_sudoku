import sys
from pathlib import Path
from mpi4py import MPI

sys.path.append("/app")  # carpeta del proyecto dentro del contenedor
from sudoku import puede_colocar
from baseline_secuencial import leer_seeds

TAG_PARAR = 99   # mensaje "ya lo resolví, dejen de buscar"
detenido = False
pasos = 0
tablero_actual = 0


def buscar_vacia(tablero):
    for f in range(9):
        for c in range(9):
            if tablero[f][c] == 0:
                return f, c
    return None


def generar_ramas(tablero, niveles=3):
    # llena las primeras 'niveles' casillas vacías con todos sus valores válidos
    ramas = [tablero]
    for _ in range(niveles):
        nuevas = []
        for rama in ramas:
            vacia = buscar_vacia(rama)
            if vacia is None:
                nuevas.append(rama)
                continue
            f, c = vacia
            for valor in range(1, 10):
                if puede_colocar(rama, f, c, valor):
                    hija = [fila[:] for fila in rama]
                    hija[f][c] = valor
                    nuevas.append(hija)
        ramas = nuevas
    return ramas


def resolver(comm, tablero):
    # mismo backtracking de sudoku.py, pero cada 2000 pasos mira si llegó el aviso
    global detenido, pasos
    pasos += 1
    if pasos % 2000 == 0:
        while comm.Iprobe(source=MPI.ANY_SOURCE, tag=TAG_PARAR):
            if comm.recv(source=MPI.ANY_SOURCE, tag=TAG_PARAR) == tablero_actual:
                detenido = True
    if detenido:
        return False
    vacia = buscar_vacia(tablero)
    if vacia is None:
        return True
    f, c = vacia
    for valor in range(1, 10):
        if puede_colocar(tablero, f, c, valor):
            tablero[f][c] = valor
            if resolver(comm, tablero):
                return True
            tablero[f][c] = 0
    return False


def resolver_por_ramas(comm, tablero, numero, envios):
    global detenido, tablero_actual
    rank, size = comm.Get_rank(), comm.Get_size()
    detenido = False
    tablero_actual = numero

    paquetes = None
    if rank == 0:
        ramas = generar_ramas(tablero)
        paquetes = [ramas[p::size] for p in range(size)]   # round-robin
    mis_ramas = comm.scatter(paquetes, root=0)

    encontre = False
    for rama in mis_ramas:
        if resolver(comm, rama):
            encontre = True
            for otro in range(size):          # avisar a los demás
                if otro != rank:
                    envios.append(comm.isend(numero, dest=otro, tag=TAG_PARAR))
            break
        if detenido:
            break

    respuestas = comm.gather(encontre, root=0)   # el 0 espera a todos
    if rank == 0:
        return True in respuestas


def main():
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()

    seleccionados = None
    if rank == 0:
        seeds = leer_seeds(Path("/app/seeds.txt"))
        if "--id" in sys.argv:
            id_buscado = sys.argv[sys.argv.index("--id") + 1]
            seleccionados = [(id_buscado, seeds[id_buscado])]
        else:
            seleccionados = list(seeds.items())
    seleccionados = comm.bcast(seleccionados, root=0)

    envios = []
    comm.Barrier()
    inicio_total = MPI.Wtime()

    for numero, (identificador, original) in enumerate(seleccionados):
        tablero = [fila[:] for fila in original]
        inicio = MPI.Wtime()
        resuelto = resolver_por_ramas(comm, tablero, numero, envios)
        if rank == 0:
            print(f"\nID: {identificador}")
            print("Resuelto" if resuelto else "Sin solución")
            print(f"Tiempo parcial: {MPI.Wtime() - inicio:.6f} segundos", flush=True)

    fin_total = MPI.Wtime()
    MPI.Request.Waitall(envios)
    if rank == 0:
        print(f"\nIDs procesados: {len(seleccionados)}")
        print(f"Tiempo total (real): {fin_total - inicio_total:.6f} segundos")


if __name__ == "__main__":
    main()