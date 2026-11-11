# narrative-deslop

Скилл для Claude, который убирает нейрослоп из художественных текстов на уровне истории: проговорённую мораль, эмоции через «сжавшуюся грудь» и дождь за окном, сквозную метафору, героя, который в финале «понял и принял», длинный эпилог, линейный сюжет без подсюжетов, сплошной лиризм без иронии.

Основа: исследование **StoryScope** (Russell et al., 2026). Авторы сравнили 10 272 человеческих рассказа с рассказами GPT-5.4, Claude Sonnet 4.6, Gemini 3 Flash, DeepSeek V3.2 и Kimi K2.5 на те же промпты и извлекли 304 нарративных признака. Только по устройству истории, без учёта стиля, ИИ-текст распознаётся с точностью 93%. Построчная стилистическая правка эту точность почти не снижает. Поэтому скилл правит решения рассказчика, а не синонимы.

## Что внутри

| Файл | Что это |
|---|---|
| `SKILL.md` | 16 маркеров с цифрами «люди против ИИ», правила правки, отпечатки моделей, формат аудита с нейрослоп-индексом |
| `references/narrative-tells.md` | 120 значений признаков, где все пять моделей отклоняются от людей в одну сторону |
| `references/model-fingerprints.md` | Чем каждая модель отличается от остальных |
| `scripts/build_reference.py` | Пересобирает таблицы из данных StoryScope |

## Установка

Claude Code:

```bash
git clone https://github.com/imuha54-cmd/narrative-deslop ~/.claude/skills/narrative-deslop
```

Claude.ai: скачайте репозиторий архивом и загрузите в Settings → Capabilities → Skills.

## Использование

- «Прогони рассказ через narrative-deslop»
- «Проверь, не звучит ли эта история как нейросеть» (аудит без переписывания)
- «Убери нейрослоп из сценария рилса»

Для фразовой чистки (тире, «не X, а Y», триады) после этого скилла запускайте `stop-slop` или `humaniser`.

## Пересборка таблиц

```bash
git clone https://github.com/jenna-russell/storyscope
pip install pandas pyarrow
python scripts/build_reference.py storyscope references/
```

## Источник и лицензия

Russell J., Rajendhran R., Pham C. M., Iyyer M., Wieting J. *StoryScope: Investigating idiosyncrasies in AI fiction.* [arXiv:2604.03136](https://arxiv.org/abs/2604.03136). Данные и код: [jenna-russell/storyscope](https://github.com/jenna-russell/storyscope) (MIT).

Скилл распространяется по лицензии MIT.

---

**English.** A Claude skill that removes narrative-level AI tells from fiction (stated morals, emotion via body and weather, recurring conceits, epiphany endings, long epilogues, single-track plots, earnest tone without irony). Built on the StoryScope dataset of 61k human and LLM stories. Instructions are in Russian.
