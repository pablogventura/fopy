# Complejidad Descriptiva Profunda

> **Prioridad:** ver [README.md](README.md)  
> **Resumen:** Model checking, Turing, alternancia, Trakhtenbrot, Datalog, clasificador de fragmentos, seguridad de queries.

> **Origen:** líneas 2718–3378 de `todo.md`

<!-- segment-header-end -->
## 1. Complejidad del *model checking*

No solo:

```python
A.models(phi)
```

sino distinguir tres complejidades:

```python
ModelChecking(phi, A).data_complexity()
ModelChecking(phi, A).expression_complexity()
ModelChecking(phi, A).combined_complexity()
```

Porque no es lo mismo fijar la fórmula y variar la estructura que recibir ambas como entrada.

Esto sería clave para una librería seria:

```python
mc = ModelChecking(logic="FO")
mc.complexity(
    formula_variable=True,
    structure_variable=True
)
```

## 2. Codificación de máquinas de Turing

Para complejidad descriptiva, necesitás poder representar cómputos como estructuras finitas:

```python
ComputationTable(machine=M, input=w).as_structure()
```

Con relaciones tipo:

```text
Time(t)
Position(i)
Symbol(t,i,s)
State(t,q)
Head(t,i)
```

Esto permite construir demostraciones del estilo:

```text
Una máquina acepta una entrada
⇔
existe una estructura/relación que satisface cierta fórmula.
```

Ese es el mecanismo técnico detrás de muchos teoremas de captura.

## 3. Traducción sistemática problema → fórmula

No solo escribir fórmulas a mano. Una librería buena debería tener:

```python
Problem("3-colorability").to_logic("ESO")
Problem("reachability").to_logic("FO+TC")
Problem("parity").to_logic("FO+MOD2")
```

Con validación:

```python
translation.verify_on_instances(max_size=6)
```

Eso sería pedagógicamente y científicamente muy fuerte.

## 4. Jerarquías de alternancia

Faltó bastante esto.

Para FO:

```python
phi.quantifier_alternation_depth()
phi.sigma_pi_level()
```

Ejemplo:

```text
Σ₁, Π₁, Σ₂, Π₂, ...
```

Para segundo orden:

```python
ESO(level="Sigma1")
SOAlternation(level=2)
```

Y para punto fijo:

```python
FixedPointAlternationHierarchy(...)
```

Esto permite estudiar no solo “si es definible”, sino **cuánta alternancia lógica necesita**.

## 5. Jerarquías por aridad

En segundo orden importa muchísimo la aridad de las relaciones cuantificadas:

```python
ExistsSO(RelationVar("R", arity=1), phi)
ExistsSO(RelationVar("E", arity=2), phi)
```

API:

```python
phi.second_order_arity()
phi.min_second_order_arity(max_arity=3)
```

Ejemplo:

```text
Esta propiedad es definible con una relación binaria existencial,
pero no se encontró definición monádica.
```

Esto es relevante para comparar MSO, monadic ESO, ESO relacional general, etc.

## 6. Trakhtenbrot y satisfacibilidad finita

Faltó un módulo conceptual sobre el hecho brutal de que la satisfacibilidad finita de FO es indecidible.

No como algoritmo mágico, sino como límite:

```python
FiniteSatisfiability(phi).semi_decide(max_size=10)
FiniteSatisfiability.explain_limitations()
```

La librería debería saber decir:

```text
Puedo buscar modelos finitos hasta tamaño n,
pero no existe un procedimiento general que decida siempre la satisfacibilidad finita de FO.
```

Esto es fundamental en teoría de modelos finitos.

## 7. Clases espectrales más finas

Ya mencionamos espectros, pero faltaría conectar con complejidad:

```python
Spec(phi).belongs_to("NE")
Spec(phi).estimate_growth()
Spec(phi).compare_with(sequence)
```

Y variantes:

