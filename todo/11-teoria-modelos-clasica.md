# Teoria Modelos Clasica

> **Prioridad:** ver [README.md](README.md)  
> **Resumen:** Teorías, subestructuras elementales, ultraproductos, tipos, saturación, estabilidad, forking.

> **Origen:** líneas 4248–4747 de `todo.md`

<!-- segment-header-end -->
Sí. En **teoría de modelos general** hay muchísimas cosas agregables, y varias son muy naturales para una librería Python. Cambia el foco: ya no es tanto “estructuras finitas y complejidad”, sino **clases elementales, tipos, saturación, ultraproductos, estabilidad y clasificación de teorías**. Chang–Keisler, por ejemplo, organiza buena parte de la teoría clásica alrededor de métodos de construcción de modelos: constantes, cadenas elementales, funciones de Skolem, indiscernibles, ultraproductos y modelos especiales. ([Google Books][1])

## 1. Teorías como objetos de primer nivel

No solo estructuras y fórmulas:

```python
T = Theory(
    language=L,
    axioms=[
        forall(x, x + 0 == x),
        forall(x, y, x + y == y + x),
    ]
)

T.is_complete()
T.is_consistent()
T.has_model(cardinality="countable")
T.models()
```

Operaciones:

```python
T.complete_diagram(M)
T.elementary_diagram(M)
T.skolemize()
T.morleyize()
T.expand_by_definitions()
```

Esto permitiría trabajar con teorías, no solo con modelos concretos.

## 2. Subestructuras elementales y embeddings elementales

Para teoría general esto es básico:

```python
M.is_elementary_substructure_of(N)
f.is_elementary_embedding()
M.elementary_extension()
```

Y variantes:

```python
M.substructure_generated_by(A)
M.elementary_submodel_containing(A, size="countable")
```

Esto conecta con Löwenheim–Skolem, cadenas elementales y construcción de modelos.

## 3. Ultraproductos y ultrapoderes

Fundamental:

```python
U = Ultrafilter(I)
P = ultraproduct(models=[M_i], ultrafilter=U)
P.satisfies(phi)
```

Con versión especial:

```python
M_star = ultrapower(M, ultrafilter=U)
```

Esto serviría para:

* compacidad;
* saturación;
* equivalencia elemental;
* no estándar;
* transferencia de Łoś;
* construcción de modelos grandes.

Chang–Keisler trata ultraproductos como uno de los métodos básicos de construcción de modelos, y Hodges también enfatiza métodos de construcción y definibilidad. ([Google Books][1])

## 4. Tipos completos y espacios de Stone

Esto faltaba muchísimo.

```python
p = Type(vars=[x], over=A)
p.add(phi(x, a))
p.is_consistent_with(T)
p.is_complete()
```

Y espacios:

```python
S1 = StoneSpace(T, variables=[x])
S1.types()
S1.is_isolated(p)
S1.basic_open(phi)
```

Operaciones útiles:

```python
T.realizes_type(p, in_model=M)
T.omits_type(p)
T.isolate_type(p)
```

Esto es el corazón de mucha teoría de modelos clásica.

## 5. Saturación y homogeneidad

Una librería seria debería poder decir:

```python
M.is_saturated(kappa)
M.is_homogeneous(kappa)
M.realizes_all_types_over(size="<kappa")
```

Y construir aproximaciones:

```python
build_saturated_model(T, cardinality=kappa)
build_homogeneous_model(T)
```

Aunque en general esto no sea computable de manera efectiva, sí puede ser representado simbólicamente, con verificadores para casos concretos.

## 6. Modelos primos, atómicos y universales

Agregar:

```python
T.has_prime_model()
M.is_prime_model_of(T)
M.is_atomic()
M.is_universal_for(cardinality=kappa)
```

Y:

```python
T.countable_models()
T.is_omega_categorical()
T.is_categorical_in(kappa)
```

Esto conecta con clasificación de teorías y categoricidad.

## 7. Eliminación de cuantificadores

Muy útil y bastante implementable en teorías conocidas:

```python
T.has_quantifier_elimination()
T.eliminate_quantifiers(phi)
```

