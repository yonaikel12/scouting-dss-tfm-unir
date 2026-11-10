"""Tipografía matemática para la memoria Word del TFM.

Combina dos técnicas:
1. Ecuaciones nativas OMML (Office Math) para las fórmulas en bloque: LaTeX -> MathML
   (latex2mathml) -> OMML (hoja oficial MML2OMML.XSL de Microsoft Office).
2. Símbolos Unicode y matemática en línea para variables dentro del texto (τ, λ, ≥, ≤, →, ×...).

Uso: llamar a `apply_math_typography(doc)` justo antes de guardar el documento.
"""

from __future__ import annotations

import copy
import re
from pathlib import Path
from typing import Callable, List, Optional, Tuple, Union

from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm
from lxml import etree

try:
    from latex2mathml.converter import convert as _latex_to_mathml
except ImportError as exc:  # pragma: no cover
    raise ImportError("Instale latex2mathml (pip install latex2mathml)") from exc

M_NS = "http://schemas.openxmlformats.org/officeDocument/2006/math"
W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"

_XSL_CANDIDATES = [
    r"C:\Program Files\Microsoft Office\root\Office16\MML2OMML.XSL",
    r"C:\Program Files (x86)\Microsoft Office\root\Office16\MML2OMML.XSL",
    r"C:\Program Files\Microsoft Office\Office16\MML2OMML.XSL",
    r"C:\Program Files (x86)\Microsoft Office\Office16\MML2OMML.XSL",
    r"C:\Program Files\Microsoft Office\Office15\MML2OMML.XSL",
]
_transform = None
_cache: dict = {}


def _get_transform():
    global _transform
    if _transform is None:
        for cand in _XSL_CANDIDATES:
            if Path(cand).exists():
                _transform = etree.XSLT(etree.parse(cand))
                break
        else:
            raise FileNotFoundError("No se encontró MML2OMML.XSL (requiere Microsoft Office)")
    return _transform


def latex_to_omml(latex: str) -> etree._Element:
    """Convierte LaTeX a un elemento <m:oMath> nativo de Word."""
    if latex not in _cache:
        mathml = _latex_to_mathml(latex)
        omml_doc = _get_transform()(etree.fromstring(mathml.encode("utf-8")))
        root = omml_doc.getroot()
        omath = root if root.tag == f"{{{M_NS}}}oMath" else root.find(f".//{{{M_NS}}}oMath")
        _cache[latex] = omath
    return copy.deepcopy(_cache[latex])


def _style_math_runs(omath, size_half_points: Optional[str]) -> None:
    for m_r in omath.iter(f"{{{M_NS}}}r"):
        rpr = m_r.find(qn("w:rPr"))
        if rpr is None:
            rpr = OxmlElement("w:rPr")
            m_r.insert(0 if m_r.find(f"{{{M_NS}}}rPr") is None else 1, rpr)
        fonts = OxmlElement("w:rFonts")
        for attr in ("w:ascii", "w:hAnsi", "w:cs"):
            fonts.set(qn(attr), "Cambria Math")
        rpr.insert(0, fonts)
        if size_half_points:
            for tag in ("w:sz", "w:szCs"):
                el = OxmlElement(tag)
                el.set(qn("w:val"), size_half_points)
                rpr.append(el)


