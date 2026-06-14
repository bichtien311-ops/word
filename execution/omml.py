"""
Нативный рендер формул LaTeX -> OMML (Office Math) для вставки в Word.

Пайплайн: LaTeX --(latex2mathml)--> MathML --(MML2OMML.XSL)--> OMML.
OMML вставляется прямо в XML абзаца python-docx, поэтому формула в Word
становится редактируемой нативной формулой, а не картинкой/текстом.

Если конвертация невозможна (нет XSL, ошибка парсинга LaTeX), функции
возвращают None — вызывающий код должен сделать фолбэк на текстовую запись.
"""
from __future__ import annotations

import logging
import os
from functools import lru_cache

log = logging.getLogger(__name__)

# Возможные расположения трансформации MathML -> OMML, поставляемой с MS Office
_XSL_CANDIDATES = [
    r"C:\Program Files (x86)\Microsoft Office\Office16\MML2OMML.XSL",
    r"C:\Program Files\Microsoft Office\Office16\MML2OMML.XSL",
    r"C:\Program Files (x86)\Microsoft Office\Office15\MML2OMML.XSL",
    r"C:\Program Files\Microsoft Office\Office15\MML2OMML.XSL",
    r"C:\Program Files (x86)\Microsoft Office\Office14\MML2OMML.XSL",
    r"C:\Program Files\Microsoft Office\Office14\MML2OMML.XSL",
]


def find_mml2omml_xsl() -> str | None:
    """Ищет файл MML2OMML.XSL. Можно переопределить через переменную окружения."""
    env = os.environ.get("MML2OMML_XSL")
    if env and os.path.isfile(env):
        return env
    for path in _XSL_CANDIDATES:
        if os.path.isfile(path):
            return path
    # Поиск по дереву Microsoft Office (медленный, как крайняя мера)
    for base in (r"C:\Program Files\Microsoft Office",
                 r"C:\Program Files (x86)\Microsoft Office"):
        if os.path.isdir(base):
            for root, _dirs, files in os.walk(base):
                if "MML2OMML.XSL" in files:
                    return os.path.join(root, "MML2OMML.XSL")
    return None


@lru_cache(maxsize=1)
def _get_transform():
    """Загружает и кеширует XSLT-трансформацию MathML -> OMML."""
    try:
        from lxml import etree
    except ImportError:
        log.warning("lxml не установлен — нативный рендер формул недоступен")
        return None

    xsl_path = find_mml2omml_xsl()
    if not xsl_path:
        log.warning("MML2OMML.XSL не найден — нативный рендер формул недоступен")
        return None

    try:
        xslt_doc = etree.parse(xsl_path)
        return etree.XSLT(xslt_doc)
    except Exception as e:  # noqa: BLE001
        log.warning(f"Не удалось загрузить MML2OMML.XSL: {e}")
        return None


def omml_available() -> bool:
    """True, если нативный рендер формул доступен в текущем окружении."""
    if _get_transform() is None:
        return False
    try:
        import latex2mathml.converter  # noqa: F401
        return True
    except ImportError:
        return False


def latex_to_omml_element(latex: str):
    """
    Преобразует строку LaTeX в элемент OMML (lxml _Element).
    Возвращает None при любой ошибке — вызывающий код делает фолбэк на текст.
    """
    transform = _get_transform()
    if transform is None:
        return None

    try:
        import latex2mathml.converter
        from lxml import etree
    except ImportError:
        return None

    cleaned = _clean_latex(latex)
    if not cleaned:
        return None

    try:
        mathml = latex2mathml.converter.convert(cleaned)
        mathml_tree = etree.fromstring(mathml)
        omml_tree = transform(mathml_tree)
        root = omml_tree.getroot()
        if root is None:
            return None
        return root
    except Exception as e:  # noqa: BLE001
        log.info(f"Фолбэк на текст: не удалось сконвертировать формулу '{latex[:40]}': {e}")
        return None


def _clean_latex(latex: str) -> str:
    """Убирает обёртки $$/$/\\[ \\] и окружения align/equation для конвертера."""
    s = latex.strip()
    # Снимаем парные $$ ... $$ и $ ... $
    if s.startswith("$$") and s.endswith("$$"):
        s = s[2:-2].strip()
    elif s.startswith("$") and s.endswith("$"):
        s = s[1:-1].strip()
    if s.startswith("\\[") and s.endswith("\\]"):
        s = s[2:-2].strip()
    # align/aligned/equation -> убираем окружение, оставляя тело
    for env in ("align*", "align", "aligned", "equation*", "equation", "gather", "gathered"):
        begin = "\\begin{" + env + "}"
        end = "\\end{" + env + "}"
        if begin in s:
            s = s.replace(begin, "").replace(end, "")
    # Выравнивающие амперсанды латеха не нужны в одиночной формуле
    s = s.replace("&", "")
    return s.strip()