Ejemplos de teorías con procedimientos especiales:

```python
ACF.eliminate_quantifiers(phi)
RCF.eliminate_quantifiers(phi)
DLO.eliminate_quantifiers(phi)
```

También:

```python
T.has_model_completion()
T.model_completion()
T.has_model_companion()
```

Esto sería muy fuerte para álgebra, geometría y estructuras ordenadas.

## 8. Clausura algebraica y definible

Operadores esenciales:

```python
M.definable_closure(A)
M.algebraic_closure(A)
M.interdefinable(a, b, over=A)
```

Y chequeos:

```python
a in dcl(A)
a in acl(A)
```

En álgebra universal esto se puede comparar con subálgebra generada; en teoría de modelos general aparecen fenómenos más finos.

## 9. Imaginarios y eliminación de imaginarios

Esto es muy importante en teoría moderna:

```python
T.eq()                       # expansión M^eq
T.has_elimination_of_imaginaries()
T.eliminate_imaginary(e)
```

Permite tratar cocientes definibles como elementos legítimos.

Ejemplo conceptual:

```python
E = definable_equivalence_relation(x, y)
quot = M.imaginary_sort(E)
```

Muy útil para grupos definibles, geometría y estabilidad.

## 10. Indiscernibles

Otro módulo clásico:

```python
seq = IndiscernibleSequence(M, index_order=Q)
seq.is_indiscernible_over(A)
```

Y construcción:

```python
EMModel(template, linear_order=I)
```

Chang–Keisler menciona indiscernibles entre los métodos básicos de construcción de modelos. ([Google Books][1])

## 11. Estabilidad

Acá empieza la teoría de clasificación.

```python
T.is_stable()
T.is_superstable()
T.is_totally_transcendental()
T.has_order_property()
T.has_independence_property()
```

Y rangos:

```python
T.morley_rank(definable_set)
T.u_rank(type_)
T.su_rank(type_)
```

Hodges introduce estabilidad como tema avanzado, y Tent–Ziegler pasa de nociones estándar a temas como estabilidad, simplicidad y construcciones de Hrushovski. ([Google Books][2])

## 12. Forking, dividing e independencia

Esto sería central:

```python
forks(phi, over=A)
divides(phi, over=A)

a.independent_from(b, over=A)
```

Con notación:

```python
independent(a, b, over=A, theory=T)
```

Y propiedades:

```python
T.forking_calculus()
T.independence_theorem()
```

En teorías estables, esto se comporta como una noción geométrica de independencia.

## 13. Simplicidad, NIP, NTP₂, NSOP₁

Más moderno:

```python
T.is_simple()
T.is_NIP()
T.is_NTP2()
T.is_NSOP1()
T.is_o_minimal()
T.is_weakly_o_minimal()
```

Con testigos negativos:

```python
T.find_order_property()
T.find_independence_property()
T.find_tree_property()
```

Esto permitiría clasificar teorías según las grandes líneas modernas.

## 14. Geometría pregeométrica

En teorías estables, `acl` puede inducir una geometría:

```python
G = Geometry.from_acl(T)
G.is_pregeometry()
G.dimension(tuple_, over=A)
G.is_modular()
G.is_locally_modular()
```

Esto conecta con geometría algebraica modelo-teórica.

## 15. Grupos, campos y anillos definibles

Módulo muy útil:

```python
G = DefinableGroup(M, operation=...)
G.connected_component()
G.generic_types()
G.stabilizer(type_)
```

Y:

```python
K = DefinableField(...)
R = DefinableRing(...)
```

Marker enfatiza aplicaciones de teoría de modelos al álgebra y al análisis de estructuras matemáticas clásicas. ([Google Books][3])

## 16. Interpretabilidad y bi-interpretabilidad

Ya lo habíamos nombrado, pero en teoría general merece módulo propio:

```python
I = Interpretation(T_source, T_target)
I.verify()
T1.is_interpretable_in(T2)
T1.is_biinterpretable_with(T2)
```

Y:

```python
T.definitional_equivalent_to(S)
```