# ---------------------------------------------------------------------------
# 1. ECUACIONES EN BLOQUE
# ---------------------------------------------------------------------------
# Clave: inicio del texto del párrafo (tras strip). Valor: lista de ecuaciones LaTeX
# (cada una recibe número consecutivo).
BLOCK_EQUATIONS: dict = {
    "d_N(A, B) = (2 * d_L(A, B))": [
        r"d_N(A,B)=\frac{2\,d_L(A,B)}{|A|+|B|+d_L(A,B)}\quad\Rightarrow\quad s_N(A,B)=1-d_N(A,B)",
        r"S_{\text{híbrida}}(A,B)=0{,}60\cdot s_N(A,B)+0{,}40\cdot \text{token_sort_ratio}(A,B)",
    ],
    "M_per90(i, j) = (X_{i,j} / M_i)": [
        r"M_{\text{per90}}(i,j)=\frac{X_{i,j}}{M_i}\cdot 90{,}0",
    ],
    "M_p90_adj(i, j) = M_per90(i, j)": [
        r"M_{\text{p90,adj}}(i,j)=M_{\text{per90}}(i,j)\cdot\frac{50{,}0}{P_{c(i)}}",
    ],
    "psi(y; lambda) = ((y + 1)^lambda": [
        r"\psi(y;\lambda)=\begin{cases}\dfrac{(y+1)^{\lambda}-1}{\lambda} & y\geq 0,\ \lambda\neq 0\\"
        r"\ln(y+1) & y\geq 0,\ \lambda=0\\"
        r"-\dfrac{(-y+1)^{2-\lambda}-1}{2-\lambda} & y<0,\ \lambda\neq 2\\"
        r"-\ln(-y+1) & y<0,\ \lambda=2\end{cases}",
    ],
    "Z_{i,j} = (psi(Y_{i,j}; lambda_j)": [
        r"Z_{i,j}=\frac{\psi(Y_{i,j};\lambda_j)-\mu_{\psi_j}}{\sigma_{\psi_j}}",
    ],
    "R * v_k = lambda_k * v_k": [
        r"R\,v_k=\lambda_k\,v_k,\qquad \lambda_1\geq\lambda_2\geq\cdots\geq\lambda_p\geq 0",
    ],
    "Varianza_Acumulada(d)": [
        r"\text{Varianza acumulada}(d)=\frac{\sum_{k=1}^{d}\lambda_k}{p}\geq 0{,}75",
    ],
    "WCSS(C) = Sum_{k=1}^K": [
        r"\mathrm{WCSS}(C)=\sum_{k=1}^{K}\sum_{y_i\in C_k}\left\lVert y_i-\mu_k\right\rVert_2^{2}",
    ],
    "Delta(C_a, C_b) = ((|C_a|": [
        r"\Delta(C_a,C_b)=\frac{|C_a|\,|C_b|}{|C_a|+|C_b|}\left\lVert \mu_a-\mu_b\right\rVert_2^{2}",
    ],
    "ARI(U, V) = (Indice_Observado": [
        r"\mathrm{ARI}(U,V)=\frac{\text{Índice observado}-\text{Índice esperado}}"
        r"{\text{Índice máximo}-\text{Índice esperado}}\geq 0{,}70",
    ],
    "d_ACP(i*, j) = sqrt(": [
        r"d_{\text{ACP}}(i^{*},j)=\sqrt{\sum_{m=1}^{d}w_m\,\left(Y_{i^{*},m}-Y_{j,m}\right)^{2}}"
        r"\quad\Rightarrow\quad \text{Similitud}(i^{*},j)=100\cdot e^{-0{,}45\,d_{\text{ACP}}(i^{*},j)}",
    ],
    "Net_Value(i) = Z_ACP_Rendimiento(i)": [
        r"\text{Net Value}(i)=Z_{\text{ACP}}(i)-Z_{\text{Coste}}(i)",
    ],
}

_eq_counter = {"n": 0}


def _make_equation_paragraph(doc, latex: str, number: str):
    p = OxmlElement("w:p")
    ppr = OxmlElement("w:pPr")
    tabs = OxmlElement("w:tabs")
    for val, pos in (("center", int(Cm(8.0).twips)), ("right", int(Cm(16.0).twips))):
        tab = OxmlElement("w:tab")
        tab.set(qn("w:val"), val)
        tab.set(qn("w:pos"), str(pos))
        tabs.append(tab)
    ppr.append(tabs)
    spacing = OxmlElement("w:spacing")
    spacing.set(qn("w:before"), "80")
    spacing.set(qn("w:after"), "80")
    spacing.set(qn("w:line"), "240")
    spacing.set(qn("w:lineRule"), "auto")
    ppr.append(spacing)
    jc = OxmlElement("w:jc")
    jc.set(qn("w:val"), "left")
    ppr.append(jc)
    p.append(ppr)

    def tab_run():
        r = OxmlElement("w:r")
        r.append(OxmlElement("w:tab"))
        return r

    p.append(tab_run())
    omath = latex_to_omml(latex)
    _style_math_runs(omath, None)
    p.append(omath)
    p.append(tab_run())
    r = OxmlElement("w:r")
    t = OxmlElement("w:t")
    t.text = f"({number})"
    r.append(t)
    p.append(r)
    return p


def _replace_block_equations(doc, chapter_prefix: str = "3") -> int:
    count = 0
    for para in list(doc.paragraphs):
        txt = para.text.strip()
        for key, eqs in BLOCK_EQUATIONS.items():
            if txt.startswith(key):
                anchor = para._element
                for latex in eqs:
                    _eq_counter["n"] += 1
                    new_p = _make_equation_paragraph(doc, latex, f"{chapter_prefix}.{_eq_counter['n']}")
                    anchor.addprevious(new_p)
                    count += 1
                anchor.getparent().remove(anchor)
                break
    return count


# ---------------------------------------------------------------------------
# 2. MATEMÁTICA EN LÍNEA Y SÍMBOLOS UNICODE
# ---------------------------------------------------------------------------
def _num(m: "re.Match") -> str:
    return m.group(1).replace(".", "{,}").replace(",", "{,}")


InlineRule = Tuple[str, Union[str, Callable[["re.Match"], str]]]