```python
Spectrum.over_graphs()
Spectrum.over_ordered_structures()
Spectrum.over_algebras()
```

No solo “para qué tamaños hay modelos”, sino qué tipo de conjunto numérico se obtiene.

## 8. Teoría casi segura

Para leyes 0-1, no alcanza con estimar probabilidades. Haría falta:

```python
AlmostSureTheory(signature).axioms(max_quantifier_rank=3)
RandomStructure(signature).extension_axioms(k=3)
```

La idea: estudiar qué oraciones son verdaderas con probabilidad tendiente a 1 en estructuras aleatorias.

API posible:

```python
phi.almost_sure_truth(random_model="G(n,1/2)")
```

## 9. Axiomas de extensión

En grafos aleatorios, una herramienta clásica es expresar propiedades de extensión:

```text
dados conjuntos finitos disjuntos A y B,
existe un vértice conectado a todos los de A y a ninguno de B.
```

En librería:

```python
ExtensionAxiom(k=3).as_fo()
RandomGraphTheory.extension_axioms(up_to=4)
```

Esto sirve para construir teoría casi segura y demostrar leyes 0-1.

## 10. Reducciones de primer orden muy restringidas

Ya nombramos reducciones lógicas, pero faltan las versiones técnicas:

```python
QuantifierFreeProjection(...)
FOProjection(...)
FirstOrderReduction(...)
```

Con chequeos:

```python
reduction.is_many_one()
reduction.is_uniform()
reduction.preserves_order()
```

Esto es importante porque en complejidad descriptiva no cualquier reducción vale; la reducción misma debe ser lógicamente débil.

## 11. Uniformidad

En circuitos y complejidad descriptiva, faltaba formalizar uniformidad:

```python
CircuitFamily(...).is_dlogtime_uniform()
CircuitFamily(...).is_fo_uniform()
```

Y conexión:

```python
FO.with_order_and_bit().to_uniform_ac0()
```

Sin uniformidad, la relación lógica/circuitos queda medio tramposa.

## 12. Lógicas con operadores aritméticos incorporados

No solo `+`, `×`, `BIT`, sino configurar vocabularios numéricos:

```python
NumericVocabulary(order=True, plus=True, times=True, bit=True)
```

Y después:

```python
A.expand_with_numeric_predicates()
```

Para estudiar diferencias entre:

```text
FO[<]
FO[<,+]
FO[<,+,×]
FO[BIT]
```

Esto es central si querés conectar con circuitos pequeños y lenguajes regulares.

## 13. Lógica sobre strings con posiciones

Para autómatas, no basta con `Word("abba")`. Necesitás estructuras tipo:

```python
w = WordStructure(
    word="abba",
    predicates={"P_a", "P_b"},
    order=True,
    successor=True
)
```

Consultas:

```python
phi.defines_language(alphabet=["a", "b"])
phi.test_on_words(length_up_to=8)
```

Y traducciones:

```python
FO_on_words.to_automaton()
MSO_on_words.to_automaton()
```

## 14. Monoide sintáctico

Como puente con álgebra:

```python
L = RegularLanguage.from_automaton(A)
M = L.syntactic_monoid()
```

Y luego:

```python
L.is_fo_definable()
L.is_star_free()
M.is_aperiodic()
```

Esto sería una conexión hermosa entre teoría de modelos finitos, autómatas y álgebra universal.

## 15. Separación por juegos automática

Ya hablamos de juegos, pero faltó convertirlos en **certificados de no definibilidad**:

```python
Inexpressibility.by_ef_game(A, B, rounds=4)
Inexpressibility.by_pebble_game(A, B, pebbles=3)
Inexpressibility.by_counting_game(A, B, pebbles=3)
```

Salida:

```text
Duplicador tiene estrategia ganadora.
Por lo tanto, ninguna fórmula FO de rango cuantificacional ≤ 4 distingue A de B.
```

Eso es más fuerte que un simple `False`.