Esto permite comparar teorías, no solo estructuras.

## 17. Omisión de tipos

Módulo clásico:

```python
T.omits_type(p)
T.has_model_omitting(types=[p, q])
```

Y:

```python
OmittingTypesTheorem.apply(T, types)
```

Chang–Keisler lista omisión de tipos entre los refinamientos de métodos de construcción de modelos. ([katalog.ub.rwth-aachen.de][4])

## 18. Compacidad, completitud e interpolación

Como herramientas internas:

```python
T.finitely_satisfiable()
T.compactness_argument()
T.interpolate(phi, psi)
```

Y:

```python
craig_interpolant(phi, psi)
beth_definability(T, relation=R)
```

Esto conecta muy bien con definibilidad.

## 19. Diagramas y métodos de construcción

Agregar:

```python
Diagram(M)
ElementaryDiagram(M)
AtomicDiagram(M)
```

Y construir modelos:

```python
ModelBuilder.from_diagram(D)
ModelBuilder.by_constants(T)
ModelBuilder.by_elementary_chain(chain)
```

Esto da una capa clásica de construcción simbólica.

## 20. Modelos no estándar

Especialmente para aritmética y análisis:

```python
Nstar = nonstandard_model(PA)
Rstar = ultrapower(RealField)
```

Operaciones:

```python
x.is_infinitesimal()
x.is_infinite()
standard_part(x)
```

No sería central para álgebra universal, pero sí muy representativo de teoría de modelos general.

---

La arquitectura quedaría así:

```text
finite_model_theory/
  FO, MSO, Datalog, LFP, juegos, complejidad descriptiva

universal_algebra/
  términos, congruencias, HSP, clones, CSP, definibilidad

general_model_theory/
  teorías, tipos, saturación, ultraproductos, estabilidad,
  independencia, eliminación de cuantificadores, interpretabilidad
```

El agregado más importante sería este:

```python
T = Theory(...)
M = Model(T)

S = StoneSpace(T, [x])
p = S.generic_type()

T.is_stable()
M.is_saturated(kappa)
a.independent_from(b, over=A)
T.eliminate_quantifiers(phi)
```

Eso transforma la librería de “lógica sobre estructuras finitas” en una plataforma más general de teoría de modelos.

## Qué sería realmente publicable

No intentaría implementar “toda la teoría de modelos”. Elegiría un núcleo novedoso:

> **una librería que unifique teoría de modelos finitos, álgebra universal computacional y teoría de modelos clásica efectiva mediante tipos, definibilidad, interpretabilidad y certificados.**

Lo más original podría ser el puente:

```text
definibilidad finita
+ tipos clásicos
+ álgebra universal
+ interpretabilidad
+ certificados computacionales
```

Eso sí sería una identidad interesante.

## Véase también

* Chang–Keisler, *Model Theory*.
* Wilfrid Hodges, *Model Theory*.
* David Marker, *Model Theory: An Introduction*.
* Katrin Tent y Martin Ziegler, *A Course in Model Theory*.
* Tipos completos.
* Saturación.
* Ultraproductos.
* Eliminación de cuantificadores.
* Estabilidad.
* Forking e independencia.

[1]: https://books.google.com/books/about/Model_Theory.html?id=sRi0AAAAQBAJ&utm_source=chatgpt.com "Model Theory: Third Edition - C.C. Chang, H. Jerome Keisler"
[2]: https://books.google.com/books/about/Model_Theory.html?hl=es&id=Rf6GWut4D30C&utm_source=chatgpt.com "Model Theory - Wilfrid Hodges - Google Libros"
[3]: https://books.google.com/books/about/Model_Theory_An_Introduction.html?id=gkvogoiEnuYC&utm_source=chatgpt.com "Model Theory : An Introduction - David Marker"
[4]: https://katalog.ub.rwth-aachen.de/discovery/fulldisplay?context=L&docid=alma991026350812606448&vid=49HBZ_UBA%3AVU1&utm_source=chatgpt.com "Model theory / / C.C. Chang, H.J. Keisler. - RWTH Aachen"
