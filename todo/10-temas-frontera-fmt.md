# Temas Frontera Fmt

> **Prioridad:** ver [README.md](README.md)  
> **Resumen:** Oráculos, SNP/MMSNP, chase, guarded logic, CFI, Weisfeiler–Leman, canonización, unificación de tres mundos.

> **Origen:** líneas 3379–3828 de `todo.md`

<!-- segment-header-end -->
## 1. Oráculos y relativización

Faltaría permitir lógicas con predicados-oráculo:

```python
Oracle("Reachability")
FO.with_oracle("Reachability")
```

Para estudiar frases del estilo:

```text
FO + oracle para problema P
```

Esto es útil para complejidad descriptiva relativizada: ver qué pasa si a la lógica le das acceso a una relación externa.

## 2. Clases tipo SNP / MMSNP

Además de ESO completo, agregaría fragmentos de segundo orden más finos:

```python
Logic("SNP")
Logic("MonadicSNP")
Logic("MMSNP")
```

Estos fragmentos son muy importantes porque se conectan con CSP, homomorfismos, problemas NP relacionales y bases de datos.

Ejemplo:

```python
Problem("graph_3_colorability").to_mmsnp()
```

Esto sería muy natural para unir **finite model theory + CSP algebraico**.

## 3. Chase de bases de datos

No lo habíamos metido explícitamente.

```python
Chase(instance, dependencies).run()
```

Con dependencias:

```python
TupleGeneratingDependency(...)
EqualityGeneratingDependency(...)
InclusionDependency(...)
FunctionalDependency(...)
```

Esto sirve para:

* bases de datos;
* contención de consultas;
* dependencias relacionales;
* Datalog±;
* homomorfismos;
* CSP.

Sería una rama muy útil si querés que la librería hable también el idioma de teoría de bases de datos.

## 4. Dependencias y restricciones relacionales

API posible:

```python
schema = Schema(...)
schema.add_functional_dependency(...)
schema.add_inclusion_dependency(...)
schema.add_tgd(...)
schema.add_egd(...)
```

Y luego:

```python
schema.satisfies(instance)
schema.chase(instance)
schema.query_containment(Q1, Q2)
```

Esto conecta primer orden con bases de datos finitas de manera bastante directa.

## 5. Lógicas guarded

Faltaba desarrollarlo más:

```python
Logic("GuardedFO")
Logic("GuardedNegationFO")
Logic("CliqueGuardedFO")
```

Son fragmentos importantes porque tienen mejor comportamiento decidible y están cerca de bases de datos, grafos, teoría modal y estructuras relacionales dispersas.

## 6. Lógica modal como fragmento finito

Una capa linda:

```python
ModalFormula(...)
KripkeStructure(...)
modal_to_fo(phi)
```

Y juegos bisimulacionales:

```python
BisimulationGame(A, a, B, b)
```

Esto agregaría:

* bisimulación;
* lógica modal;
* traducción estándar a FO;
* invariancia por bisimulación;
* profundidad modal mínima.

No es álgebra universal clásica, pero sí es finito-model-teórico.

## 7. Invariancia como mecanismo general

Más general que orden-invariancia:

```python
phi.is_invariant_under("isomorphism")
phi.is_invariant_under("automorphisms")
phi.is_invariant_under("bisimulation")
phi.is_invariant_under("homomorphisms")
phi.is_invariant_under("generated_substructures")
```

Esto permite decir:

```text
Esta fórmula usa más estructura auxiliar de la que realmente define.
```

Y sirve para explicar teoremas de caracterización: “las propiedades FO invariantes bajo X corresponden a tal fragmento”.

## 8. Teoremas de preservación finita como pruebas asistidas

No solo testear preservación, sino usarla como criterio:

```python
Preservation.homomorphism(phi, finite=True)
Preservation.extension(phi, finite=True)
Preservation.substructure(phi, finite=True)
```

En estructuras finitas estos teoremas son más delicados que en teoría de modelos clásica; una librería útil debería distinguir claramente:

```text
válido en estructuras arbitrarias
válido en estructuras finitas
falso en estructuras finitas
abierto / no implementado
```

## 9. CFI graphs y límites de conteo

Metería ejemplos canónicos tipo **Cai–Fürer–Immerman**:

```python
CFIGraph(base_graph, parity=0)
CFIGraph(base_graph, parity=1)
```

Sirven para mostrar límites de lógicas con pocas variables y conteo, y están muy conectados con Weisfeiler–Leman, isomorfismo de grafos y `IFP+C`.

API:

```python
A.indistinguishable_from(B, logic="C^k")
```

Esto sería excelente para inexpresabilidad computacional.

## 10. Weisfeiler–Leman como herramienta nativa

Muy importante:

```python
WL.color_refinement(G, k=1)
WL.k_dimensional(G, k=3)
```

Y conexión lógica:

```python
G.equivalent_to(H, logic="C^k")
```

Esto une:

* lógica con conteo;
* juegos de pebble con conteo;
* isomorfismo de grafos;
* expresividad finita;
* aprendizaje sobre grafos.

## 11. Rank logic y solvability logic

Esto es más moderno, pero entraría en una librería ambiciosa:

```python
Logic("FPRank")
Logic("FPSolve")
```

Con operadores sobre rangos de matrices finitas:

```python
Rank_p(matrix_definable_relation, p=2)
```

Son lógicas creadas para superar limitaciones de `IFP+C` en estructuras finitas.

## 12. Choiceless Polynomial Time

Otra capa avanzada:

```python
Logic("CPT")
```

No necesariamente implementable de entrada, pero sí como objeto teórico para comparar con `PTIME`, `IFP+C`, orden, conteo, etc.

Esto toca una cuestión profunda: cómo capturar `PTIME` sin imponer un orden arbitrario.

## 13. Canonización lógica

Para conectar con orden-invariancia e isomorfismo:

```python
canonical_order = A.definable_canonization(logic="IFP+C")
```

O:

```python
A.has_definable_order(logic="FO")
```

Esto permite estudiar cuándo una estructura puede ordenarse de manera canónica usando cierta lógica.

## 14. Lógicas sobre grafos dispersos

Módulos para clases restringidas:

```python
Graphs.bounded_degree(d)
Graphs.nowhere_dense()
Graphs.bounded_expansion()
```

Y model checking:

```python
FOModelChecker.on_sparse_class(...)
```

Esto es más moderno que Ebbinghaus–Flum, pero muy relevante para teoría de modelos finitos algorítmica.

## 15. Meta-resultados como objetos

Una idea fuerte: representar teoremas conocidos como objetos consultables.

```python
Theorem("Fagin").statement()
Theorem("Immerman-Vardi").conditions()
Theorem("Trakhtenbrot").consequence()
```

Ejemplo:

```python
Logic("ESO").captures("NP")
```

Y que la librería diga:

```text
Esto vale sobre estructuras finitas, sin requerir orden incorporado.
```

Sería una mezcla de librería y enciclopedia computacional rigurosa.

## 16. Asistente de separación lógica

Una función muy útil:

```python
separate_property(
    property="connectivity",
    not_in="FO",
    method=["locality", "EF", "compactness_failure"]
)
```

Salida:

```text
La conectividad no es FO-definible sobre grafos finitos.
Método sugerido: localidad de Gaifman o juego de Ehrenfeucht–Fraïssé.
```

No solo calcula; sugiere método de prueba.

## 17. Biblioteca de propiedades clásicas

Incluir propiedades ya formalizadas:

```python
GraphProperties.connected()
GraphProperties.acyclic()
GraphProperties.bipartite()
GraphProperties.has_even_cardinality()
GraphProperties.has_hamiltonian_cycle()
GraphProperties.k_colorable(k)
```

Y para cada una:

```python
P.known_definability()
P.known_complexity()
P.example_formula(logic="ESO")
P.inexpressibility_certificate(logic="FO")
```

Esto haría la librería muy didáctica y útil para investigación.

## 18. Comparación experimental de lógicas

Algo como:

```python
LogicExperiment(
    property=P,
    logics=["FO", "FO+C", "FO+TC", "LFP", "ESO"],
    structures=Graphs.up_to_size(7)
).run()
```

Que produzca una tabla:

```text
FO: no encontrada / obstrucción EF
FO+C: no encontrada
FO+TC: sí
LFP: sí
ESO: sí
```

## 19. Inferencia de lógica mínima

Muy atractiva:

```python
infer_minimal_logic(property=P, examples=dataset)
```

Salida:

```text
La propiedad parece requerir TC.
FO no alcanza hasta rango 6.
FO+C tampoco separa los ejemplos CFI dados.
```

Esto no prueba todo, pero ayuda a descubrir.

## 20. Unificación de tres mundos

La arquitectura final debería tener tres “tipos de objetos” de primer nivel:

```python
Structure
Formula
Problem
```

Y que todos conversen:

```python
Problem.to_formula(logic)
Formula.model_check(Structure)
Structure.generate_counterexample(Problem)
Problem.known_complexity()
Formula.expressive_resources()
```

Ese diseño sería más potente que una librería de fórmulas.

---

A esta altura, mi resumen sería:

```text
Lo que todavía faltaba:
oráculos,
SNP/MMSNP,
chase,
dependencias de bases de datos,
guarded fragments,
lógica modal,
CFI graphs,
Weisfeiler–Leman,
rank logic,
canonización,
CPT,
grafos dispersos,
biblioteca de propiedades clásicas,
asistente de separación lógica.
```

La versión verdaderamente ambiciosa no sería:

> “una librería Python de lógica de primer orden”.

Sería:

> **un laboratorio computacional de expresividad finita**, con un submódulo fuerte de álgebra universal finita.

Eso sí tendría una identidad tremenda.

## Véase también

* MMSNP.
* Chase.
* Guarded fragment.
* Cai–Fürer–Immerman.
* Weisfeiler–Leman.
* Lógica con rango.
* Choiceless Polynomial Time.
* Canonización lógica.
* Grafos nowhere dense.
* Preservación finita.

[1]: https://link.springer.com/book/10.1007/3-540-28788-4?utm_source=chatgpt.com "Finite Model Theory: Second Edition | Springer Nature Link"