## 16. Síntesis de fórmulas separadoras

Lo dual de lo anterior:

```python
SeparatingFormula(A, B, logic="FO", max_rank=4).find()
```

Si Spoiler gana, la librería debería construir una fórmula que distingue:

```text
A ⊨ φ
B ⊭ φ
```

Esto une juegos con síntesis de fórmulas.

## 17. Cálculo de rango cuantificacional mínimo

Para una propiedad o consulta:

```python
minimal_quantifier_rank(property, examples, logic="FO")
```

Ejemplo:

```text
La propiedad distingue estos grafos recién a rango cuantificacional 5.
```

Esto es muy finito-model-teórico.

## 18. Módulo de indistinguibilidad lógica

Una API general:

```python
A.indistinguishable_from(
    B,
    logic="FO",
    resources={
        "variables": 3,
        "quantifier_rank": 5,
        "counting": False
    }
)
```

Y para tuplas:

```python
A.tuple_type((a,b), logic="FO3", rank=4)
```

Esto se vuelve una herramienta muy potente de clasificación.

## 19. Datalog con semántica incremental

No solo evaluar Datalog; hacerlo como punto fijo observable:

```python
program.evaluate(A, trace=True)
```

Salida:

```text
Iteración 0: Path = ∅
Iteración 1: agrega aristas directas
Iteración 2: agrega caminos de longitud 2
...
Punto fijo alcanzado en 4 iteraciones
```

Esto sirve para enseñar y para depurar.

## 20. Estratificación y negación

Datalog básico es positivo. Pero una librería útil debería manejar:

```python
DatalogProgram(...).is_stratified()
DatalogProgram(...).strata()
DatalogProgram(...).evaluate_stratified()
```

Con negación estratificada:

```prolog
Reach(x,y) :- Edge(x,y).
Reach(x,z) :- Edge(x,y), Reach(y,z).
NotReach(x,y) :- Node(x), Node(y), not Reach(x,y).
```

## 21. Captura de clases sub-PTIME

No solo NP y PTIME. Faltaban clases finas:

```python
Logic("FO").captures("AC0", ordered=True)
Logic("FO+TC").captures("NL", ordered=True)
Logic("FO+DTC").captures("L", ordered=True)
Logic("FO+LFP").captures("PTIME", ordered=True)
Logic("FO+PFP").captures("PSPACE", ordered=True)
```

Estas correspondencias son parte del paisaje de complejidad descriptiva; el libro trata lógicas de punto fijo, clausura transitiva e infinitarias como lógicas importantes para esta conexión. ([PhilPapers][2])

## 22. Problemas completos como objetos

Una librería publicable debería traer problemas canónicos:

```python
Problems.GraphReachability()
Problems.ThreeColorability()
Problems.SAT()
Problems.HamiltonianPath()
Problems.Clique(k)
Problems.QueryContainment()
```

Y para cada uno:

```python
problem.logic_definitions()
problem.known_complexity()
problem.standard_reductions()
problem.random_instances()
```

## 23. Reducción inversa: fórmula → algoritmo

Dada una fórmula de cierto lenguaje, generar algoritmo:

```python
Algorithm.from_logic(phi, logic="LFP")
```

Ejemplo:

```python
reachable = TC(E)
alg = reachable.to_algorithm()
```

Esto haría explícita la promesa computacional de cada lógica.

## 24. Pequeños modelos y bounds

Para ciertos fragmentos, sería útil:

```python
phi.small_model_bound(fragment="monadic")
phi.has_finite_model_property()
```

No en general, porque FO finito es indecidible, pero sí para fragmentos restringidos.

## 25. Fragmentos decidibles de FO finita

Faltaba una lista operativa:

```python
Fragment("monadic_fo").decide_finite_satisfiability(phi)
Fragment("guarded").model_check(phi, A)
Fragment("two_variable").analyze(phi)
```

Fragmentos importantes:

