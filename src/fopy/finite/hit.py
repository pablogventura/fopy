"""HIT algorithm for open definability."""

from __future__ import annotations

import copy
import math
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import TYPE_CHECKING

from fopy.finite import open_formulas as formulas
from fopy.finite.open_formulas import Formula, OpSym, Term, Variable
from fopy.finite.models import Model
from fopy.finite.relops import Operation, Relation

if TYPE_CHECKING:
    pass


@dataclass
class HitConfig:
    use_information_gain: bool = False
    ig_sample: int | None = 20


@dataclass
class Counterexample:
    tuples: list[list[int]]

    def __repr__(self) -> str:
        return f"Counterexample({self.tuples!r})"


def _entropy(in_count: int, out_count: int) -> float:
    n = in_count + out_count
    if n == 0:
        return 0.0
    p = in_count / n
    q = out_count / n

    def h(x: float) -> float:
        return -x * math.log2(x) if x > 0 else 0.0

    return h(p) + h(q)


def information_gain_from_counts(
    n: int,
    in_total: int,
    partition_counts: dict[tuple[int, bool], tuple[int, int]],
) -> float:
    if n == 0:
        return 0.0
    out_total = n - in_total
    h_before = _entropy(in_total, out_total)
    h_after = 0.0
    for g_in, g_out in partition_counts.values():
        gs = g_in + g_out
        h_after += (gs / n) * _entropy(g_in, g_out)
    return h_before - h_after


def _cartesian_product_indices(
    pool: list[int], n: int, forced: set[int]
) -> list[list[int]]:
    if n == 0:
        return [[]]

    def build(current: list[int]) -> None:
        if len(current) == n:
            if any(i in forced for i in current):
                result.append(list(current))
            return
        for p in pool:
            build(current + [p])

    result: list[list[int]] = []
    build([])
    return result


@dataclass
class TupleHistory:
    t: list[int]
    history: list[int]
    index_map: dict[int, int] = field(default_factory=dict)
    in_target: bool = False
    has_generated: bool = False

    @classmethod
    def new(cls, t: list[int], targets: list[Relation]) -> TupleHistory:
        history = list(t)
        index_map = {x: i for i, x in enumerate(t)}
        in_target = all(
            tg.contains(t) if tg.arity == len(t) else True for tg in targets
        )
        return cls(t=t, history=history, index_map=index_map, in_target=in_target)

    def step(self, op: Operation, ti: list[int]) -> int:
        args = [self.history[i] for i in ti]
        x = op.call(args)
        if x is None:
            raise ValueError(f"Operation {op.sym} undefined for args {args}")
        if x in self.index_map:
            self.has_generated = False
            return self.index_map[x]
        idx = len(self.history)
        self.history.append(x)
        self.index_map[x] = idx
        self.has_generated = True
        return idx

    def simulate_step(self, op: Operation, ti: list[int]) -> tuple[int, bool]:
        args = [self.history[i] for i in ti]
        x = op.call(args)
        if x is None:
            raise ValueError(f"Operation {op.sym} undefined for args {args}")
        if x in self.index_map:
            return self.index_map[x], False
        return len(self.history), True

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TupleHistory):
            return NotImplemented
        return self.t == other.t and self.history == other.history

    def __hash__(self) -> int:
        return hash((tuple(self.t), tuple(self.history)))


class _GenStateKind(Enum):
    INIT = auto()
    ITER = auto()


@dataclass
class _GenState:
    kind: _GenStateKind = _GenStateKind.INIT
    arities: list[int] = field(default_factory=list)
    arity_idx: int = 0
    op_idx: int = 0
    perm_idx: int = 0
    perms: list[list[int]] = field(default_factory=list)


