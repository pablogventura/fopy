# Nucleo Confiable Y Certificados Negativos

> **Prioridad:** ver [README.md](README.md)  
> **Resumen:** Kernel confiable vs capa experimental; certificados negativos estandarizados.

> **Origen:** líneas 3829–3890 de `todo.md`

<!-- segment-header-end -->
Sí, pero ya no agregaría “más temas” sin control. Agregaría **capas transversales** que hacen que todo lo anterior sea usable, verificable y publicable.

## 1. Un núcleo pequeño y confiable

Separaría:

```text
kernel confiable:
  sintaxis, sustitución, evaluación, certificados, verificación

capa experimental:
  heurísticas, SAT, Z3, Mace4, búsqueda, aprendizaje
```

La idea: que todo resultado difícil termine en un certificado que pueda verificar un núcleo simple.

Ejemplo:

```python
result = Definability.check(A, R, fragment="pp")
cert = result.certificate()

TrustedKernel.verify(cert)
```

Esto es clave para no depender ciegamente de heurísticas.

## 2. Certificados negativos estandarizados

Los certificados positivos son fáciles: una fórmula que define algo. Los negativos son lo interesante.

Tipos de certificado:

```text
no FO-definible:
  estrategia ganadora de Duplicador en juego EF

no FO[k]-definible:
  estrategia en pebble game

no C[k]-definible:
  estrategia en counting pebble game

no PP-definible:
  polimorfismo que no preserva la relación

no QF-definible:
  dos tuplas con el mismo tipo atómico/término
```

Eso haría que la librería no diga solamente:

```text
False
```

sino:

```text
False, y acá está la razón matemática verificable.
```

