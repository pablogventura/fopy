# Plataforma Meta Investigacion

> **Prioridad:** ver [README.md](README.md)  
> **Resumen:** Atlas de álgebras, identificadores canónicos, smallest example, separación de propiedades, refutador de conjeturas.

> **Origen:** líneas 1339–1823 de `todo.md`

<!-- segment-header-end -->
Más cosas, pero ya entramos en una capa **meta-matemática y de ingeniería científica**. No son módulos “normales”, sino cosas que harían que la librería sea una **plataforma de investigación**.

## 1. Un “Atlas de álgebras finitas”

No solo cargar ejemplos: construir una base navegable.

```python
Atlas.search(
    size=5,
    signature="binary_idempotent",
    properties=["congruence_permutable", "not_distributive"]
)
```

Con páginas automáticas para cada álgebra:

```text
A_5_142
universo: 5
operaciones: 2 binarias
congruencias: 4
subálgebras: 7
automorfismos: 2
término de Maltsev: sí
término de mayoría: no
clones parciales: ...
```

Sería una especie de **LMFDB para álgebras universales finitas**. LMFDB no es de álgebra universal: es una base de objetos de teoría de números y geometría aritmética, pero sirve como modelo cultural de “atlas matemático computacional”. ([lmfdb.org][1])

## 2. Identificadores canónicos

Cada álgebra debería tener un identificador estable:

```python
A.canonical_id()
```

Algo como:

```text
ua:bin2-idem:n5:sha256:9f3a...
```

Y también:

```python
A.canonical_label()
A.isomorphic_hash()
A.canonical_tables()
```

Esto permitiría citar una estructura en un paper sin pegar diez tablas gigantes.

## 3. Motor de “smallest example”

Una función central:

```python
smallest_example(
    satisfies=[P, Q],
    refutes=[R],
    sizes=range(2, 10)
)
```

Ejemplo:

```python
smallest_example(
    satisfies=["malcev_term"],
    refutes=["majority_term"],
    signature="one_binary_operation"
)
```

Esto es muy útil porque muchos resultados computacionales se formulan así:

> “El menor ejemplo que satisface X pero no Y tiene tamaño n.”

## 4. Motor de “separación de propiedades”

Esto sería tremendo:

```python
separate(P, Q, max_size=8)
```

Salida:

```text
P no implica Q.
Contraejemplo mínimo: tamaño 4.
```

Y si no encuentra:

```text
No se encontró contraejemplo hasta tamaño 8.
Posible conjetura: P ⇒ Q.
```

Aplicable a:

* congruence distributive;
* congruence modular;
* congruence permutable;
* Taylor;
* Siggers;
* Maltsev;
* majority;
* Jónsson;
* Day;
* near-unanimity;
* semidistributividad;
* residual smallness;
* primalidad;
* discriminator terms.

## 5. Búsqueda de axiomatizaciones pequeñas

No solo verificar axiomas, sino buscar bases:

```python
find_equational_basis(class_examples, max_depth=4)
```

O:

```python
minimize_axioms(axioms, models_up_to_size=6)
```

Salida:

```text
El axioma 3 es independiente de los demás.
Contraejemplo de tamaño 5.
```

Eso sería muy útil para álgebra universal experimental.

## 6. “Refutador de conjeturas”

Un objeto explícito:

```python
Conjecture(
    assumptions=[...],
    conclusion=...
).refute(max_size=7)
```

Y que devuelva:

* contraejemplo mínimo;
* por qué satisface las hipótesis;
* valuación que viola la conclusión;
* tablas mínimas;
* diagrama;
* archivo reproducible.

## 7. Minería de identidades

Dada un álgebra finita:

```python
A.mine_identities(max_depth=5, variables=3)
```

Que descubra cosas como:

```text
f(x,x) = x
f(x,f(y,x)) = f(x,y)
t(x,y,y) = t(y,x,y)
```

Y clasifique:

* identidades triviales;
* identidades independientes;
* identidades características;
* identidades que separan esta álgebra de otras.

## 8. Diferencia semántica entre dos álgebras

Algo así:

```python
A.distinguish_from(B, fragment="equational", max_depth=4)
```

Salida:

```text
La identidad más chica que vale en A y falla en B es:
    f(x, f(y,z)) = f(f(x,y), z)
```

O para lógica de primer orden:

```python
A.fo_distinguish(B, quantifier_rank=3)
```

Esto sería muy útil para clasificación.

## 9. Juegos de Ehrenfeucht–Fraïssé finitos

Para estructuras finitas:

```python
EFGame(A, B, rounds=3).winner()
```

Y más algebraico:

```python
A.fo_equivalent_to(B, quantifier_rank=3)
```

Esto ayudaría a explicar cuándo dos estructuras no se distinguen con fórmulas chicas.

## 10. Complejidad descriptiva finita

Agregar mediciones como:

```python
FormulaComplexity.minimal_definition(A, R)
```

Con parámetros:

* tamaño de fórmula;
* profundidad de términos;
* rango cuantificacional;
* cantidad de variables;
* alternancia de cuantificadores;
* fragmento lógico mínimo.

Ejemplo:

```text
R es definible con 3 variables, pero no con 2.
R es definible existencial-positivamente, pero no primitivamente-positivamente.
```

Esto conecta definibilidad con una noción fina de complejidad lógica.

