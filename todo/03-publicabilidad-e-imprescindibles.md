# Publicabilidad E Imprescindibles

> **Prioridad:** ver [README.md](README.md)  
> **Resumen:** Interoperabilidad, finite model finding, isomorfismo, certificados, HSP, clones/CSP, TCT; lista de 20 imprescindibles.

> **Origen:** líneas 404–862 de `todo.md`

<!-- segment-header-end -->
No. **Sería un muy buen núcleo**, pero no sería “todo lo realmente útil”. Para que sea **publicable**, la pregunta no es solo “qué funciones tiene”, sino **qué hace mejor, más nuevo o más integradamente que UACalc, Mace4, Sage, GAP/Cream, Z3, etc.** UACalc ya trabaja con álgebras finitas, reticulados de congruencias y subálgebras; Mace4 ya busca modelos finitos de fórmulas de primer orden; Sage ya tiene infraestructura para reticulados finitos y congruencias de reticulados; y Cream/GAP apunta a operaciones rápidas sobre álgebras universales finitas. ([UACalc][1])

Lo que faltaría para que sea **realmente redondo y publicable**:

## 1. Importar y exportar ecosistema existente

Imprescindible:

```python
A = load_uacalc("algebra.ua")
A.to_uacalc("out.ua")
phi.to_tptp()
phi.to_smtlib()
A.to_gap()
A.to_sage()
```

Sin eso, queda aislada. La librería debería funcionar como **puente Python moderno** entre álgebra universal, lógica finita y demostración automática.

## 2. Finite model finder propio o wrapper serio

No basta con evaluar fórmulas en una estructura dada. Haría falta:

```python
find_model(theory, size=5)
find_counterexample(axioms, conjecture, max_size=8)
```

Eso la acerca al rol de Mace4, que busca estructuras finitas para fórmulas de primer orden, especialmente como contraejemplos a conjeturas. ([Ciencias de la Computación][2])

Pero la novedad podría ser que esté **sesgado hacia álgebra universal**:

* operaciones totales por defecto;
* identidades ecuacionales;
* simetrías de tablas;
* reducción por isomorfismo;
* filtros por congruencias;
* búsqueda de contraejemplos con propiedades algebraicas.

## 3. Ruptura de simetrías e isomorfismo

Esto es clave. La búsqueda de álgebras finitas explota porque muchas tablas son isomorfas.

Necesitaría:

```python
A.canonical_form()
A.is_isomorphic_to(B)
enumerate_algebras(signature, size=n, up_to_iso=True)
```

Y para modelos:

```python
find_models(theory, size=n, nonisomorphic=True)
```

Sin esto, cualquier búsqueda seria muere combinatoriamente.

## 4. Certificados verificables

Para ser publicable, no alcanza con devolver `True`.

Debería devolver certificados:

```python
result.certificate()
result.verify()
```

Ejemplos:

* certificado de que una relación es definible;
* certificado de no-definibilidad;
* testigos de separación;
* modelo finito contraejemplo;
* prueba ecuacional;
* traza de búsqueda reproducible;
* hash de estructura;
* script minimal que reproduce el resultado.

Esto es muy importante si querés que otros matemáticos confíen en resultados computacionales.

## 5. Algoritmos de preservación

Para definibilidad, no todo debería ser búsqueda bruta.

Agregaría criterios tipo:

```python
is_pp_definable(R, A)
is_qf_definable(R, A)
is_ep_definable(R, A)
```

Pero internamente usando invariantes:

* preservación por homomorfismos;
* preservación por subestructuras;
* preservación por productos;
* preservación por automorfismos;
* separación por tipos atómicos;
* clausuras Galois `Pol–Inv`.

Esto la vuelve matemática, no solo computacional.

## 6. Clones, polimorfismos y CSP

Esto sería un módulo mayor:

```python
clone = A.term_clone(max_arity=4)
pols = Pol(R1, R2, R3)
invs = Inv(operations)
```

Funciones deseables:

* calcular funciones término;
* calcular clon generado;
* comparar clones;
* buscar términos especiales;
* calcular polimorfismos de relaciones;
* traducir problemas a CSP;
* detectar condiciones de Taylor/Siggers/near-unanimity.

Esto conecta álgebra universal moderna con complejidad computacional.

## 7. Tame Congruence Theory computacional

