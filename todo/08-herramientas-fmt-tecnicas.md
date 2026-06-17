# Herramientas Fmt Tecnicas

> **Prioridad:** ver [README.md](README.md)  
> **Resumen:** Gaifman/Hanf, tipos Hintikka, MSO, queries, homomorfismos, jerarquías, inexpresabilidad.

> **Origen:** líneas 2226–2717 de `todo.md`

<!-- segment-header-end -->
Sí: todavía faltan cosas más finas. Las anteriores eran “grandes capítulos”; ahora iría por **herramientas técnicas concretas** que aparecen en el espíritu de *Finite Model Theory* y que todavía no metimos bien. El libro está muy cargado de temas como juegos, lógica monádica de segundo orden, Datalog, lógicas de punto fijo, clases como PTIME/PSPACE/LOGSPACE y clausura transitiva. ([Google Books][1])

## 1. Localidad: Gaifman y Hanf

Esto es central para demostrar **inexpresabilidad** en primer orden.

API:

```python
phi.gaifman_radius()
A.local_neighborhood(a, radius=r)
is_gaifman_local(query, radius=r)
is_hanf_local(query, radius=r)
```

La idea: una fórmula FO no puede ver arbitrariamente lejos en estructuras como grafos; muchas propiedades globales, como conectividad, no son FO-definibles. En cursos de teoría de modelos finitos se formula como que toda consulta FO-definible es local en el sentido de Gaifman. ([ifis.uni-luebeck.de][2])

Esto serviría para que la librería diga:

```text
No parece FO-definible: viola localidad de Gaifman.
```

## 2. Tipos de Hintikka

Faltaba un módulo de **tipos finitos por rango cuantificacional**.

```python
A.hintikka_type(tuple=(a,b), quantifier_rank=3)
A.same_fo_type(B, tuple1, tuple2, qr=3)
```

Esto permite comparar elementos o tuplas según lo que puede distinguir FO con profundidad acotada.

Muy útil para:

* juegos de Ehrenfeucht–Fraïssé;
* minimización de fórmulas;
* clasificación de tuplas;
* definibilidad con rango acotado.

## 3. Normal forms finitas

No solo prenexa/CNF/DNF. En finito interesan formas normales ligadas a juegos y localidad:

```python
phi.to_scott_normal_form()
phi.to_gaifman_normal_form()
phi.to_existential_second_order_normal_form()
```

Esto es clave si después querés conectar con complejidad descriptiva.

## 4. Segundo orden completo

Habíamos mencionado ESO y MSO medio de pasada, pero faltaría implementarlo de verdad:

```python
X = RelationVar("X", arity=1)
E = Relation("E", 2)

phi = ExistsSO(X, ForAll([x,y], Implies(E(x,y), X(x) != X(y))))
```

Soportar:

* SO completo;
* ESO;
* USO;
* MSO;
* monadic ESO;
* cuantificación sobre funciones;
* cuantificación sobre relaciones de aridad fija.

La lógica monádica de segundo orden y sus juegos aparecen como tema reconocido en Ebbinghaus–Flum. ([homepages.inf.ed.ac.uk][3])

## 5. Traducción de problemas NP a ESO

Esto sería hermoso:

```python
ThreeColorability().to_eso()
HamiltonianPath().to_eso()
SAT().to_eso()
```

Ejemplo conceptual:

```python
exists Colors R, G, B:
    partition(R,G,B)
    and no_edge_same_color
```

Esto implementaría el costado “teorema de Fagin”: **NP como lógica existencial de segundo orden**.

## 6. MSO sobre grafos de ancho acotado

Una capa más avanzada:

```python
G.tree_decomposition()
MSOModelChecker(phi).run_on_bounded_treewidth(G)
```

Esto conecta con Courcelle: muchas propiedades MSO son decidibles eficientemente en grafos de ancho de árbol acotado. No es el centro de Ebbinghaus–Flum, pero pertenece al vecindario natural de MSO y teoría de modelos finitos.

## 7. Queries, no solo sentencias

Hasta ahora hablamos mucho de fórmulas y estructuras, pero teoría de modelos finitos vive también de **consultas**.

```python
Q = Query(lambda x, y: Exists(z, And(E(x,z), E(z,y))))
Q.evaluate(A)
Q.arity
Q.is_boolean()
```

Diferenciar:

* oración: devuelve verdadero/falso;
* consulta unaria;
* consulta binaria;
* consulta k-aria;
* consulta booleana;
* consulta con parámetros.

Esto acerca la librería a bases de datos.

## 8. Contención y equivalencia de consultas

Muy importante:

```python
Q1.contained_in(Q2, over=class_of_structures)
Q1.equivalent_to(Q2)
Q1.find_counterexample_to_containment(Q2, max_size=6)
```

Ejemplo:

```text
Q1 ⊆ Q2 falla en una estructura de tamaño 4.
```

