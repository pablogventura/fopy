# Roadmap fopy — priorizado

Índice derivado de [`todo.md`](../todo.md), reorganizado de **más a menos importante** para implementar.

## Triángulo central

> **Álgebra universal finita + definibilidad + contraejemplos certificados**

## Niveles de madurez

| Nivel | Objetivo |
|-------|----------|
| **1 — útil** | FOL, estructuras finitas, evaluación, congruencias, subálgebras, homomorfismos, definibilidad, síntesis |
| **2 — publicable** | certificados, finite model finding, isomorfismo, benchmarks, interoperabilidad UACalc/GAP/Mace4/TPTP/SMT-LIB |
| **3 — investigación** | clones, CSP, TCT, dualidades, HSP, reescritura, asistentes de prueba, experimentos reproducibles |

## Lista de 20 imprescindibles

Detalle en [`03-publicabilidad-e-imprescindibles.md`](03-publicabilidad-e-imprescindibles.md).

1. sintaxis FOL robusta · 2. estructuras finitas many-sorted · 3. evaluación eficiente · 4. funciones término · 5. subálgebras/congruencias/homomorfismos · 6. reticulados · 7. definibilidad por fragmentos · 8. síntesis mínima · 9. testigos no-definibilidad · 10. finite model finding · 11. contraejemplos · 12. isomorfismo · 13. HSP · 14. términos Maltsev/Taylor/Siggers · 15. clones · 16. CSP · 17. reescritura · 18. certificados · 19. interoperabilidad · 20. benchmarks

## Archivos por prioridad

| # | Archivo | Contenido |
|---|---------|-----------|
| 01 | [01-vision-y-killer-feature.md](01-vision-y-killer-feature.md) | Visión inicial y killer feature (l.1–403, 403 líneas) |
| 02 | [02-nucleo-confiable-y-certificados-negativos.md](02-nucleo-confiable-y-certificados-negativos.md) | Kernel confiable y certificados negativos (l.3829–3890, 62 líneas) |
| 03 | [03-publicabilidad-e-imprescindibles.md](03-publicabilidad-e-imprescindibles.md) | Publicabilidad e imprescindibles (l.404–862, 459 líneas) |
| 04 | [04-tercera-capa-y-niveles.md](04-tercera-capa-y-niveles.md) | Tercera capa y niveles 1–3 (l.863–1338, 476 líneas) |
| 05 | [05-capas-transversales-resto.md](05-capas-transversales-resto.md) | Capas transversales (IR, benchmarks, experimentos) (l.3891–4247, 357 líneas) |
| 06 | [06-plataforma-meta-investigacion.md](06-plataforma-meta-investigacion.md) | Plataforma meta-investigación (l.1339–1823, 485 líneas) |
| 07 | [07-teoria-modelos-finitos-ebbinghaus-flum.md](07-teoria-modelos-finitos-ebbinghaus-flum.md) | Teoría de modelos finitos (Ebbinghaus–Flum) (l.1824–2225, 402 líneas) |
| 08 | [08-herramientas-fmt-tecnicas.md](08-herramientas-fmt-tecnicas.md) | Herramientas FMT técnicas (l.2226–2717, 492 líneas) |
| 09 | [09-complejidad-descriptiva-profunda.md](09-complejidad-descriptiva-profunda.md) | Complejidad descriptiva profunda (l.2718–3378, 661 líneas) |
| 10 | [10-temas-frontera-fmt.md](10-temas-frontera-fmt.md) | Temas frontera FMT (l.3379–3828, 450 líneas) |
| 11 | [11-teoria-modelos-clasica.md](11-teoria-modelos-clasica.md) | Teoría de modelos clásica (l.4248–4747, 500 líneas) |

## Cobertura

- Líneas en `todo.md`: **4747**
- Líneas en `todo/`: **4747** (100%)

## Estado actual del repo

Parcialmente implementado: sintaxis FOL, estructuras, evaluación finita, definibilidad (HIT/splitting), parse `.model`, Hasse/draw, builders, printing LaTeX. Ver [`AGENTS.md`](../AGENTS.md).
