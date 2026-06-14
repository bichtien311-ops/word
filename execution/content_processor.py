"""
Обработчик контента для подготовки текста перед вставкой в Word.

Отвечает за:
- Очистку raw-вывода из NotebookLM
- Замену точек на запятые в числах (ГОСТ)
- Парсинг LaTeX-формул
- Парсинг Markdown-таблиц
- Автоматическое определение структуры текста
"""

import os
import re
import sys
from dataclasses import dataclass, field
from enum import Enum

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "utils"))
from logger import setup_logger

log = setup_logger("content_processor")


# =============================================================================
# МОДЕЛИ ДАННЫХ
# =============================================================================

class ContentBlockType(str, Enum):
    """Типы блоков контента."""
    HEADING = "heading"
    PARAGRAPH = "paragraph"
    FORMULA = "formula"
    TABLE = "table"
    LIST_ITEM = "list_item"
    FIGURE_CAPTION = "figure_caption"
    EMPTY = "empty"


@dataclass
class ContentBlock:
    """Один блок структурированного контента."""
    block_type: ContentBlockType
    content: str
    level: int = 0          # Уровень заголовка (1, 2, 3) или вложенности списка
    number: str = ""        # Номер (формулы, таблицы, рисунка)
    metadata: dict = field(default_factory=dict)  # Доп. данные (variables для формул, headers для таблиц)


@dataclass
class ParsedTable:
    """Распарсенная таблица из Markdown."""
    headers: list[str]
    rows: list[list[str]]
    caption: str = ""
    number: str = ""


# =============================================================================
# ОБРАБОТКА ЧИСЕЛ
# =============================================================================

def fix_numbers(text: str) -> str:
    """
    Заменяет точки на запятые в десятичных числах по ГОСТ.
    32.09 → 32,09
    Не трогает точки в аббревиатурах, URL, IP-адресах и т.д.
    """
    # Паттерн: цифры.цифры (но не IP и не версии вида 1.2.3)
    def replace_decimal(match):
        full = match.group(0)
        # Проверяем, не является ли это частью IP или версии (более двух точек)
        return full.replace(".", ",", 1)

    # Заменяем только одиночные десятичные точки между цифрами
    result = re.sub(r"(?<!\d)(\d+)\.(\d+)(?!\.\d)", r"\1,\2", text)
    log.debug(f"fix_numbers: обработано {len(text)} символов")
    return result


# =============================================================================
# ПАРСИНГ LATEX-ФОРМУЛ
# =============================================================================

def extract_latex_formulas(text: str) -> list[dict]:
    """
    Извлекает LaTeX-формулы из текста.
    Ищет паттерны:
    - ```latex ... ```
    - $$ ... $$
    - \\[ ... \\]
    - Блоки кода с LaTeX-паттернами (\\frac, \\cdot, etc.)

    Returns:
        Список словарей {"latex": str, "position": int, "plain_text": str}
    """
    formulas = []

    # Паттерн 1: Блоки кода с LaTeX
    for match in re.finditer(r"```(?:latex)?\s*\n(.*?)\n```", text, re.DOTALL):
        content = match.group(1).strip()
        if _looks_like_latex(content):
            formulas.append({
                "latex": content,
                "position": match.start(),
                "plain_text": _latex_to_plain(content)
            })

    # Паттерн 2: $$ ... $$
    for match in re.finditer(r"\$\$(.*?)\$\$", text, re.DOTALL):
        formulas.append({
            "latex": match.group(1).strip(),
            "position": match.start(),
            "plain_text": _latex_to_plain(match.group(1).strip())
        })

    # Паттерн 3: Инлайн-LaTeX (одиночные строки с \\frac, \\cdot и т.д.)
    for match in re.finditer(r"^([^\n]*(?:\\frac|\\cdot|\\sqrt|\\sum|\\int|\\text\{)[^\n]*)$",
                             text, re.MULTILINE):
        content = match.group(1).strip()
        # Проверяем, не нашли ли мы это уже в блоке кода
        already_found = any(f["latex"] == content for f in formulas)
        if not already_found:
            formulas.append({
                "latex": content,
                "position": match.start(),
                "plain_text": _latex_to_plain(content)
            })

    log.info(f"Найдено LaTeX-формул: {len(formulas)}")
    return formulas


