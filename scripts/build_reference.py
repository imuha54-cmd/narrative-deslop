"""Пересобирает таблицы references/ из данных StoryScope.

Запуск:
    git clone https://github.com/jenna-russell/storyscope
    pip install pandas pyarrow
    python scripts/build_reference.py /path/to/storyscope references/
"""
import json
import sys
from pathlib import Path

import pandas as pd

SOURCES = ["gpt", "claude", "deepseek", "kimi", "gemini"]
DIM_RU = {
    "plot": "Сюжет", "agents": "Персонажи", "social_networks": "Социальные связи",
    "style": "Стиль", "setting": "Место действия", "events": "События",
    "revelation": "Раскрытие информации", "situatedness": "Тема и контекст",
    "temporal_structure": "Время и хронология", "perspective": "Точка зрения",
}


def load(root):
    tax = json.load(open(root / "data/taxonomy.json"))["feature_taxonomy"]
    meta = {}
    for dim, d in tax.items():
        for a in d["aspects"].values():
            for f in a["features"]:
                meta[f["id"]] = (dim, f["name"], f["question"], f["type"])
    return meta, pd.read_parquet(root / "data/storyscope_features.parquet")


def value_shares(meta, df):
    rows = []
    for fid, (dim, name, question, typ) in meta.items():
        if fid not in df:
            continue
        col = df[fid].fillna("").astype(str)
        if typ == "multi_select":
            parts = col.apply(lambda x: {v.strip() for v in x.split("|") if v.strip()})
            values = set().union(*parts)
            hit = lambda v: parts.apply(lambda s: v in s)
        else:
            values = set(col.unique()) - {""}
            hit = lambda v: col == v
        for v in values:
            m = hit(v)
            per = {s: m[df.source == s].mean() for s in SOURCES}
            rows.append(dict(fid=fid, dim=dim, name=name, question=question, value=v,
                             human=m[df.source == "human"].mean(),
                             ai=m[df.source != "human"].mean(), **per))
    r = pd.DataFrame(rows)
    r["diff"] = r.ai - r.human
    lo, hi = r[SOURCES].min(axis=1), r[SOURCES].max(axis=1)
    # «Согласованный» признак: все пять моделей по одну сторону от людей
    r["consistent"] = ((r["diff"] > 0) & (lo > r.human)) | ((r["diff"] < 0) & (hi < r.human))
    r["ai_min"], r["ai_max"] = lo, hi
    return r


def pct(x):
    return f"{x:.0%}"


def tells_md(r, n=120):
    top = r[r.consistent].reindex(r[r.consistent]["diff"].abs()
                                  .sort_values(ascending=False).index).head(n)
    out = ["# Нарративные признаки ИИ-прозы: полная таблица", "",
           "Источник: StoryScope (Russell et al., 2026, arXiv:2604.03136), "
           "61 575 рассказов: 10 239 человеческих и по ~10 270 от GPT-5.4, Claude Sonnet 4.6, "
           "Gemini 3 Flash, DeepSeek V3.2, Kimi K2.5 на одни и те же промпты.", "",
           f"Здесь {len(top)} значений признаков с самой большой разницей между людьми и ИИ, "
           "причём только те, где **все пять моделей** отклоняются в одну сторону. "
           "Доля = в скольких рассказах встречается это значение. "
           "«ИИ (разброс)» = от самой сдержанной модели до самой выраженной.", "",
           "↑ ИИ = у машин чаще (это слоп, убирать). ↓ ИИ = у людей чаще (это добавлять).", ""]
    for dim, g in top.groupby("dim", sort=False):
        out += [f"## {DIM_RU.get(dim, dim)}", "",
                "| | Признак | Значение | Люди | ИИ | ИИ (разброс) |",
                "|---|---|---|---|---|---|"]
        for _, x in g.iterrows():
            arrow = "↑ ИИ" if x["diff"] > 0 else "↓ ИИ"
            out.append(f"| {arrow} | {x['name']} | `{x['value']}` | {pct(x.human)} | "
                       f"{pct(x.ai)} | {pct(x.ai_min)}–{pct(x.ai_max)} |")
        out.append("")
    return "\n".join(out)


def fingerprints_md(r, n=10):
    names = {"gpt": "GPT-5.4", "claude": "Claude Sonnet 4.6", "gemini": "Gemini 3 Flash",
             "deepseek": "DeepSeek V3.2", "kimi": "Kimi K2.5"}
    out = ["# Отпечатки отдельных моделей", "",
           "Значения признаков, где модель сильнее всего отличается от остальных четырёх ИИ "
           "и при этом дальше от людей. Полезно, если известно, какой моделью написан текст.", ""]
    for s in SOURCES:
        others = [o for o in SOURCES if o != s]
        d = r[s] - r[others].mean(axis=1)
        top = r[(d > 0) & (r[s] > r.human)].assign(d=d).sort_values("d", ascending=False).head(n)
        out += [f"## {names[s]}", "", f"| Признак | Значение | {names[s]} | Другие ИИ | Люди |",
                "|---|---|---|---|---|"]
        for _, x in top.iterrows():
            out.append(f"| {x['name']} | `{x['value']}` | {pct(x[s])} | "
                       f"{pct(x[others].mean())} | {pct(x.human)} |")
        out.append("")
    return "\n".join(out)


if __name__ == "__main__":
    root, dest = Path(sys.argv[1]), Path(sys.argv[2])
    meta, df = load(root)
    r = value_shares(meta, df)
    (dest / "narrative-tells.md").write_text(tells_md(r))
    (dest / "model-fingerprints.md").write_text(fingerprints_md(r))
    print("ok:", len(r), "значений,", int(r.consistent.sum()), "согласованных")
