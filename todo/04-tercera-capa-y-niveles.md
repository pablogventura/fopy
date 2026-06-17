# Tercera Capa Y Niveles

> **Prioridad:** ver [README.md](README.md)  
> **Resumen:** Laboratorio de contraejemplos, perfiles, invariantes, descubrimiento; Niveles 1–3 de madurez.

> **Origen:** líneas 863–1338 de `todo.md`

<!-- segment-header-end -->
Sí: queda una **tercera capa**, más de frontera. Ya no son “features obvias”, sino cosas que podrían hacer que la librería sea **distinta**.

## 1. Un laboratorio de contraejemplos

No solo:

```python
find_counterexample(axioms, conjecture)
```

Sino:

```python
CounterexampleLab(theory).search(
    sizes=range(2, 9),
    prefer="smallest_nontrivial",
    avoid_isomorphic=True,
    explain_failure=True,
)
```

Y que devuelva algo publicable:

```text
El menor contraejemplo tiene tamaño 4.
Es subdirectamente irreducible.
Tiene 3 congruencias.
Falla la identidad en la valuación x=..., y=...
```

Esto competiría conceptualmente con buscadores finitos tipo Mace4/Nitpick/Kodkod, pero especializado en álgebra universal. Nitpick, por ejemplo, se apoya en Kodkod como buscador relacional finito basado en SAT. ([tcs.ifi.lmu.de][1])

## 2. Cálculo de “perfiles algebraicos”

Para cada álgebra:

```python
A.profile()
```

Que diga:

```text
tamaño: 5
idempotente: sí
conmutativa: no
congruence distributive: no
congruence permutable: sí
término de Maltsev: sí
término de mayoría: no
Taylor: sí
Siggers: sí
subdirectamente irreducible: no
```

Sería una especie de `fingerprint` matemático.

## 3. Motor de invariantes

Algo como:

```python
A.invariants()
```

Con invariantes útiles para filtrar búsquedas:

* cantidad de subálgebras;
* cantidad de congruencias;
* tipos de congruencias;
* cardinalidades de cocientes;
* automorfismos;
* endomorfismos;
* funciones término por aridad;
* tamaño del clon parcial calculado;
* relaciones invariantes bajo el clon;
* espectro de subálgebras generadas.

CREAM/GAP ya apunta a calcular automorfismos, endomorfismos, isomorfismos, congruencias, divisores y subálgebras para muchas álgebras finitas, así que una librería nueva tendría que justificar muy bien qué aporta encima de eso. ([arXiv][2])

## 4. Álgebra de reductos y expansiones

Esto sería muy útil:

```python
B = A.reduct(["join"])
C = A.expand({"R": relation})
```

Y luego:

```python
A.definitional_reducts()
A.minimal_expansions_preserving(property="pp_definability")
```

Preguntas que podría responder:

* qué operaciones son redundantes;
* qué relaciones son definibles desde las operaciones;
* qué expansión hace definible cierta relación;
* cuál es la signatura mínima para preservar una teoría;
* cuándo dos expansiones son definicionalmente equivalentes.

## 5. Explicación de “por qué no se puede”

La mayoría de las herramientas dice `False`. Una librería buena debería decir:

```python
result = Definability.check(A, R, fragment="pp")
result.explain_obstruction()
```

Ejemplo:

```text
R no es pp-definible porque no está preservada por este polimorfismo binario p.

Tupla en R:
  (a,b), (c,d)

Pero:
  p((a,b),(c,d)) = (e,f) ∉ R
```

Eso conecta directo con el enfoque algebraico de CSP, donde los polimorfismos son centrales para entender complejidad y definibilidad. ([karlin.mff.cuni.cz][3])

## 6. Modo “descubridor de teoremas”

Esto sería hermoso:

```python
Discover(theory).conjectures(max_size=6)
```

Que genere conjeturas del tipo:

```text
Toda álgebra de esta clase con término de Maltsev y tamaño ≤ 6 parece tener ...
```

Y después busque contraejemplos:

```python
conjecture.test(sizes=range(2, 9))
```