def _looks_like_latex(text: str) -> bool:
    """Проверяет, похож ли текст на LaTeX-формулу."""
    latex_indicators = ["\\frac", "\\cdot", "\\sqrt", "\\sum", "\\int",
                        "\\text{", "_{", "^{", "\\alpha", "\\beta",
                        "\\tan", "\\sin", "\\cos", "\\pi"]
    return any(ind in text for ind in latex_indicators)


def _latex_to_plain(latex: str) -> str:
    """
    Упрощённое преобразование LaTeX в текст для Word.
    Не полный конвертер — для базового отображения.
    """
    result = latex
    # Дроби
    result = re.sub(r"\\frac\{([^}]*)\}\{([^}]*)\}", r"(\1) / (\2)", result)
    # Операторы
    result = result.replace("\\cdot", "·")
    result = result.replace("\\times", "×")
    result = result.replace("\\sqrt", "√")
    result = result.replace("\\pm", "±")
    result = result.replace("\\leq", "≤")
    result = result.replace("\\geq", "≥")
    result = result.replace("\\neq", "≠")
    result = result.replace("\\approx", "≈")
    # Тригонометрия
    result = result.replace("\\tan", "tg")
    result = result.replace("\\sin", "sin")
    result = result.replace("\\cos", "cos")
    # Греческие буквы
    result = result.replace("\\alpha", "α")
    result = result.replace("\\beta", "β")
    result = result.replace("\\gamma", "γ")
    result = result.replace("\\delta", "δ")
    result = result.replace("\\omega", "ω")
    result = result.replace("\\pi", "π")
    result = result.replace("\\phi", "φ")
    result = result.replace("\\Phi", "Φ")
    # Надстрочные и подстрочные
    result = re.sub(r"\^\{([^}]*)\}", r"^(\1)", result)
    result = re.sub(r"_\{([^}]*)\}", r"_(\1)", result)
    result = re.sub(r"\^(\w)", r"^\1", result)
    result = re.sub(r"_(\w)", r"_\1", result)
    # Текст внутри \text{}
    result = re.sub(r"\\text\{([^}]*)\}", r"\1", result)
    # Пробелы LaTeX
    result = result.replace("\\,", " ")
    result = result.replace("\\;", " ")
    result = result.replace("\\quad", "  ")
    # Убираем оставшиеся бэкслеши
    result = re.sub(r"\\([a-zA-Z]+)", r"\1", result)
    # Чистим лишние пробелы
    result = re.sub(r"\s+", " ", result).strip()
    return result


# =============================================================================
# ПАРСИНГ MARKDOWN-ТАБЛИЦ
# =============================================================================

def parse_markdown_tables(text: str) -> list[ParsedTable]:
    """
    Парсит Markdown-таблицы из текста.

    Returns:
        Список ParsedTable
    """
    tables = []

    # Паттерн: строки начинающиеся с |
    table_pattern = re.compile(
        r"((?:^[^\n]*\|[^\n]*$\n?)+)",
        re.MULTILINE
    )

    for match in table_pattern.finditer(text):
        table_text = match.group(1).strip()
        lines = [line.strip() for line in table_text.split("\n") if line.strip()]

        if len(lines) < 2:
            continue

        # Парсим заголовки (первая строка)
        headers = _parse_table_row(lines[0])
        if not headers:
            continue

        # Пропускаем разделительную строку (---)
        data_start = 1
        if len(lines) > 1 and re.match(r"^\|[\s\-:|]+\|$", lines[1]):
            data_start = 2

        # Парсим строки данных
        rows = []
        for line in lines[data_start:]:
            row = _parse_table_row(line)
            if row:
                rows.append(row)

        if headers and rows:
            tables.append(ParsedTable(headers=headers, rows=rows))

    log.info(f"Найдено Markdown-таблиц: {len(tables)}")
    return tables


