# Вставка контента в существующий документ (Режим 2)

## Цель
Добавить новый контент в уже существующий Word-документ, не ломая структуру и форматирование.

## Входные данные
1. **Существующий .docx** — файл, в который вставляем
2. **Raw-текст** — новый контент для вставки
3. **Позиция** — где вставлять:
   - `append` — в конец документа
   - `after_heading` — после указанного заголовка
   - `before_heading` — перед указанным заголовком
   - `replace_section` — заменить содержимое раздела (заголовок остаётся)
4. **Заголовок** (для after/before/replace) — текст целевого заголовка

## Инструменты
- `execution/word_injector.py` — основной инструмент
- `execution/content_processor.py` — парсинг нового контента
- `execution/gost_formatter.py` — опциональное форматирование

## Пайплайн

### Шаг 1: Анализ существующего документа
```bash
python execution/word_injector.py --analyze existing.docx --output dummy.docx
```
Это покажет: заголовки, количество абзацев, таблиц, наличие оглавления.

### Шаг 2: Вставка контента
```bash
# В конец документа
python execution/word_injector.py \
  --target existing.docx \
  --input new_content.txt \
  --output result.docx \
  --position append

# После конкретного заголовка
python execution/word_injector.py \
  --target existing.docx \
  --input new_content.txt \
  --output result.docx \
  --position after_heading \
  --heading "Введение"

# Замена раздела
python execution/word_injector.py \
  --target existing.docx \
  --input new_content.txt \
  --output result.docx \
  --position replace_section \
  --heading "Глава 3"
```

### Шаг 3 (опционально): Переформатирование по ГОСТ
Добавьте флаг `--apply-gost` чтобы переформатировать весь документ:
```bash
python execution/word_injector.py \
  --target existing.docx \
  --input new_content.txt \
  --output result.docx \
  --position append \
  --apply-gost
```

## Ожидаемый результат
- **Оригинальный файл НЕ изменяется** — результат сохраняется в `--output`
- Нумерация таблиц и формул продолжается с учётом существующих
- Форматирование нового контента соответствует стилям документа

## Краевые случаи
- **Заголовок не найден** — скрипт выбросит ошибку с подсказкой (используйте `--analyze` для поиска)
- **Поиск заголовков** — регистронезависимый, ищет подстроку (т.е. «введение» найдёт «ВВЕДЕНИЕ»)
- **Кириллица в заголовках** — поддерживается полностью
- **Таблицы/формулы в новом контенте** — нумерация автоматическая

## Уроки
- (Обновляйте этот раздел при обнаружении ошибок)