@dataclass
class IndicesTupleGenerator:
    ops: dict[int, list[Operation]]
    arity: int
    viejos: list[int]
    nuevos: list[int]
    sintactico: list[Term] = field(default_factory=list)
    last_term: Term | None = None
    forked: bool = False
    finished: bool = False
    state: _GenState = field(default_factory=_GenState)

    @classmethod
    def new(
        cls,
        ops: dict[int, list[Operation]],
        arity: int,
        viejos: list[int],
        nuevos: list[int],
    ) -> IndicesTupleGenerator:
        sintactico = [Term.variable(Variable.from_index(i)) for i in range(arity + 11)]
        return cls(
            ops=copy.deepcopy(ops),
            arity=arity,
            viejos=list(viejos),
            nuevos=list(nuevos),
            sintactico=sintactico,
        )

    def step(self) -> tuple[Operation, list[int]] | None:
        if self.forked:
            raise RuntimeError("Generator was forked!")
        while True:
            if self.state.kind == _GenStateKind.INIT:
                constants = self.ops.get(0)
                if constants:
                    op = constants[0]
                    self.last_term = Term.op_term(OpSym.new(op.sym, 0), [])
                    self.state = _GenState(
                        kind=_GenStateKind.ITER,
                        arities=[0],
                        arity_idx=0,
                        op_idx=1,
                        perm_idx=0,
                        perms=[[]],
                    )
                    return op, []
                arities = sorted(a for a in self.ops if a > 0)
                if not arities and 0 not in self.ops:
                    self.finished = True
                    return None
                self.state = _GenState(
                    kind=_GenStateKind.ITER,
                    arities=arities,
                    arity_idx=0,
                    op_idx=0,
                    perm_idx=0,
                    perms=[],
                )
                if self.nuevos and arities:
                    pool = self.viejos + self.nuevos
                    forced = set(self.nuevos)
                    perms = _cartesian_product_indices(pool, arities[0], forced)
                    self.state.perms = perms

            elif self.state.kind == _GenStateKind.ITER:
                st = self.state
                arities = st.arities
                if not arities:
                    if not self.nuevos:
                        self.finished = True
                        return None
                    self.viejos.extend(self.nuevos)
                    self.nuevos.clear()
                    self.state = _GenState()
                    continue
                if st.arity_idx >= len(arities):
                    if not self.nuevos:
                        self.finished = True
                        return None
                    self.viejos.extend(self.nuevos)
                    self.nuevos.clear()
                    st.arity_idx = 0
                    pool = self.viejos + self.nuevos
                    forced = set(self.nuevos)
                    st.perms = _cartesian_product_indices(pool, arities[0], forced)
                    continue
                a = arities[st.arity_idx]
                op_list = self.ops.get(a)
                if op_list is None:
                    return None
                if st.op_idx >= len(op_list):
                    st.op_idx = 0
                    st.perm_idx = 0
                    st.arity_idx += 1
                    if st.arity_idx >= len(arities):
                        if not self.nuevos:
                            self.finished = True
                            return None
                        self.viejos.extend(self.nuevos)
                        self.nuevos.clear()
                        st.arity_idx = 0
                    pool = self.viejos + self.nuevos
                    forced = set(self.nuevos)
                    st.perms = _cartesian_product_indices(pool, arities[st.arity_idx], forced)
                    continue
                if st.perm_idx >= len(st.perms):
                    st.op_idx += 1
                    st.perm_idx = 0
                    continue
                op = op_list[st.op_idx]
                ti = st.perms[st.perm_idx]
                st.perm_idx += 1
                args = [self.sintactico[i] for i in ti]
                self.last_term = Term.op_term(OpSym.new(op.sym, op.arity), args)
                return op, ti

    def formula_diferenciadora(self, index: int) -> Formula:
        assert self.last_term is not None
        return formulas.eq(self.last_term, self.sintactico[index])

    def hubo_nuevo(self) -> None:
        if self.forked:
            raise RuntimeError("Generator was forked!")
        new_idx = len(self.viejos) + len(self.nuevos)
        self.nuevos.append(new_idx)
        while len(self.sintactico) <= new_idx:
            self.sintactico.append(
                Term.variable(Variable.from_index(len(self.sintactico)))
            )
        assert self.last_term is not None
        self.sintactico[new_idx] = self.last_term

    def fork(self, quantity: int) -> list[IndicesTupleGenerator]:
        if self.forked:
            raise RuntimeError("Generator was forked!")
        self.forked = True
        return [
            IndicesTupleGenerator(
                ops=copy.deepcopy(self.ops),
                arity=self.arity,
                viejos=list(self.viejos),
                nuevos=list(self.nuevos),
                sintactico=list(self.sintactico),
                last_term=self.last_term,
                forked=False,
                finished=self.finished,
            )
            for _ in range(quantity)
        ]

    def enumerate_candidates(self) -> list[tuple[Operation, list[int]]]:
        gen = copy.deepcopy(self)
        result: list[tuple[Operation, list[int]]] = []
        while True:
            nxt = gen.step()
            if nxt is None:
                break
            result.append(nxt)
        return result

    def take_candidates(self, limit: int) -> list[tuple[Operation, list[int]]]:
        gen = copy.deepcopy(self)
        result: list[tuple[Operation, list[int]]] = []
        for _ in range(limit):
            nxt = gen.step()
            if nxt is None:
                break
            result.append(nxt)
        return result