INLINE_RULES: List[InlineRule] = [
    (r"s\(i\) = \(b\(i\) - a\(i\)\) / max\{a\(i\), b\(i\)\}",
     r"s(i)=\frac{b(i)-a(i)}{\max\{a(i),b(i)\}}"),
    (r"Z_Coste_Financiero\(i\) =\s+Estandarizar\(0,60 \* Z_Valor_Mercado\(i\) \+ 0,40 \* Z_Salario_Bruto\(i\)\)",
     r"Z_{\text{Coste}}(i)=\text{Estandarizar}\left(0{,}60\,Z_{\text{VM}}(i)+0{,}40\,Z_{\text{Sal}}(i)\right)"),
    (r"Net Value = Z_ACP_Rendimiento - Z_Coste_Financiero",
     r"\text{Net Value}=Z_{\text{ACP}}-Z_{\text{Coste}}"),
    (r"Z_ACP - Z_Coste", r"Z_{\text{ACP}}-Z_{\text{Coste}}"),
    (r"Net_Value\(i\) > 0", r"\text{Net Value}(i)>0"),
    (r"Net_Value\(i\)", r"\text{Net Value}(i)"),
    (r"Z_ACP >= 0 y Z_Coste < 0", None),  # placeholder (se resuelve abajo por reglas simples)
    (r"Z_(ACP|Coste)\s*(>=|<)\s*0",
     lambda m: r"Z_{\text{%s}}%s0" % (m.group(1), r"\geq " if m.group(2) == ">=" else "<")),
    (r"Z_ACP_Rendimiento\(i\)", r"Z_{\text{ACP}}(i)"),
    (r"Z_ACP_Rendimiento", r"Z_{\text{ACP}}"),
    (r"Z_Coste_Financiero\(i\)", r"Z_{\text{Coste}}(i)"),
    (r"Z_Coste_Financiero", r"Z_{\text{Coste}}"),
    (r"Z_Valor_Mercado", r"Z_{\text{VM}}"),
    (r"Z_Salario_Bruto", r"Z_{\text{Sal}}"),
    (r"\bZ_ACP\b", r"Z_{\text{ACP}}"),
    (r"\bZ_Coste\b", r"Z_{\text{Coste}}"),
    (r"\bZ_MV\b", r"Z_{\text{MV}}"),
    (r"\bZ_Sal\b", r"Z_{\text{Sal}}"),
    (r"0,60 \* Z_MV", None),
    (r"M_p90 \* \(50 / Pos_Club\)", r"M_{\text{p90}}\cdot\frac{50}{\text{Pos}_{\text{Club}}}"),
    (r"\bM_p90_adj\b", r"M_{\text{p90,adj}}"),
    (r"\bM_per90\b", r"M_{\text{per90}}"),
    (r"\btau = 0,85", r"\tau=0{,}85"),
    (r"kappa\(R\) < 30,0", r"\kappa(R)<30{,}0"),
    (r"kappa = (\d+[.,]\d+)", lambda m: r"\kappa=" + _num(m)),
    (r"p < 10\^-16", r"p<10^{-16}"),
    (r"10\^-16", r"10^{-16}"),
    (r"w_m = lambda_m / Sum\(lambda\)", r"w_m=\frac{\lambda_m}{\sum\lambda}"),
    (r"lambda_([a-z])\b", lambda m: r"\lambda_{%s}" % m.group(1)),
    (r"\blambda\b", r"\lambda"),
    (r"\bv_k\b", r"v_k"),
    (r"\bw_m\b", r"w_m"),
    (r"X_\{i,j\}", r"X_{i,j}"),
    (r"P_\{c\(i\)\}", r"P_{c(i)}"),
    (r"\bM_i\b", r"M_i"),
    (r"R = \(1 / \(N - 1\)\) \* Z\^T \* Z", r"R=\frac{1}{N-1}Z^{\top}Z"),
    (r"Y = Z \* V_d", r"Y=ZV_d"),
    (r"mu_j = 0", r"\mu_j=0"),
    (r"sigma_j\^2 = 1", r"\sigma_j^2=1"),
    (r"C = \{C_1, \.\.\., C_K\}", r"C=\{C_1,\dots,C_K\}"),
    (r"Delta\(C_a, C_b\)", r"\Delta(C_a,C_b)"),
    (r"\(C_a, C_b\)", r"(C_a,C_b)"),
    (r"d_ACP\(i\*, j\)", r"d_{\text{ACP}}(i^{*},j)"),
    (r"y in R\b", r"y\in\mathbb{R}"),
    (r"j en \{1, \.\.\., p\}", r"j\in\{1,\dots,p\}"),
    (r"\bln\(y\)", r"\ln(y)"),
    (r"S_hibrida < 0,85", r"S_{\text{híbrida}}<0{,}85"),
    (r"y en R\b", r"y\in\mathbb{R}"),
    (r"indefinidas para y = 0", None),
    (r"\by = 0\b", r"y=0"),
    (r"N x p\b", r"N\times p"),
    (r"N x d\b", r"N\times d"),
    (r"O\(N x M\)", r"O(N\times M)"),
    (r"O\(1\)", r"O(1)"),
    (r"K\* = 3", r"K^{*}=3"),
    (r"K\*", r"K^{*}"),
]
INLINE_RULES = [(p, l) for p, l in INLINE_RULES if l is not None]
_COMPILED = [(re.compile(p), l) for p, l in INLINE_RULES]

