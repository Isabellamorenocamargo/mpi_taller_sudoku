# Informe de resultados

Completa este informe después de implementar las tres tareas MPI. Ejecuta las comparaciones con el mismo archivo `seeds.txt`, en el mismo equipo y con el contenedor del taller.

## Entorno

- Equipo: MacBook Air con chip Apple M4
- Versión del contenedor: `augustosalazar/slim-mpi:2`
- Cantidad de repeticiones por medición: 3
- Valor común de `N` elegido: 8

## Comparación final con el mismo `N`

Repite tres veces cada ejecución y registra la mediana. Mantén fijo el `N` elegido en todas las filas MPI. Incluye `--allow-run-as-root --use-hwthread-cpus --oversubscribe` en `mpiexec`, igual que en la calibración, para permitir valores de `N` mayores que los slots detectados.

| Implementación | Caso | Procesos | Mediana del tiempo total (s) | Aceleración frente a secuencial |
| --- | --- | ---: | ---: | ---: |
| Secuencial | Todos los IDs | 1 | 43,34  | 1,00 |
| MPI por tableros | Todos los IDs | 8 | 11,20 | 3,87 |
| MPI por ramas | Todos los IDs, uno después de otro | 8 | 15,26 | 2,84 |
| MPI híbrido (G = 2) | Todos los IDs | 8 | 11,75 | 3,69 |

Calcula la aceleración como `tiempo secuencial / tiempo MPI`. Mide el tiempo MPI desde el inicio del reparto hasta recibir todos los resultados necesarios.

### Mediciones individuales (s)

| Implementación | Medición 1 | Medición 2 | Medición 3 | Mediana |
| --- | ---: | ---: | ---: | ---: |
| Secuencial | 43,51 | 43,30 | 43,34 | 43,34 |
| MPI por tableros | 11,20 | 11,25 | 10,96 | 11,20 |
| MPI por ramas | 14,99 | 15,26 | 15,36 | 15,26 |
| MPI híbrido (G = 2) | 11,75 | 11,75 | 11,91 | 11,75 |

Las salidas completas de cada ejecución están en la carpeta `resultados/`. 


## Conclusiones

- ¿Qué estrategia obtuvo el menor tiempo para los 30 tableros? ¿Cuánto mejoró respecto a la versión secuencial?

  La estrategia más rápida fue MPI por tableros, con una mediana de 11,20 s frente a los 43,34 s de la versión secuencial, es decir, fue 3,87 veces más rápida. 
  
  El híbrido obtuvo un resultado cercano, con 11,75 s y una aceleración de 3,69, mientras que MPI por ramas fue la más lenta de las tres estrategias, con 15,26 s y una aceleración de 2,84.


- ¿Cómo afectaron la comunicación y las diferencias de duración entre tableros?

  En la versión por tableros la comunicación casi no influyó, porque los tableros se reparten una sola vez al inicio y los resultados se recogen una sola vez al final. Lo que más afectó fue que no todos los procesos tuvieron la misma cantidad de trabajo: los 30 tableros no se dividen exacto entre 8 procesos y además no todos tardan lo mismo en resolverse. Por eso, en la primera medición, el proceso 1 trabajó 11,20 s y el proceso 6 solo 5,50 s. Como el coordinador debe esperar a que todos terminen, el tiempo total fue justamente el del proceso más cargado (11,20 s), y los que terminaron antes se quedaron esperando.

  En la versión por ramas la comunicación sí pesó más, porque por cada uno de los 30 tableros hay que repartir las ramas, avisar a los demás cuando se encuentra la solución y esperar a que todos terminen antes de pasar al siguiente.



- ¿Cómo se comparó repartir tableros con resolverlos en orden y repartir las ramas de cada uno?

  Repartir tableros (11,20 s) fue más rápido que repartir ramas (15,26 s), porque cada proceso trabaja en tableros distintos de forma independiente y casi no necesita coordinarse con los demás. Repartir ramas depende de dónde esté la solución: si está en un camino que la versión secuencial revisaría de último, un proceso la encuentra muy rápido, como en el ID 3, que en la primera medición bajó de 3,00 s a 0,075 s. Pero si la solución está en los primeros caminos, los demás procesos trabajan en ramas que no llevan a nada y no hay mejora o incluso empeora, como probablemente pasó en el ID 11, que subió de 1,06 s a 1,13 s. El híbrido quedó en un punto intermedio, porque combina las ventajas del reparto por tableros con el costo de coordinación del reparto por ramas.