@dataclass
class Block:
    operations: dict[int, list[Operation]]
    tuples: list[TupleHistory]
    targets: list[Relation]
    formula: Formula
    arity: int
    generator: IndicesTupleGenerator
    config: HitConfig

    @classmethod
    def new(
        cls,
        operations: dict[int, list[Operation]],
        tuples: list[TupleHistory],
        targets: list[Relation],
        formula: Formula,
        config: HitConfig,
    ) -> Block:
        arity = targets[0].arity
        nuevos = list(range(arity))
        generator = IndicesTupleGenerator.new(operations, arity, [], nuevos)
        return cls(
            operations=operations,
            tuples=tuples,
            targets=targets,
            formula=formula,
            arity=arity,
            generator=generator,
            config=config,
        )

    def is_all_in_targets(self) -> bool:
        return all(th.in_target for th in self.tuples)

    def is_disjunt_to_targets(self) -> bool:
        return all(not th.in_target for th in self.tuples)

    def finished(self) -> bool:
        return self.generator.finished

    def step(self) -> list[Block] | Counterexample:
        op_ti = self._next_candidate()
        if op_ti is None:
            return [copy.deepcopy(self)]

        op, ti = op_ti
        result: dict[int, list[TupleHistory]] = {}
        any_has_gen = False
        tuples = self.tuples
        self.tuples = []
        for th in tuples:
            th = copy.deepcopy(th)
            idx = th.step(op, ti)
            any_has_gen = any_has_gen or th.has_generated
            result.setdefault(idx, []).append(th)

        if len(result) == 1:
            if any_has_gen:
                self.generator.hubo_nuevo()
            self.tuples = next(iter(result.values()))
            return [copy.deepcopy(self)]

        num_groups = len(result)
        generators = self.generator.fork(num_groups)
        blocks: list[Block] = []
        fneg = formulas.true_formula(None)
        negados: list[tuple[int, int, list[TupleHistory]]] = []
        i = 0
        for index, tuples_new in sorted(result.items()):
            if any(th.has_generated for th in tuples_new):
                generators[i].hubo_nuevo()
                negados.append((i, index, tuples_new))
            else:
                fd = generators[i].formula_diferenciadora(index)
                f = self.formula.and_formula(fd)
                fneg = fneg.and_formula(fd.neg())
                blocks.append(
                    Block(
                        operations=copy.deepcopy(self.operations),
                        tuples=tuples_new,
                        targets=copy.deepcopy(self.targets),
                        formula=f,
                        arity=self.arity,
                        generator=generators[i],
                        config=self.config,
                    )
                )
            i += 1
        for i, _index, tuples_new in negados:
            f = self.formula.and_formula(fneg)
            blocks.append(
                Block(
                    operations=copy.deepcopy(self.operations),
                    tuples=tuples_new,
                    targets=copy.deepcopy(self.targets),
                    formula=f,
                    arity=self.arity,
                    generator=generators[i],
                    config=self.config,
                )
            )
        return blocks

    def _next_candidate(self) -> tuple[Operation, list[int]] | None:
        if self.config.use_information_gain:
            if self.config.ig_sample == 1:
                nxt = self.generator.step()
                if nxt is None:
                    self.generator.finished = True
                return nxt
            cand_list = (
                self.generator.take_candidates(self.config.ig_sample)
                if self.config.ig_sample is not None
                else self.generator.enumerate_candidates()
            )
            if not cand_list:
                self.generator.finished = True
                return None
            tuples_clone = copy.deepcopy(self.tuples)
            n = len(tuples_clone)
            in_total = sum(1 for th in tuples_clone if th.in_target)
            best: tuple[float, int, Operation, list[int]] | None = None
            for idx, (op, ti) in enumerate(cand_list):
                part: dict[tuple[int, bool], tuple[int, int]] = {}
                for th in tuples_clone:
                    sim_idx, _ = th.simulate_step(op, ti)
                    key = (sim_idx, th.in_target)
                    g_in, g_out = part.get(key, (0, 0))
                    if th.in_target:
                        part[key] = (g_in + 1, g_out)
                    else:
                        part[key] = (g_in, g_out + 1)
                ig = information_gain_from_counts(n, in_total, part)
                if best is None or ig > best[0]:
                    best = (ig, idx, op, ti)
            if best is None:
                self.generator.finished = True
                return None
            return self.generator.step()
        return self.generator.step()


