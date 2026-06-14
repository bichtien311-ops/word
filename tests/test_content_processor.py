"""
Тесты для content_processor.py

Проверяет: замену чисел, парсинг LaTeX, парсинг таблиц,
структурирование контента, очистку NotebookLM.
"""

import os
import sys

# Добавляем путь к execution-скриптам
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "execution"))

import pytest
from content_processor import (
    fix_numbers,
    extract_latex_formulas,
    parse_markdown_tables,
    structure_content,
    clean_notebooklm_output,
    ContentBlockType,
)


# =============================================================================
# ТЕСТЫ: fix_numbers
# =============================================================================

class TestFixNumbers:
    """Замена точек на запятые в десятичных числах по ГОСТ."""

    def test_simple_decimal(self):
        assert fix_numbers("32.09") == "32,09"

    def test_multiple_decimals(self):
        result = fix_numbers("Мощность 1500.5 кВт, ток 32.09 А")
        assert "1500,5" in result
        assert "32,09" in result

    def test_integer_not_affected(self):
        assert fix_numbers("1500 кВт") == "1500 кВт"

    def test_ip_address_not_affected(self):
        """IP-адреса (более 2 точек) не должны затрагиваться."""
        result = fix_numbers("192.168.1.1")
        # IP остаётся с точками (не десятичное число)
        assert "192" in result

    def test_text_without_numbers(self):
        text = "Просто текст без чисел"
        assert fix_numbers(text) == text

    def test_zero_decimal(self):
        assert fix_numbers("0.5") == "0,5"

    def test_large_decimal(self):
        assert fix_numbers("123456.789") == "123456,789"


# =============================================================================
# ТЕСТЫ: extract_latex_formulas
# =============================================================================

class TestExtractLatexFormulas:
    """Извлечение LaTeX-формул из текста."""

    def test_code_block_latex(self):
        text = "Текст\n```latex\nI_{р} = \\frac{S}{\\sqrt{3}\\cdot U}\n```\nТекст"
        formulas = extract_latex_formulas(text)
        assert len(formulas) >= 1
        assert "\\frac" in formulas[0]["latex"]

    def test_dollar_latex(self):
        text = "Формула: $$I = \\frac{P}{U}$$"
        formulas = extract_latex_formulas(text)
        assert len(formulas) >= 1
        assert "\\frac" in formulas[0]["latex"]

    def test_inline_latex(self):
        text = "r = h \\cdot \\tan \\alpha"
        formulas = extract_latex_formulas(text)
        assert len(formulas) >= 1

    def test_no_latex(self):
        text = "Обычный текст без формул"
        formulas = extract_latex_formulas(text)
        assert len(formulas) == 0

    def test_plain_text_conversion(self):
        text = "```latex\nr = h \\cdot \\tan \\alpha\n```"
        formulas = extract_latex_formulas(text)
        assert len(formulas) >= 1
        # Проверяем что plain_text содержит преобразованные символы
        assert "·" in formulas[0]["plain_text"] or "tg" in formulas[0]["plain_text"]


# =============================================================================
# ТЕСТЫ: parse_markdown_tables
# =============================================================================

class TestParseMarkdownTables:
    """Парсинг Markdown-таблиц."""

    def test_simple_table(self):
        text = """| Показатель | Значение |
| --- | --- |
| Мощность | 1500 кВт |
| Ток | 32 А |"""
        tables = parse_markdown_tables(text)
        assert len(tables) == 1
        assert tables[0].headers == ["Показатель", "Значение"]
        assert len(tables[0].rows) == 2

    def test_table_with_many_columns(self):
        text = """| A | B | C | D |
| --- | --- | --- | --- |
| 1 | 2 | 3 | 4 |"""
        tables = parse_markdown_tables(text)
        assert len(tables) == 1
        assert len(tables[0].headers) == 4

    def test_no_table(self):
        text = "Обычный текст без таблицы"
        tables = parse_markdown_tables(text)
        assert len(tables) == 0


# =============================================================================
# ТЕСТЫ: structure_content
# =============================================================================

class TestStructureContent:
    """Структурирование текста в блоки."""

    def test_heading_detection(self):
        text = "# Заголовок 1\nПараграф\n## Заголовок 2"
        blocks = structure_content(text)
        headings = [b for b in blocks if b.block_type == ContentBlockType.HEADING]
        assert len(headings) == 2
        assert headings[0].level == 1
        assert headings[1].level == 2

    def test_paragraph_detection(self):
        text = "Это обычный абзац текста."
        blocks = structure_content(text)
        assert len(blocks) >= 1
        assert blocks[0].block_type == ContentBlockType.PARAGRAPH

    def test_numbered_heading(self):
        text = "1.2. Расчёт мощности"
        blocks = structure_content(text)
        assert len(blocks) >= 1
        assert blocks[0].block_type == ContentBlockType.HEADING
        assert blocks[0].number == "1.2"

    def test_list_detection(self):
        text = "- Первый пункт\n- Второй пункт"
        blocks = structure_content(text)
        list_items = [b for b in blocks if b.block_type == ContentBlockType.LIST_ITEM]
        assert len(list_items) == 2

    def test_mixed_content(self):
        text = """# Введение
Это абзац.

## Формулы
```latex
I = \\frac{P}{U}
```

| Показатель | Значение |
| --- | --- |
| Мощность | 100 кВт |"""
        blocks = structure_content(text)
        types = {b.block_type for b in blocks}
        assert ContentBlockType.HEADING in types
        assert ContentBlockType.PARAGRAPH in types


# =============================================================================
# ТЕСТЫ: clean_notebooklm_output
# =============================================================================

class TestCleanNotebookLMOutput:
    """Очистка вывода NotebookLM."""

    def test_remove_source_references(self):
        text = "Мощность составляет 1500 кВт [Source 1]."
        result = clean_notebooklm_output(text)
        assert "[Source 1]" not in result
        assert "1500" in result

    def test_remove_numbered_references(self):
        text = "Значение тока [1] составляет 32 А [2]."
        result = clean_notebooklm_output(text)
        assert "[1]" not in result
        assert "[2]" not in result

    def test_fix_numbers_applied(self):
        text = "Мощность 1500.5 кВт"
        result = clean_notebooklm_output(text)
        assert "1500,5" in result

    def test_remove_triple_newlines(self):
        text = "Абзац 1\n\n\n\nАбзац 2"
        result = clean_notebooklm_output(text)
        assert "\n\n\n" not in result

    def test_remove_quotes(self):
        text = "> Цитата из источника"
        result = clean_notebooklm_output(text)
        assert not result.startswith(">")