## 11. Modo “solo variables finitas”

Para muchos problemas, el cuello de botella no es la fórmula sino el número de variables. Pondría:

```python
A.definability_with_k_variables(R, k=2)
```

Fragmentos:

```python
FO2
FO3
QF2
PP2
EP2
```

Esto puede generar resultados publicables: “tal relación requiere 3 variables”.

## 12. Reducción automática a SAT

No solo usar Z3. También codificar internamente:

```python
encode_to_sat(problem)
```

Problemas:

* existencia de operación con identidades dadas;
* existencia de término especial;
* existencia de homomorfismo;
* isomorfismo;
* búsqueda de modelo finito;
* búsqueda de fórmula;
* minimalidad.

Alloy va en una dirección parecida: traduce modelos relacionales a SAT y usa Kodkod/Pardinus como motor interno. ([alloytools.org][2])

## 13. Búsqueda con aprendizaje

No necesariamente “IA generativa”, sino heurísticas aprendidas:

```python
search(strategy="learned")
```

Para aprender:

* qué términos conviene probar primero;
* qué ramas de búsqueda podar;
* qué invariantes predicen una propiedad;
* qué estructuras son candidatas a contraejemplo.

Esto puede ser muy potente en enumeraciones grandes.

## 14. Sistema de “oráculos intercambiables”

Un mismo problema podría resolverse por varios motores:

```python
result = Problem(...).solve_with(["bruteforce", "sat", "z3", "mace4", "uacalc"])
```

Y comparar:

```python
result.cross_validate()
```

Esto aumenta confianza: si dos motores independientes dan lo mismo, el resultado es más creíble.

## 15. Análisis de sensibilidad de signatura

Dada una estructura con muchas operaciones:

```python
A.signature_sensitivity(property="qf_defines_R")
```

Que diga:

```text
La operación g es irrelevante.
La operación f es esencial.
Con {f,h} alcanza para definir R.
Con {f} no alcanza.
```

Esto es muy útil para encontrar la **signatura mínima** de un fenómeno.

## 16. Compresión de tablas

Para publicar álgebras, las tablas son horribles. Agregaría:

```python
A.compress()
```

Representaciones:

* por generadores;
* por términos;
* por reglas;
* por simetrías;
* por descomposición subdirecta;
* por producto/cociente;
* por permutaciones;
* por tablas parciales más closure.

## 17. Reconstrucción desde invariantes

Problema inverso:

```python
find_algebra_with(
    congruence_lattice=L,
    subalgebra_lattice=S,
    size=6
)
```

O más modesto:

```python
find_algebra_with_congruence_lattice(L)
```

Esto toca problemas clásicos de representación de reticulados de congruencias. UACalc ya tiene infraestructura para álgebras finitas, congruencias y reticulados de subálgebras, así que una librería nueva debería aprovechar o interoperar con eso. ([UACalc][3])

## 18. Diagnóstico de “por qué explota”

Cuando una búsqueda tarda demasiado:

```python
search.diagnose()
```

Salida:

```text
El cuello de botella es la enumeración de términos binarios.
Hay 18241 clases semánticas distintas hasta profundidad 4.
La operación f genera muchas funciones nuevas.
Sugerencia: usar quotient por automorfismos.
```

Esto es muy valioso para investigar.

## 19. Perfil probabilístico

Para clases grandes:

```python
random_algebra(signature, size=6, constraints=[...])
```

Y después:

```python
estimate_probability(property="has_malcev_term", samples=10000)
```

No prueba teoremas, pero ayuda a detectar fenómenos raros.

## 20. Módulo de “fenómenos raros”

Buscar estructuras extremales:

```python
find_extreme(
    maximize="number_of_congruences",
    among="idempotent_binary_algebras",
    size=6
)
```

O:

```python
find_rare(
    property="has_siggers_but_no_majority",
    size=5
)
```

Esto puede generar ejemplos interesantes para papers.

---

Mi respuesta más honesta ahora sería:

**La librería ideal no sería solamente una librería de lógica de primer orden. Sería una máquina de experimentación algebraica finita.**

La fórmula conceptual:

```text
sintaxis lógica
+ álgebra universal finita
+ búsqueda de modelos
+ síntesis de definiciones
+ certificados
+ atlas de ejemplos
+ contraejemplos mínimos
+ interoperabilidad
= herramienta publicable
```

La parte más original, para mí, sería:

```text
definibilidad + minimalidad + obstrucciones + contraejemplos certificados
```

Eso tiene más identidad científica que intentar hacer “otro Sage” u “otro UACalc”.

## Véase también

* Atlas computacionales de objetos matemáticos.
* Kodkod y Alloy.
* UACalc.
* Bases finitas de identidades.
* Ehrenfeucht–Fraïssé games.
* Complejidad descriptiva finita.
* SAT para estructuras finitas.
* Representación de reticulados de congruencias.
* Búsqueda de contraejemplos mínimos.

[1]: https://www.lmfdb.org/?utm_source=chatgpt.com "LMFDB - The L-functions and modular forms database"
[2]: https://alloytools.org/documentation.html?utm_source=chatgpt.com "Documentation Alloy 6"
[3]: https://uacalc.org/?utm_source=chatgpt.com "UACalc -- Universal Algeba Calculator"