def _parse_table_row(line: str) -> list[str]:
    """Парсит одну строку Markdown-таблицы."""
    if "|" not in line:
        return []

    # Убираем крайние |
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]

    cells = [cell.strip() for cell in line.split("|")]
    return cells


# =============================================================================
# СТРУКТУРИРОВАНИЕ КОНТЕНТА
# =============================================================================

def structure_content(text: str) -> list[ContentBlock]:
    """
    Автоматически определяет структуру текста и разбивает на блоки.
    Распознаёт: заголовки (#), формулы, таблицы, списки, абзацы.

    Args:
        text: Raw-текст (Markdown или plain text)

    Returns:
        Список ContentBlock
    """
    blocks = []
    lines = text.split("\n")
    i = 0

    while i < len(lines):
        line = lines[i].strip()

        # --- Пустая строка ---
        if not line:
            i += 1
            continue

        # --- Markdown заголовки ---
        heading_match = re.match(r"^(#{1,3})\s+(.+)$", line)
        if heading_match:
            level = len(heading_match.group(1))
            blocks.append(ContentBlock(
                block_type=ContentBlockType.HEADING,
                content=heading_match.group(2).strip(),
                level=level
            ))
            i += 1
            continue

        # --- Нумерованные заголовки (1.2. Название) ---
        numbered_heading = re.match(r"^(\d+(?:\.\d+)*)\.\s+(.+)$", line)
        if numbered_heading:
            num = numbered_heading.group(1)
            level = num.count(".") + 1
            blocks.append(ContentBlock(
                block_type=ContentBlockType.HEADING,
                content=numbered_heading.group(2).strip(),
                level=min(level, 3),
                number=num
            ))
            i += 1
            continue

        # --- Блок кода / формулы ---
        if line.startswith("```"):
            code_content = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code_content.append(lines[i])
                i += 1
            i += 1  # Пропускаем закрывающие ```

            joined = "\n".join(code_content).strip()
            if _looks_like_latex(joined):
                blocks.append(ContentBlock(
                    block_type=ContentBlockType.FORMULA,
                    content=joined,
                    metadata={"plain_text": _latex_to_plain(joined)}
                ))
            else:
                # Обычный код — как параграф
                blocks.append(ContentBlock(
                    block_type=ContentBlockType.PARAGRAPH,
                    content=joined
                ))
            continue

        # --- Markdown таблица (начинается с |) ---
        if line.startswith("|"):
            table_lines = [line]
            i += 1
            while i < len(lines) and lines[i].strip().startswith("|"):
                table_lines.append(lines[i].strip())
                i += 1
            table_text = "\n".join(table_lines)
            parsed = parse_markdown_tables(table_text)
            if parsed:
                t = parsed[0]
                blocks.append(ContentBlock(
                    block_type=ContentBlockType.TABLE,
                    content=table_text,
                    metadata={"headers": t.headers, "rows": t.rows}
                ))
            continue

        # --- Список (- или цифра.) ---
        list_match = re.match(r"^[-•]\s+(.+)$", line)
        if not list_match:
            list_match = re.match(r"^(\d+)[.)]\s+(.+)$", line)
        if list_match:
            content = list_match.group(len(list_match.groups()))
            blocks.append(ContentBlock(
                block_type=ContentBlockType.LIST_ITEM,
                content=content
            ))
            i += 1
            continue

        # --- Инлайн-формула ---
        if _looks_like_latex(line):
            blocks.append(ContentBlock(
                block_type=ContentBlockType.FORMULA,
                content=line,
                metadata={"plain_text": _latex_to_plain(line)}
            ))
            i += 1
            continue

        # --- Обычный абзац ---
        paragraph_lines = [line]
        i += 1
        while i < len(lines):
            next_line = lines[i].strip()
            # Абзац заканчивается на пустой строке, заголовке, формуле и т.д.
            if (not next_line or
                    next_line.startswith("#") or
                    next_line.startswith("|") or
                    next_line.startswith("```") or
                    next_line.startswith("- ") or
                    re.match(r"^\d+[.)]\s", next_line) or
                    re.match(r"^\d+\.\d+\.\s", next_line) or
                    _looks_like_latex(next_line)):
                break
            paragraph_lines.append(next_line)
            i += 1

        blocks.append(ContentBlock(
            block_type=ContentBlockType.PARAGRAPH,
            content=" ".join(paragraph_lines)
        ))

    log.info(f"Структурировано блоков: {len(blocks)} "
             f"(заголовков: {sum(1 for b in blocks if b.block_type == ContentBlockType.HEADING)}, "
             f"абзацев: {sum(1 for b in blocks if b.block_type == ContentBlockType.PARAGRAPH)}, "
             f"формул: {sum(1 for b in blocks if b.block_type == ContentBlockType.FORMULA)}, "
             f"таблиц: {sum(1 for b in blocks if b.block_type == ContentBlockType.TABLE)})")

    return blocks