Esto es natural para consultas conjuntivas, Datalog y bases de datos.

## 9. Homomorfismos como semántica de consultas conjuntivas

Esto faltaba como puente fuerte:

```python
ConjunctiveQuery(...).as_pattern()
Q.evaluate_by_homomorphisms(A)
```

En bases de datos finitas, las consultas conjuntivas se entienden muy bien vía homomorfismos. Y eso conecta perfecto con CSP y polimorfismos.

## 10. Jerarquías de fragmentos

No solo soportar lógicas, sino poder comparar fragmentos:

```python
Logic("FO2") < Logic("FO3")
Logic("FO") < Logic("LFP")
Logic("ESO").captures("NP")
Logic("MSO").on_words().captures("regular_languages")
```

Y tener una tabla interna:

```text
FO
FO[k]
FO+C
L∞ω[k]
MSO
ESO
LFP
IFP
PFP
FO+TC
FO+DTC
```

## 11. Orden-invariancia

Esto es muy fino y muy de teoría de modelos finitos.

A veces una fórmula usa un orden auxiliar `<`, pero el resultado no depende de cuál orden se eligió.

```python
phi.is_order_invariant(structure_class, max_size=7)
```

Ejemplo conceptual:

```text
La fórmula usa <, pero define la misma consulta para todos los órdenes lineales del universo.
```

Esto importa porque muchas capturas de complejidad requieren estructuras ordenadas.

## 12. Sucesor-invariancia

Parecido al anterior, pero con una relación sucesor auxiliar:

```python
phi.is_successor_invariant(max_size=8)
```

Hay problemas abiertos históricos sobre orden-invariancia y sucesor-invariancia en teoría de modelos finitos; aparecen incluso en listas de problemas del área asociadas a Ebbinghaus y otros. ([Logic RWTH Aachen][4])

## 13. Aritmética incorporada

Para complejidad descriptiva, no alcanza con orden. Muchas veces se agregan:

```python
A.with_order()
A.with_successor()
A.with_plus()
A.with_times()
A.with_bit()
```

Y después:

```python
Logic("FO+BIT").expresses(problem)
```

Esto es clave para conectar con circuitos y clases pequeñas como AC⁰.

## 14. Circuit complexity

Faltaba el puente con circuitos:

```python
FOFormula(...).to_uniform_AC0_circuit_family()
```

Relaciones típicas:

* FO con orden/arithmetic ↔ AC⁰ uniforme;
* FO con conteo/paridad ↔ circuitos con compuertas de conteo;
* lógicas de punto fijo ↔ clases de complejidad mayores.

Esto ya es más Immerman que Ebbinghaus–Flum, pero pertenece al mismo bloque de complejidad descriptiva.

## 15. Cuantificadores de Lindström/generalizados

No solo `∃` y `∀`.

```python
Q_even(x, phi(x))
Q_majority(x, phi(x))
Q_reachability(x, y, E)
Q_isomorphism(...)
```

El libro incluye cuantificadores y reducciones lógicas como parte del cierre de la teoría. ([Google Books][1])

## 16. Propiedades de cierre

Para clases definibles:

```python
ClassOfStructures(...).closed_under_disjoint_union()
ClassOfStructures(...).closed_under_complement()
ClassOfStructures(...).closed_under_extensions()
ClassOfStructures(...).closed_under_homomorphisms()
```

Esto serviría para probar que cierta propiedad **no** está en cierto fragmento.

## 17. Preservación finita

En modelo infinito hay teoremas clásicos de preservación; en finito muchos fallan o se vuelven más sutiles.

API:

```python
phi.is_preserved_under_homomorphisms(finite=True, max_size=8)
phi.equivalent_existential_positive_on_finite(max_size=8)
```

Esto conecta con resultados modernos, pero también con el corazón del contraste entre teoría de modelos clásica y finita.

## 18. Espectros refinados

Ya mencioné espectros, pero faltaba hacerlo bien:

```python
Spec(phi).compute(n_max=30)
Spec(phi).guess_eventual_periodicity()
Spec(phi).complexity_class_hint()
```

Y variantes:

```python
Spec(phi, structures="graphs")
Spec(phi, structures="algebras")
Spec(phi, structures="ordered")
```

En finito, preguntar para qué tamaños existe modelo es mucho más natural que en teoría de modelos clásica.

## 19. Enumeración de estructuras relacionales aleatorias

No solo álgebras aleatorias.

```python
RandomGraph(n, p=0.5)
RandomRelationalStructure(signature, n)
RandomOrderedStructure(n)
```

Y evaluar:

```python
estimate_asymptotic_probability(phi, n_values=[10,20,40,80])
```

Esto sirve para leyes 0-1 y para ver empíricamente límites expresivos de FO.

## 20. Juegos para MSO y ESO

No solo EF clásico:

```python
MSOGame(A, B, rounds=...)
FaginGame(...)
AjtaiFaginGame(...)
```