def _cartesian_product_sized(items: list[int], n: int) -> list[list[int]]:
    result: list[list[int]] = [[]]
    for _ in range(n):
        result = [r + [item] for r in result for item in items]
    return result


def is_open_def(
    model: Model,
    targets: list[Relation],
    config: HitConfig | None = None,
) -> Formula | Counterexample:
    """Run the HIT algorithm; returns a defining formula or a counterexample."""
    cfg = config or HitConfig()
    arity = targets[0].arity
    universe = model.universe
    mut_targets = targets
    tuples = [
        TupleHistory.new(list(t), mut_targets)
        for t in _cartesian_product_sized(universe, arity)
    ]
    tuples.sort(key=lambda th: th.t)
    operations: dict[int, list[Operation]] = {}
    for op in model.operations.values():
        operations.setdefault(op.arity, []).append(copy.deepcopy(op))
    for op_list in operations.values():
        op_list.sort(key=lambda o: o.sym)
    pattern = targets[0].pattern
    if pattern is None:
        raise ValueError("Target relation must have a pattern (run preprocessing first)")
    formula = pattern.preprocessed_formula()
    start_block = Block.new(operations, tuples, mut_targets, formula, cfg)
    return _is_open_def_sequential(start_block)


def _is_open_def_sequential(block: Block) -> Formula | Counterexample:
    current = block
    while True:
        if current.is_all_in_targets():
            return current.formula
        if current.is_disjunt_to_targets():
            return formulas.false_formula(None)
        if current.finished():
            return Counterexample([list(th.t) for th in current.tuples])
        children = current.step()
        if isinstance(children, Counterexample):
            return children
        if len(children) == 1:
            current = children[0]
            continue
        results: list[Formula | Counterexample] = [
            _is_open_def_sequential(child) for child in children
        ]
        for res in results:
            if isinstance(res, Counterexample):
                return res
        combined = formulas.false_formula(None)
        for f in results:
            assert isinstance(f, Formula)
            combined = combined.or_formula(f)
        return combined