```text
FO²
FO² con conteo
monadic FO
guarded fragment
existential positive
universal Horn
Bernays–Schönfinkel
```

Esto sería tremendamente útil para saber cuándo hay algoritmos completos.

## 26. Clasificador de fragmento lógico

Dada una fórmula:

```python
phi.classify_fragment()
```

Salida:

```text
FO
usa 3 variables
rango cuantificacional 4
alternancia Σ₂
sin negación sobre relaciones intensionales
pertenece a guarded fragment: no
pertenece a FO²: no
pertenece a existential positive: sí
```

Esto ayuda muchísimo en investigación.

## 27. Contención entre lógicas sobre clases finitas

Una base de conocimiento interna:

```python
Logic("FO2") <= Logic("FO")
Logic("FO") < Logic("LFP")
Logic("LFP") <= Logic("PFP")
```

Pero parametrizada:

```python
over="ordered finite structures"
over="words"
over="trees"
over="graphs"
```

Porque las relaciones cambian según la clase de estructuras.

## 28. Generación de ejemplos separadores de lógicas

Esto sería muy lindo:

```python
separate_logics(
    weaker="FO",
    stronger="FO+TC",
    property="reachability",
    max_size=8
)
```

O:

```python
find_property_definable_in("FO3").not_definable_in("FO2")
```

La salida ideal:

```text
Propiedad candidata, ejemplos positivos/negativos, juego que certifica separación.
```

## 29. Módulo de “lógica como lenguaje de consulta”

Para bases de datos:

```python
DatabaseInstance(...)
RelationalQuery(...)
ActiveDomainSemantics(...)
```

Distinguir:

* semántica de dominio total;
* semántica de dominio activo;
* consultas seguras;
* independencia del dominio.

Esto es muy importante: en bases de datos, no querés que una consulta dependa de elementos que no aparecen en la base.

## 30. Seguridad de consultas

```python
Query(phi).is_domain_independent()
Query(phi).is_safe()
Query(phi).safe_rewrite()
```

Esto conecta FO con cálculo relacional seguro.

---

Mi lista de “faltantes finales” quedaría así:

```text
model checking complexity
codificación de cómputos
jerarquías de alternancia
jerarquías por aridad
satisfacibilidad finita e indecidibilidad
teoría casi segura
axiomas de extensión
uniformidad
strings como estructuras
monoides sintácticos
certificados de juegos
Datalog estratificado
clases sub-PTIME
fragmentos decidibles
clasificación automática de fórmulas
dominio activo y seguridad de consultas
```

Con todo eso, la librería deja de ser solo una herramienta para manipular estructuras y pasa a ser algo más ambicioso:

> una plataforma para experimentar con **expresividad lógica finita**, donde cada fórmula viene acompañada de su costo, su fragmento, sus límites, sus traducciones y sus posibles certificados de no-definibilidad.

## Véase también

* Trakhtenbrot.
* Espectros finitos.
* Axiomas de extensión.
* Teoría casi segura.
* FO[BIT].
* Monoide sintáctico.
* Datalog estratificado.
* Seguridad de consultas.
* Alternancia cuantificacional.
* Complejidad combinada del model checking.

[1]: https://link.springer.com/book/10.1007/3-540-28788-4?utm_source=chatgpt.com "Finite Model Theory: Second Edition | Springer Nature Link"
[2]: https://philpapers.org/rec/EBBFMT?utm_source=chatgpt.com "Heinz-Dieter Ebbinghaus & Jörg Flum, Finite Model Theory"



Sí. Ya estamos en la **capa residual**, pero todavía hay cosas importantes, sobre todo si la librería quiere cubrir no solo álgebra universal sino el espíritu completo de *Finite Model Theory*. Ebbinghaus–Flum enfatiza justamente la conexión entre estructuras finitas, complejidad descriptiva, bases de datos, Datalog, cuantificadores, leyes 0-1, optimización y aproximación. ([Springer][1])