Si apuntás alto, metería:

```python
A.tct_types()
A.has_taylor_term()
A.has_siggers_term()
A.has_malcev_term()
A.has_majority_term()
A.has_day_terms()
A.has_gumm_terms()
```

Esto sería muy publicable si está bien hecho, porque no es una feature cosmética: son propiedades profundas de variedades generadas por álgebras finitas.

## 8. Birkhoff / HSP / variedades generadas

Módulo central:

```python
V = Variety.generated_by(A)

B in V
V.free_algebra(generators=2, max_size=...)
V.subdirectly_irreducibles(max_size=...)
V.identity_basis(max_depth=...)
```

Operaciones:

* cierre por H, S, P;
* pertenencia finita aproximada;
* álgebras libres finitas;
* subdirect decomposition;
* búsqueda de identidades válidas;
* búsqueda de bases ecuacionales pequeñas;
* independencia de axiomas.

Esto ya es álgebra universal “de verdad”.

## 9. Reescritura ecuacional

Agregaría un motor de términos:

```python
rewrite_system = KnuthBendix(identities)
normal_form = rewrite_system.normalize(term)
```

Con:

* unificación;
* matching;
* completion;
* critical pairs;
* reducción módulo teoría;
* orientación por orden de términos;
* búsqueda de pruebas ecuacionales.

Esto complementa la parte semántica finita con razonamiento sintáctico.

## 10. Minimalidad y explicación

La librería debería poder responder:

```python
minimal_formula(A, R, fragment="qf")
```

Pero además:

```python
prove_minimality=True
```

O sea:

> “Esta relación se define con profundidad 2, y no existe definición con profundidad 1.”

Eso es mucho más fuerte que solo encontrar una fórmula.

## 11. Benchmark suite

Para publicar, haría falta una colección de problemas:

```text
benchmarks/
  lattices/
  semilattices/
  quasigroups/
  small_algebras/
  definability/
  tct/
  csp/
  mace4_comparison/
  uacalc_comparison/
```

Con métricas:

* tiempo;
* memoria;
* tamaño del universo;
* aridad máxima;
* cantidad de operaciones;
* cantidad de relaciones;
* cantidad de fórmulas exploradas;
* cantidad de modelos no isomorfos.

Sin benchmark, es difícil convencer a nadie.

## 12. Base de datos de estructuras chicas

Algo estilo:

```python
SmallAlgebras.load("lattice", size=5)
SmallAlgebras.search(properties=["distributive", "non_boolean"])
```

Con filtros:

* tamaño;
* signatura;
* idempotencia;
* conmutatividad;
* asociatividad;
* congruence distributive;
* congruence permutable;
* simple;
* subdirectly irreducible;
* finitely based / nonfinitely based, cuando se sepa.

UACalc ya tiene archivos de ejemplo clásicos, incluyendo reticulados pequeños y álgebras famosas, así que convendría interoperar con ese mundo en vez de competir ingenuamente. ([UACalc][3])

## 13. Módulo de “descubrimiento”

Esto sí sería muy interesante:

```python
Discover(A).interesting_relations()
Discover(A).candidate_theorems()
Discover(A).unexpected_congruences()
Discover(A).small_counterexamples()
```

La idea: que el sistema sugiera cosas.

Ejemplos:

* “esta relación parece definible primitivamente positiva”;
* “esta identidad falla solo en estas dos tuplas”;
* “esta álgebra tiene pocas congruencias para su tamaño”;
* “este reducto conserva todas las relaciones relevantes”;
* “hay un término ternario que se comporta casi como mayoría”.

Eso la convierte en asistente de investigación.

## 14. DSL declarativo

Algo así:

```python
@theory
class Lattice:
    join: BinOp
    meet: BinOp

    axioms = [
        forall(x, y, join(x, y) == join(y, x)),
        forall(x, y, meet(x, y) == meet(y, x)),
        forall(x, y, join(x, meet(x, y)) == x),
    ]
```

Y también una sintaxis matemática:

```text
theory Lattice {
  ∀x y. x∨y = y∨x
  ∀x y. x∧y = y∧x
  ∀x y. x∨(x∧y) = x
}
```

Esto es importante para adopción.

## 15. Tipos dependientes livianos / muchos-sorted

Álgebra universal clásica suele ser unisorted, pero para matemáticos conviene soportar muchos-sorted:

```python
GroupAction = Signature(
    sorts=["G", "X"],
    operations={
        "*": ("G", "G", "G"),
        "act": ("G", "X", "X"),
    }
)
```

Los buscadores de modelos finitos muchos-sorted tienen dificultades específicas porque cada sort puede tener distinto tamaño; hay trabajos dedicados a esa explosión combinatoria. ([arXiv][4])

## 16. Relational structures además de algebras

No limitaría la librería a operaciones. Universal algebra moderna dialoga mucho con estructuras relacionales:

```python
M = FiniteStructure(
    universe=[0,1,2],
    relations={"R": {(0,1), (1,2)}},
    operations={"f": ...}
)
```

Eso permite:

* teoría de modelos finitos;
* CSP;
* definibilidad relacional;
* polimorfismos;
* interpretabilidad;
* reductos y expansiones.

## 17. Interpretaciones y equivalencia definicional

Módulo avanzado:

```python
interpret(A, in_structure=B, by=formulas)
A.definitionally_equivalent(B)
A.biinterpretable_with(B)
```

Esto sería muy útil para comparar estructuras, teorías y expansiones.

## 18. Visualización avanzada

No solo dibujar Hasse.

También:

```python
A.operation_table("join").heatmap()
A.congruence_lattice().interactive()
A.subalgebra_lattice().interactive()
result.obstruction_graph().draw()
```

Y exportación a:

* LaTeX;
* TikZ;
* Graphviz;
* SVG;
* HTML;
* notebooks reproducibles.

## 19. Integración con Lean/Isabelle/Coq

No necesariamente probar todo ahí, pero sí exportar declaraciones:

```python
result.to_lean()
result.to_isabelle()
```

Sería útil para que un resultado computacional pueda transformarse en un lema verificable.

## 20. Publicabilidad real: cuál sería la tesis fuerte

La librería sería publicable si el paper no dice solo:

> “Implementamos una librería de lógica de primer orden.”

Eso no alcanza.

Algo publicable sería:

> “Presentamos una librería Python para álgebra universal finita que integra definibilidad, síntesis de fórmulas, búsqueda de modelos finitos, certificados verificables e interoperabilidad con UACalc/Mace4/Sage/GAP; además introducimos nuevos algoritmos de no-definibilidad cuantificador-libre basados en separación semántica de tipos término.”

Ahí sí.

## Mi lista final de imprescindibles

Si tuviera que elegir lo **realmente importante**, lo dejaría así:

1. sintaxis FOL robusta;
2. estructuras finitas muchos-sorted;
3. evaluación eficiente de fórmulas;
4. términos y funciones término;
5. subálgebras, congruencias, cocientes, homomorfismos;
6. reticulados de subálgebras y congruencias;
7. definibilidad por fragmentos;
8. síntesis de fórmulas mínimas;
9. testigos de no-definibilidad;
10. finite model finding;
11. búsqueda de contraejemplos;
12. simetrías e isomorfismo;
13. HSP y variedades generadas;
14. términos de Maltsev/Taylor/Siggers/mayoría;
15. clones y polimorfismos;
16. CSP;
17. reescritura ecuacional;
18. certificados verificables;
19. interoperabilidad con UACalc, Mace4, TPTP, SMT-LIB, Sage y GAP;
20. benchmarks reproducibles.

Con eso sí estaríamos hablando de una herramienta seria, útil y defendible como contribución científica.

## Véase también

* Universal Algebra Calculator.
* Mace4 y Prover9.
* TPTP.
* SMT-LIB.
* Tame Congruence Theory.
* Clones y polimorfismos.
* CSP algebraico.
* HSP y teorema de Birkhoff.
* Definibilidad cuantificador-libre.
* Síntesis de fórmulas.

[1]: https://www.uacalc.org/description.html?utm_source=chatgpt.com "UACalc (Semi) Technical Description"
[2]: https://www.cs.unm.edu/~mccune/prover9/manual/2009-02A/mace4.html?utm_source=chatgpt.com "Prover9 Manual: Mace4"
[3]: https://uacalc.org/algfiles/?utm_source=chatgpt.com "UACalc -- Universal Algeba Calculator"
[4]: https://arxiv.org/abs/1604.08040?utm_source=chatgpt.com "Finding Finite Models in Multi-Sorted First Order Logic"