UNICODE_SUBS = [
    (">=", "≥"),
    ("<=", "≤"),
    ("+-", "±"),
    (" -> ", " → "),
    ("->", "→"),
    (" * ", " × "),
]


def _unicode(text: str) -> str:
    for a, b in UNICODE_SUBS:
        text = text.replace(a, b)
    return text


def _split_math(text: str) -> List[Tuple[str, str]]:
    """Divide un texto en trozos ('t', texto) y ('m', latex)."""
    out: List[Tuple[str, str]] = []
    pos = 0
    while pos < len(text):
        best = None
        for rx, latex in _COMPILED:
            m = rx.search(text, pos)
            if m and (best is None or m.start() < best[0].start()
                      or (m.start() == best[0].start() and m.end() > best[0].end())):
                best = (m, latex)
        if best is None:
            break
        m, latex = best
        if m.start() > pos:
            out.append(("t", text[pos:m.start()]))
        out.append(("m", latex(m) if callable(latex) else latex))
        pos = m.end()
    if pos < len(text):
        out.append(("t", text[pos:]))
    return out


def _is_heading(p_el, doc) -> bool:
    ppr = p_el.find(qn("w:pPr"))
    if ppr is None:
        return False
    ps = ppr.find(qn("w:pStyle"))
    if ps is None:
        return False
    sid = ps.get(qn("w:val")) or ""
    return sid.lower().startswith(("heading", "ttulo", "título", "titulo"))


def _process_paragraph(p_el, doc, allow_math: bool) -> None:
    for r in list(p_el.findall(qn("w:r"))):
        children = [c for c in r if c.tag != qn("w:rPr")]
        if not children:
            continue
        only_text = all(c.tag == qn("w:t") for c in children)
        if not only_text:
            for t in r.findall(qn("w:t")):
                if t.text:
                    t.text = _unicode(t.text)
            continue
        text = "".join(t.text or "" for t in children)
        if not text:
            continue
        if "python -m" in text or "pip " in text:
            continue
        pieces = _split_math(text) if allow_math else [("t", text)]
        if not any(k == "m" for k, _ in pieces):
            new_text = _unicode(text)
            if new_text != text:
                for t in children[1:]:
                    r.remove(t)
                children[0].text = new_text
                children[0].set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
            continue
        rpr = r.find(qn("w:rPr"))
        sz = None
        if rpr is not None and rpr.find(qn("w:sz")) is not None:
            sz = rpr.find(qn("w:sz")).get(qn("w:val"))
        new_nodes = []
        for kind, content in pieces:
            if kind == "t":
                nr = OxmlElement("w:r")
                if rpr is not None:
                    nr.append(copy.deepcopy(rpr))
                nt = OxmlElement("w:t")
                nt.text = _unicode(content)
                nt.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
                nr.append(nt)
                new_nodes.append(nr)
            else:
                om = latex_to_omml(content)
                _style_math_runs(om, sz)
                new_nodes.append(om)
        for node in new_nodes:
            r.addprevious(node)
        p_el.remove(r)


def apply_math_typography(doc) -> dict:
    """Aplica ecuaciones OMML en bloque y matemática/Unicode en línea a todo el documento."""
    _eq_counter["n"] = 0
    n_blocks = _replace_block_equations(doc)
    body = doc.element.body
    in_references = False
    n_inline = 0
    for p_el in list(body.iter(qn("w:p"))):
        heading = _is_heading(p_el, doc)
        text = "".join(t.text or "" for t in p_el.iter(qn("w:t")))
        if heading and text.strip().upper().startswith("REFERENCIAS BIBLIOGR"):
            in_references = True
        if p_el.find(f"{{{M_NS}}}oMath") is not None:
            continue
        before = len(list(p_el.iter(f"{{{M_NS}}}oMath")))
        _process_paragraph(p_el, doc, allow_math=not heading and not in_references)
        n_inline += len(list(p_el.iter(f"{{{M_NS}}}oMath"))) - before
    return {"block_equations": n_blocks, "inline_math": n_inline}