No reemplaza al matemático; le da una lupa.

## 7. Minimización de estructuras

Si una conjetura falla, reducir el contraejemplo:

```python
minimize_counterexample(A, property_failure)
```

Buscando:

* subálgebra más chica que falla;
* cociente que falla;
* reducto que todavía falla;
* subconjunto de operaciones necesario para que falle;
* subconjunto mínimo de axiomas usado.

Eso es oro para papers.

## 8. Comparador de teorías

Algo así:

```python
compare(T1, T2, max_size=7)
```

Salida:

```text
T1 implica T2 hasta tamaño 7.
T2 no implica T1: contraejemplo de tamaño 4.
```

Y además:

```python
T1.independent_axioms(max_size=6)
```

Para buscar independencia de axiomas mediante modelos finitos.

## 9. Base de datos versionada de experimentos

No solo guardar resultados, sino experimentos reproducibles:

```python
Experiment(
    name="qf_definability_lattices_size_6",
    code=...,
    structures=...,
    seed=...
).run()
```

Y que produzca:

* JSON;
* notebook;
* tablas LaTeX;
* hashes;
* versiones de dependencias;
* certificados.

Sin esto, los resultados computacionales son frágiles.

## 10. Algoritmos certificados por doble vía

Por ejemplo, para una definición encontrada:

1. el algoritmo produce fórmula;
2. un verificador independiente chequea exhaustivamente;
3. opcionalmente exporta a Lean/Isabelle/Coq.

Para ecuaciones, existe toda una línea de demostradores ecuacionales basados en Knuth-Bendix, como Twee o Waldmeister; Twee implementa completion ecuacional y fue presentado como demostrador de lógica ecuacional. ([research.chalmers.se][4])

## 11. Puente con Maude / reescritura

Maude ya tiene herramientas para especificaciones ecuacionales, incluyendo chequeo Church-Rosser, terminación y completion de Knuth-Bendix. ([maude.cs.illinois.edu][5])

Entonces una librería Python podría hacer:

```python
theory.to_maude()
maude_result = MaudeBackend.complete(theory)
```

Y traer de vuelta:

```python
rewrite_system = maude_result.to_rewrite_system()
```

Eso sería muy potente para combinar **álgebra finita + reescritura simbólica**.

## 12. Modo “complejidad computacional”

Para cada problema:

```python
Problem("has_malcev_term").complexity_hint()
```

No como verdad absoluta, sino como orientación:

```text
Búsqueda ingenua: O(n^(n^k))
Reducción usada: SAT con simetrías
Cuello de botella: enumeración de operaciones ternarias
```

Esto ayuda a que el matemático entienda por qué algo explota.

## 13. Búsqueda guiada por tipos de términos

En vez de enumerar todos los términos, buscar por esquemas:

```python
A.search_term(
    arity=3,
    identities=[
        "t(x,x,y)=y",
        "t(x,y,y)=x"
    ],
    strategy="cegis"
)
```

Y permitir familias:

* Maltsev;
* mayoría;
* near-unanimity;
* Siggers;
* Jónsson;
* Day;
* Gumm;
* Pixley;
* weak near-unanimity.

## 14. Módulo de dualidades finitas

Esto sería más sofisticado:

```python
Duality.find_alter_ego(A)
Duality.test_natural_duality(A, alter_ego)
```

Para álgebras finitas con dualidades naturales. No es necesario para un MVP, pero sería muy publicable si se hace bien.

## 15. Topología / orden / enriquecimientos

Muchas estructuras algebraicas interesantes tienen orden, topología finita, grafo subyacente o métrica discreta útil.

```python
A.with_order(leq)
A.order_compatible_operations()
A.monotone_term_functions()
```

Útil para:

* reticulados;
* álgebras de Heyting;
* álgebras residuadas;
* semirreticulados;
* ordered algebras.

## 16. Un “modo paper”

Esto parece menor, pero no lo es:

```python
result.to_paper_section()
```

Que produzca:

* enunciado;
* tabla;
* fórmula LaTeX;
* contraejemplo;
* diagrama;
* código reproducible;
* cita del experimento.

Ejemplo:

```latex
The following 4-element algebra refutes identity ...
```

Eso haría que la librería sea una herramienta de escritura matemática.

## 17. Interfaz tipo shell matemática

Algo como:

```bash
folua
> load lattice_5.ua
> congruences
> define R by qf
> find counterexample distributive -> modular size <= 6
```

No todo debería ser Python puro. Una REPL especializada puede ser muy cómoda.

## 18. Pedagogía avanzada

Como sos docente, metería un modo didáctico:

```python
A.explain_congruence_generation(theta)
A.explain_formula_evaluation(phi)
A.explain_subalgebra_generated_by(S)
```

Que muestre paso a paso cómo se cierra un conjunto por operaciones, cómo se genera una congruencia, cómo se evalúa una fórmula cuantificada, etc.

Eso no solo sirve para enseñar: también sirve para depurar.

## 19. Integración con gráficos de búsqueda

Visualizar la búsqueda:

```python
SearchTree(...).draw()
```

Para ver:

* ramas podadas;
* simetrías eliminadas;
* candidatos descartados;
* contraejemplos encontrados;
* fórmulas equivalentes colapsadas.

## 20. Una teoría de “experimentos algebraicos”

La capa más publicable quizás no sea una función, sino un concepto:

```python
AlgebraicExperiment = {
    structures,
    fragment,
    property,
    search_strategy,
    certificate_type
}
```

Y que todo resultado sea:

```python
TheoremCandidate
Counterexample
Certificate
Obstruction
Benchmark
```

Eso le daría identidad científica.

---

Mi veredicto: **sí hay más**, pero ya no agregaría cosas al azar. Haría tres niveles:

## Nivel 1: librería útil

* FOL;
* estructuras finitas;
* evaluación;
* congruencias;
* subálgebras;
* homomorfismos;
* definibilidad;
* síntesis de fórmulas.

## Nivel 2: librería publicable

* certificados;
* finite model finding;
* búsqueda hasta isomorfismo;
* benchmarks;
* interoperabilidad UACalc/GAP/Mace4/TPTP/SMT-LIB;
* contraejemplos mínimos.

## Nivel 3: librería de investigación fuerte

* clones;
* CSP;
* Tame Congruence Theory;
* dualidades;
* descubrimiento de conjeturas;
* HSP computacional;
* reescritura ecuacional;
* exportación a asistentes de prueba;
* experimentos reproducibles.

La frase más honesta sería:

> Una librería publicable no debería intentar hacer “toda la lógica de primer orden”. Debería resolver de manera excelente un triángulo muy específico: **álgebra universal finita + definibilidad + contraejemplos certificados**.

Ese triángulo sí tiene personalidad propia.

## Véase también

* Universal Algebra Calculator.
* CREAM para GAP.
* Mace4.
* Nitpick y Kodkod.
* Maude.
* Twee y Waldmeister.
* CSP algebraico.
* Tame Congruence Theory.
* Dualidades naturales.
* Síntesis de fórmulas.

[1]: https://www.tcs.ifi.lmu.de/staff/jasmin-blanchette/itp2010-nitpick.pdf?utm_source=chatgpt.com "Nitpick: A Counterexample Generator for Higher-Order ..."
[2]: https://arxiv.org/abs/2202.00613?utm_source=chatgpt.com "CREAM: a Package to Compute [Auto, Endo, Iso, Mono, Epi]-morphisms, Congruences, Divisors and More for Algebras of Type $(2^n,1^n)$"
[3]: https://www.karlin.mff.cuni.cz/~barto/Articles/polymorphisms.pdf?utm_source=chatgpt.com "Polymorphisms, and how to use them"
[4]: https://research.chalmers.se/en/publication/525501?utm_source=chatgpt.com "Twee: An Equational Theorem Prover"
[5]: https://maude.cs.illinois.edu/maude1/tools/?utm_source=chatgpt.com "A Set of Proving Tools for Maude Specifications"