# =============================================================================
# ОЧИСТКА ВЫВОДА NotebookLM
# =============================================================================

def clean_notebooklm_output(text: str) -> str:
    """
    Очищает raw-вывод из NotebookLM:
    - Убирает маркеры источников [Source 1], [1] и т.д.
    - Убирает артефакты форматирования
    - Нормализует пробелы и переносы
    - Заменяет точки на запятые в числах
    """
    result = text

    # Убираем ссылки на источники [Source 1], [1], [1, 2], [2-4], [source: ...]
    result = re.sub(r"\[Source\s*\d+\]", "", result, flags=re.IGNORECASE)
    result = re.sub(r"\[source:\s*[^\]]*\]", "", result, flags=re.IGNORECASE)
    # Одиночные и составные числовые сноски: [1], [1, 2], [2-4], [10, 11, 15]
    result = re.sub(r"\[\s*\d+(?:\s*[,\u2013\u2014-]\s*\d+)*\s*\]", "", result)
    # Висячие пробелы перед знаками препинания после удаления сносок
    result = re.sub(r"\s+([.,;:])", r"\1", result)

    # Убираем маркеры цитат из NotebookLM
    result = re.sub(r"^>\s*", "", result, flags=re.MULTILINE)

    # Нормализуем переносы строк (убираем тройные+)
    result = re.sub(r"\n{3,}", "\n\n", result)

    # Убираем trailing spaces
    result = re.sub(r"[ \t]+$", "", result, flags=re.MULTILINE)

    # Схлопываем двойные пробелы (остаются после удаления сносок)
    result = re.sub(r"(?<=\S)[ \t]{2,}(?=\S)", " ", result)

    # Заменяем точки на запятые в числах
    result = fix_numbers(result)

    log.info(f"Очищен вывод NotebookLM: {len(text)} → {len(result)} символов")
    return result.strip()


# =============================================================================
# CLI
# =============================================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Обработчик контента для Word")
    parser.add_argument("input", help="Входной текстовый файл")
    parser.add_argument("--fix-numbers", action="store_true", help="Заменить точки на запятые")
    parser.add_argument("--extract-formulas", action="store_true", help="Извлечь LaTeX-формулы")
    parser.add_argument("--structure", action="store_true", help="Структурировать контент")
    parser.add_argument("--clean-nlm", action="store_true", help="Очистить вывод NotebookLM")

    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        text = f.read()

    if args.fix_numbers:
        print(fix_numbers(text))
    elif args.extract_formulas:
        for formula in extract_latex_formulas(text):
            print(f"LaTeX: {formula['latex']}")
            print(f"Plain: {formula['plain_text']}")
            print("---")
    elif args.structure:
        for block in structure_content(text):
            print(f"[{block.block_type.value}] (level={block.level}) {block.content[:80]}...")
    elif args.clean_nlm:
        print(clean_notebooklm_output(text))
    else:
        parser.print_help()
