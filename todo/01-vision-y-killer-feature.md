# Vision Y Killer Feature

> **Prioridad:** ver [README.md](README.md)  
> **Resumen:** Visión inicial, núcleo lógico (§1–11), killer feature explain_definibility, diseño interno, nombre tentativo.

> **Origen:** líneas 1–403 de `todo.md`

<!-- segment-header-end -->
Yo la haría **centrada en estructuras finitas, términos y definibilidad**, no como una librería genérica de lógica. Algo así:

## 1. Núcleo lógico

Incluiría una representación fuerte de:

```python
x, y, z = Vars("x y z")
f = Function("f", 2)
g = Function("g", 1)
R = Relation("R", 2)

phi = ForAll(x, Exists(y, R(f(x, y), g(x))))
```

Con soporte para:

* igualdad;
* funciones y relaciones de aridad arbitraria;
* lógica muchos-sorted;
* sustitución sin captura;
* variables libres y ligadas;
* alfa-equivalencia;
* forma prenexa, NNF, CNF, DNF;
* normalización de términos;
* impresión en LaTeX, texto y Python;
* parser tipo matemático:
  `∀x ∃y R(f(x,y),g(x))`.

También pondría exportación a **TPTP**, porque TPTP es un estándar usado en demostración automática y soporta fórmulas de primer orden, CNF y lógicas tipadas como TFF/THF. ([tptp.org][1])

## 2. Estructuras algebraicas finitas como objeto central

Algo así:

```python
A = FiniteAlgebra(
    universe=[0, 1, 2],
    operations={
        "join": table_join,
        "meet": table_meet,
        "neg": table_neg,
    }
)
```

Operaciones básicas:

* evaluar términos en un álgebra;
* evaluar fórmulas en una estructura;
* producto directo;
* subálgebras generadas;
* homomorfismos;
* embeddings;
* isomorfismos;
* congruencias;
* cocientes;
* reticulado de congruencias;
* álgebras simples, subdirectamente irreducibles;
* términos, polinomios y funciones término;
* clon de operaciones término, al menos para universos pequeños.

Ejemplo lindo:

```python
A.subalgebra_generated_by([0, 1])
A.congruence_lattice()
A.term_functions(max_depth=4)
A.is_subdirectly_irreducible()
```

## 3. Model checking finito

Para álgebra universal finita, esto es clave:

```python
A.models(phi)
A.counterexample(phi)
A.satisfying_assignments(phi)
```

Con evaluación eficiente por:

* tablas;
* bitsets;
* `numpy`;
* cacheo de subfórmulas;
* evaluación por cuantificadores acotados;
* testigos explícitos para `∃`;
* contraejemplos explícitos para `∀`.

Ejemplo:

```python
phi = ForAll([x, y], Eq(join(x, y), join(y, x)))
A.models(phi)
# True
```

## 4. Módulo de definibilidad

Este sería el corazón diferencial.

Incluiría:

```python
Definability.check(
    structure=A,
    relation=R_target,
    fragment="qf"   # qf, pp, ep, horn, fo
)
```

Fragmentos:

* cuantificador-libre;
* ecuacional;
* conjunciones de ecuaciones;
* primitivamente positivo;
* existencial positivo;
* Horn;
* primer orden completo, cuando el universo es chico.

Y no solo decir `True/False`, sino devolver algo matemáticamente útil:

```python
result.is_definable
result.formula
result.obstruction
result.witnesses
```

Por ejemplo:

```python
R = A.relation([(0,0), (1,1), (2,2)])
Definability.synthesize(A, R, fragment="qf")
```

Salida esperable:

```python
x = y
```

## 5. Síntesis de fórmulas

No solo verificar fórmulas: **encontrarlas**.

```python
FormulaSearch(
    signature=A.signature,
    target_relation=R,
    fragment="qf",
    max_depth=5,
    minimize=True
).run()
```

Estrategias:

* enumeración por tamaño;
* poda por equivalencia semántica;
* CEGIS: proponer fórmula, buscar contraejemplo, refinar;
* codificación SAT/SMT;
* ranking por simplicidad;
* eliminación de redundancias;
* explicación humana.

Esto sería muy útil para descubrir definiciones en estructuras chicas.

## 6. Interoperabilidad con demostradores

Tendría backends:

```python
phi.to_tptp()
phi.to_smtlib()
phi.to_z3()
```

SMT-LIB es una iniciativa estándar para facilitar investigación y desarrollo en SMT, así que conviene soportarlo como formato de intercambio. ([smt-lib.org][2])

Para Z3, sería útil como backend pragmático, pero con cuidado: Z3 puede manejar cuantificadores, aunque su guía aclara que usa técnicas como instanciación por patrones y que eso es inherentemente incompleto en general. ([microsoft.github.io][3])

O sea: usaría Z3 como motor auxiliar, no como fundamento matemático único.

## 7. Categorías algebraicas comunes

Constructores prearmados:

```python
BooleanAlgebra(n=2)
Lattice(...)
Semilattice(...)
Group(...)
Monoid(...)
Ring(...)
Module(...)
HeytingAlgebra(...)
RelationAlgebra(...)
```

Y propiedades:

```python
A.is_lattice()
A.is_distributive_lattice()
A.is_boolean_algebra()
A.is_malcev()
A.has_majority_term()
A.has_near_unanimity_term()
```

