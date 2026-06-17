# Capas Transversales Resto

> **Prioridad:** ver [README.md](README.md)  
> **Resumen:** IR común, recursos expresivos, frontera de expresividad, benchmarks, experimentos reproducibles, métrica de sorpresa.

> **Origen:** líneas 3891–4247 de `todo.md`

<!-- segment-header-end -->
## 3. Un lenguaje intermedio común

Diseñaría un IR, tipo:

```text
FiniteRelationalIR
```

Para que todo pueda traducirse a todo:

```text
FO
MSO
ESO
Datalog
LFP
SAT
SMT
TPTP
UACalc
GAP
Sage
Lean
```

Sin un IR común, cada módulo queda pegado con cinta.

## 4. Sistema de recursos expresivos

Cada fórmula debería tener un “perfil”:

```python
phi.resources()
```

Salida:

```text
lógica: FO
variables usadas: 3
rango cuantificacional: 4
alternancia: Σ₂
usa igualdad: sí
usa orden: no
usa conteo: no
usa punto fijo: no
usa segundo orden: no
```

Esto vuelve científica la comparación entre fórmulas.

## 5. Búsqueda por frontera de expresividad

Una función muy poderosa:

```python
find_boundary(property=P)
```

Salida ideal:

```text
P no está en FO hasta rango 6.
P sí está en FO+TC.
P sí está en LFP.
P tiene definición ESO.
P parece no estar en FO+C según ejemplos CFI.
```

Es decir: no solo “encuentra una fórmula”, sino que intenta ubicar la propiedad en un mapa lógico.

## 6. Contraejemplos pedagógicos mínimos

Para cada separación lógica, traer ejemplos clásicos:

```python
Examples.connectivity_not_fo()
Examples.parity_not_fo()
Examples.cfi_pair(k=3)
Examples.fo2_vs_fo3()
Examples.mso_not_fo_on_words()
```

Con:

```python
example.explain()
example.draw()
example.play_game()
example.separating_formula_if_any()
```

Esto sería oro para investigación y docencia.

## 7. Modo “auditor de papers”

Una función muy práctica:

```python
audit_claim(
    assumptions=...,
    conclusion=...,
    max_size=7,
    logic="FO"
)
```

Que busque:

* contraejemplos pequeños;
* independencia de axiomas;
* errores de signatura;
* cuantificadores innecesarios;
* hipótesis redundantes;
* definición más chica;
* modelo mínimo.

Esto sirve directamente para revisar conjeturas.

## 8. Composición de interpretaciones

No alcanza con tener interpretaciones. Deberían componerse:

```python
I = Interpretation(A, B)
J = Interpretation(B, C)

K = J.compose(I)
```

Y poder preguntar:

```python
K.verify()
K.formula_size()
K.quantifier_rank()
```

Esto es importante para reducciones lógicas y equivalencias definicionales.

## 9. Complejidad de las traducciones

Cuando traducís una fórmula, deberías medir el costo:

```python
translation.profile()
```

Salida:

```text
tamaño original: 27
tamaño traducido: 143
rango cuantificacional original: 3
rango nuevo: 7
variables nuevas: 4
fragmento preservado: sí
```

Sin eso, las traducciones pueden volverse monstruos inservibles.

## 10. Generador de familias, no solo estructuras sueltas

Muchos fenómenos aparecen en familias:

```python
Cycles(n)
Paths(n)
Grids(n, m)
Cliques(n)
RandomGraphs(n, p)
CFIGraphs(base, parity)
FiniteFields(q)
BooleanAlgebras(n)
Lattices.small(n)
```

Y luego:

```python
Family(Cycles).test_property(phi, n=range(3, 30))
```

Esto conecta computación experimental con comportamiento asintótico.

## 11. Álgebra universal + palabras regulares

Este puente es muy lindo y faltaba integrarlo mejor:

```python
L = RegularLanguage("a*b*")
M = L.syntactic_monoid()

M.is_aperiodic()
L.is_fo_definable_on_words()
```

Ahí se unen:

```text
autómatas
lógica sobre palabras
monoides finitos
variedades algebraicas
```

Para una librería hecha por alguien de álgebra universal, esto sería una zona natural y elegante.

## 12. Capa de “no hacer”

También definiría explícitamente qué **no** va a hacer.

No intentaría competir de entrada con:

```text
Sage entero
GAP entero
Z3 entero
Coq/Lean enteros
Alloy entero
Maude entero
```

La identidad debería ser más precisa:

```text
finite model theory efectiva
+ álgebra universal finita
+ definibilidad
+ certificados
+ contraejemplos mínimos
```

Eso sí es una contribución clara.

## 13. Un formato de benchmark publicable

Algo así:

```text
FMTBench
```

Con problemas como:

```text
Definability/QF
Definability/PP
FO-separation
Pebble-games
CSP-polymorphisms
Finite-model-finding
Datalog-evaluation
LFP-reachability
Congruence-lattices
Term-clone-search
```

Cada benchmark debería tener:

```text
entrada
resultado esperado
certificado
tiempo base
memoria
referencia bibliográfica
```

## 14. Una API de “experimento reproducible”

```python
with Experiment("malcev_vs_majority_size_6") as E:
    E.add_structures(...)
    E.add_search(...)
    E.run()
    E.export("paper/")
```

Que genere:

```text
resultados.json
certificados/
tablas.tex
figuras.svg
notebook.ipynb
reproduce.sh
```

Eso hace que el software sea publicable de verdad.

## 15. Métrica de sorpresa matemática

Medio raro, pero útil:

```python
A.surprising_features()
```

Ejemplo:

```text
Tiene término de Siggers pero no mayoría.
Tiene pocas congruencias para su tamaño.
Dos reductos no isomorfos tienen el mismo clon parcial hasta aridad 3.
Una relación requiere 4 variables para definirse.
```

Esto ayuda a encontrar material investigable.

---

Mi respuesta final sería:

**Sí, queda algo más, pero ya no son “temas del libro”. Son principios de diseño científico.**

La librería ideal tendría cinco pilares:

```text
1. Computar:
   evaluar, buscar, enumerar, sintetizar.

2. Explicar:
   fórmulas, testigos, juegos, obstrucciones.

3. Certificar:
   resultados positivos y negativos verificables.

4. Comparar:
   lógicas, fragmentos, estructuras, propiedades.

5. Publicar:
   benchmarks, notebooks, LaTeX, datos reproducibles.
```

La frase más compacta del proyecto sería:

> **Una plataforma Python para experimentar con expresividad lógica finita y álgebra universal computacional, produciendo certificados verificables de definibilidad, no-definibilidad y contraejemplos mínimos.**

Eso ya no suena a “otra librería de lógica”. Suena a proyecto publicable.

## Véase también

* Certificados de no-definibilidad.
* Juegos de Ehrenfeucht–Fraïssé.
* Pebble games.
* Monoides sintácticos.
* FMTBench.
* Interpretaciones lógicas.
* Complejidad de traducciones.
* Experimentos matemáticos reproducibles.
* Reducciones de primer orden.
* Álgebra universal computacional.