Libkin menciona que los juegos de MSO están tratados en Ebbinghaus–Flum. ([homepages.inf.ed.ac.uk][3])

Esto permitiría demostrar cosas como:

```text
Esta propiedad no es definible en monadic ESO.
```

## 21. Traducciones lógicas entre vocabularios

Más que interpretaciones algebraicas: traducciones de estructuras.

```python
tau = FOTransduction(source_signature, target_signature)
tau.apply(A)
tau.reduce_property(P, Q)
```

Esto es esencial para reducciones descriptivas.

## 22. Model checking parametrizado

Esto no estaba:

```python
ModelChecking(phi).parameterized_complexity()
```

Ejemplo:

```text
Parámetro: tamaño de la fórmula.
Entrada: estructura.
Problema: A ⊨ φ.
```

Hay una línea importante que relaciona model checking, definibilidad y complejidad parametrizada; Flum y Grohe lo desarrollan desde fines de los 90. ([arXiv][5])

## 23. Clases de estructuras restringidas

La teoría cambia mucho si no mirás todas las estructuras, sino clases como:

```python
Graphs.bounded_degree(d)
Graphs.planar()
Graphs.excluded_minor(H)
Graphs.bounded_treewidth(k)
Orders.linear()
Words()
Trees()
```

Entonces:

```python
phi.is_definable_on(class_=Graphs.planar())
```

No es lo mismo definibilidad sobre todos los grafos que sobre grafos planares, árboles o palabras.

## 24. Palabras, árboles y estructuras con sucesor

Ya habíamos dicho autómatas, pero lo pondría como submundo propio:

```python
Word("abba").as_structure()
Tree(...).as_structure()
MSO.to_automaton()
Automaton.to_mso()
```

Esto conecta con Büchi, MSO y lenguajes regulares.

## 25. Una capa de “pruebas de inexpresabilidad”

Esto sería una feature muy potente:

```python
Inexpressibility.prove(
    property="connectivity",
    logic="FO",
    method="locality"
)
```

Métodos:

* juego EF;
* juego de pebble;
* localidad de Gaifman;
* localidad de Hanf;
* conteo;
* simetría;
* preservación;
* reducción desde separación conocida.

---

La versión extendida de la librería quedaría en cuatro mundos:

```text
1. Álgebra universal finita
   términos, congruencias, HSP, clones, CSP.

2. Lógica finita efectiva
   FO, SO, MSO, conteo, punto fijo, Datalog.

3. Inexpresabilidad
   juegos, localidad, tipos, preservación, jerarquías.

4. Complejidad descriptiva
   ESO=NP, LFP=PTIME ordenado, TC, reducciones, circuitos.
```

Lo que más faltaba, si pienso específicamente en **Ebbinghaus–Flum**, era esto:

```text
localidad
tipos finitos
segundo orden
MSO
Datalog
punto fijo
orden-invariancia
reducciones lógicas
complejidad descriptiva
consultas de bases de datos
```

Y si lo llevás a tu proyecto, la frase de diseño sería:

> No construir solo una librería para evaluar fórmulas sobre álgebras, sino un laboratorio para estudiar **qué puede y qué no puede expresar una lógica sobre estructuras finitas**.

## Véase también

* Localidad de Gaifman.
* Localidad de Hanf.
* Tipos de Hintikka.
* Juegos de pebble.
* Lógica monádica de segundo orden.
* Datalog.
* Orden-invariancia.
* Sucesor-invariancia.
* Circuitos AC⁰.
* Complejidad parametrizada del model checking.

[1]: https://books.google.com/books/about/Finite_Model_Theory.html?hl=uk&id=qwXtCAAAQBAJ&utm_source=chatgpt.com "Finite Model Theory: First Edition"
[2]: https://www.ifis.uni-luebeck.de/~oezcep/teaching/WS1617/Foundations/fmt-1.pdf?utm_source=chatgpt.com "Finite Model Theory - Lecture 3"
[3]: https://homepages.inf.ed.ac.uk/libkin/fmt/fmt.pdf?utm_source=chatgpt.com "Elements of Finite Model Theory"
[4]: https://logic.rwth-aachen.de/Research/AlMoTh/problems.pdf?utm_source=chatgpt.com "Problems in Finite Model Theory"
[5]: https://arxiv.org/abs/cs/9910001?utm_source=chatgpt.com "Fixed-parameter tractability, definability, and model checking"



Sí. A esta altura faltan sobre todo cosas que no son “módulos vistosos”, sino **fundamentos finos** de teoría de modelos finitos. Ebbinghaus–Flum no es solo una lista de lógicas: también enseña cómo codificar cómputos, comparar lenguajes y demostrar separaciones. Springer presenta el libro justamente como una exposición de la conexión entre axiomatizabilidad de clases finitas y complejidad temporal/espacial. ([Springer][1])