Esto permitiría buscar términos de Maltsev, mayoría, Jónsson, Pixley, near-unanimity, etc.

Ejemplo:

```python
A.find_term_identity(
    equations=[
        Eq(t(x, x, y), y),
        Eq(t(x, y, y), x)
    ],
    max_depth=4
)
```

## 8. Identidades, variedades y cuasivariedades

Incluiría objetos como:

```python
V = Variety(axioms=[
    ForAll([x, y], Eq(join(x, y), join(y, x))),
    ForAll([x, y, z], Eq(join(x, join(y, z)), join(join(x, y), z)))
])
```

Operaciones:

* verificar si un álgebra satisface identidades;
* generar consecuencias chicas;
* buscar contraejemplos finitos;
* calcular álgebra libre finita, cuando sea posible;
* comparar teorías ecuacionales;
* minimizar bases de identidades;
* buscar independencia de axiomas con modelos finitos.

## 9. Reticulados y visualización

Para matemáticos de álgebra universal, la visualización importa mucho:

```python
A.congruence_lattice().draw()
A.subalgebra_lattice().draw()
A.hasse_diagram()
```

Exportaría a:

* Graphviz;
* Mermaid;
* TikZ;
* SVG;
* HTML interactivo.

## 10. Una API “de cuaderno”

La librería debería sentirse natural en Jupyter:

```python
A.show_tables()
phi.latex()
A.draw_congruences()
Definability.explain(A, R)
```

Y cada resultado importante debería ser inspeccionable:

```python
result.pretty()
result.latex()
result.proof_sketch()
result.counterexample_table()
```

## 11. Diseño interno que elegiría

Internamente usaría:

* AST inmutable para términos y fórmulas;
* hash-consing para compartir subexpresiones;
* firmas explícitas;
* separación entre sintaxis y semántica;
* evaluación vectorizada;
* relaciones como bitsets;
* operaciones como arrays multidimensionales;
* simplificación semántica respecto de una estructura finita;
* sistema de plugins para backends externos.

Algo tipo:

```python
folua/
  syntax/
    terms.py
    formulas.py
    signatures.py
  finite/
    structures.py
    algebras.py
    relations.py
  universal_algebra/
    congruences.py
    subalgebras.py
    homomorphisms.py
    term_functions.py
  definability/
    qf.py
    pp.py
    synthesis.py
    preservation.py
  solvers/
    z3.py
    tptp.py
    smtlib.py
  viz/
    hasse.py
    graphviz.py
```

## Mi “killer feature”

La función principal sería esta:

```python
explain_definability(A, R, fragment="qf")
```

Y que devuelva:

```text
La relación R es definible sin cuantificadores.

Una fórmula mínima es:

    (f(x,y) = x) ∧ (g(y) = x)

Además, no existe una fórmula equivalente con profundidad de términos menor que 2.
```

O, si falla:

```text
R no es definible en el fragmento cuantificador-libre.

Obstrucción:
las tuplas (a,b) y (c,d) no pueden ser separadas por ninguna fórmula
cuantificador-libre de esta signatura.

Testigo:
toda función término toma los mismos valores relevantes sobre ambas tuplas.
```

Eso la haría realmente útil para investigación, no solamente para jugar con fórmulas.

## Nombre tentativo

Le pondría algo como:

```text
folua
```

por **First-Order Logic for Universal Algebra**.

O más lindo:

```text
TermForge
```

pero `folua` sería más honesto y académico.

## Véase también

* TPTP y formatos para demostración automática.
* SMT-LIB y backends SMT.
* Z3 para razonamiento automatizado con cuantificadores.
* Universal Algebra Calculator.
* Definibilidad cuantificador-libre.
* Polimorfismos y clones.
* Reticulados de congruencias.
* CEGIS para síntesis de fórmulas.

[1]: https://tptp.org/UserDocs/TPTPLanguage/TPTPLanguage.shtml?utm_source=chatgpt.com "TPTP Language"
[2]: https://smt-lib.org/?utm_source=chatgpt.com "SMT-LIB The Satisfiability Modulo Theories Library"
[3]: https://microsoft.github.io/z3guide/docs/logic/Quantifiers/?utm_source=chatgpt.com "Quantifiers | Online Z3 Guide"

## Estado de implementación (fase visión doc 01)

- [x] §1 Núcleo FO lite many-sorted, alpha, CNF/DNF, TPTP/SMT, API `Vars`/`Function`/`Relation`
- [x] §2 `FiniteAlgebra`, producto, subálgebras, homomorfismos, cociente, clon acotado
- [x] §3 Model checking FO simbólico, eval cache, bitsets opcionales
- [x] §4 Definibilidad qf/pp/ep/horn/fo con kernels k-types + HIT
- [x] §5 Síntesis enumeración, CEGIS, SMT stub
- [x] §6 `to_z3`, Z3 auxiliar
- [x] §7 Builders Group/Ring/…, Maltsev/majority acotados
- [x] §8 `Variety` (álgebra libre finita: stub documentado)
- [x] §9 Hasse SVG + Mermaid/TikZ/HTML export
- [x] §10 Notebook `show_tables`, `draw_*`, explain pretty
- [x] §11 Hash-cons, plugins registry, ADRs 007–010
- [x] Killer feature `explain_definability` multi-fragmento

