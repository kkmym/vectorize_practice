#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
data/rds_results_MIXED_20250913.json を読み込み、各求人に content.summary を追記します。

summary には以下を含めます：
- 必須/歓迎スキル（requirementsの抽出）
- 取り組む業務内容（descriptionの箇条書き抽出）
- 会社・部署の事業内容要約（company_features または description 冒頭から要約）

実行:
  python -m src.01_PoC.03_summarize_mixed_data [--input data/rds_results_MIXED_20250913.json]

デフォルトでは同一ファイルを書き換えます（BOMなし, UTF-8, indent=4）。
書き換え前に .bak を作成します。
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
from typing import Any, Dict, List, Optional, Tuple


INPUT_DEFAULT = os.path.join("data", "rds_results_MIXED_20250913.json")


def normalize_text(s: str) -> str:
    # Collapse whitespace and full-width spaces, trim
    s = s.replace("\u3000", " ")
    s = re.sub(r"[\t\r\f]+", " ", s)
    s = re.sub(r" +", " ", s)
    s = re.sub(r"\n{2,}", "\n", s)
    return s.strip()


def split_sentences(text: str) -> List[str]:
    # Simple split by '。' while keeping concise sentences
    text = normalize_text(text)
    # Replace some bullets with line breaks to help splitting
    text = re.sub(r"\s*[・\-•]\s*", "\n・", text)
    text = text.replace("▼", "\n・").replace("■", "\n・").replace("◆", "\n・")
    parts: List[str] = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        # If bullet-like, keep as-is; otherwise split by 。
        if line.startswith("・") or line.startswith("-"):
            parts.append(line.lstrip("・- "))
            continue
        for seg in re.split("。", line):
            seg = seg.strip()
            if seg:
                parts.append(seg)
    return parts


def extract_bullets(text: str, max_items: int = 8) -> List[str]:
    if not text:
        return []
    lines = []
    # Prefer explicit bullets
    for line in text.splitlines():
        if re.match(r"^\s*[・\-–—]", line):
            lines.append(normalize_text(re.sub(r"^\s*[・\-–—]\s*", "", line)))
    # Fallback: take sentences that contain verbs or look like tasks
    if not lines:
        for s in split_sentences(text):
            if len(s) < 6:
                continue
            if re.search(r"(開発|設計|実装|運用|推進|改善|構築|分析|設計|要件|連携|最適化|評価|検証|構成)", s):
                lines.append(s)
    # Deduplicate while preserving order
    seen = set()
    uniq: List[str] = []
    for l in lines:
        if l not in seen:
            seen.add(l)
            uniq.append(l)
    return uniq[:max_items]


def extract_requirements(req: Optional[str]) -> Tuple[List[str], List[str]]:
    if not req:
        return [], []
    text = normalize_text(req)

    # Identify MUST and WANT sections
    # Patterns for headers
    must_headers = [
        r"【?必須（?MUST）?】?",
        r"必須（?MUST）?",
        r"MUST",
    ]
    want_headers = [
        r"【?歓迎（?WANT）?】?",
        r"歓迎（?WANT）?",
        r"WANT",
        r"あると望ましい",
    ]

    def find_section(h_patterns: List[str]) -> Optional[re.Match]:
        for p in h_patterns:
            m = re.search(p, text)
            if m:
                return m
        return None

    m_must = find_section(must_headers)
    m_want = find_section(want_headers)

    def section_text(start: Optional[int], end: Optional[int]) -> str:
        s = start if start is not None else 0
        e = end if end is not None else len(text)
        return text[s:e]

    must_text = ""
    want_text = ""
    if m_must and m_want:
        if m_must.start() < m_want.start():
            must_text = section_text(m_must.end(), m_want.start())
            want_text = section_text(m_want.end(), None)
        else:
            want_text = section_text(m_want.end(), m_must.start())
            must_text = section_text(m_must.end(), None)
    elif m_must:
        must_text = section_text(m_must.end(), None)
    elif m_want:
        want_text = section_text(m_want.end(), None)
    else:
        must_text = text

    def bullets(t: str, cap: int) -> List[str]:
        items = []
        for line in t.splitlines():
            if re.match(r"^\s*[・\-–—]", line):
                items.append(normalize_text(re.sub(r"^\s*[・\-–—]\s*", "", line)))
        if not items:
            # Fallback: split sentences and pick skill-like
            for s in split_sentences(t):
                if len(s) < 6:
                    continue
                if re.search(r"(経験|知識|理解|能力|スキル|開発|運用|設計|英語|マネジメント|実装|クラウド|AWS|GCP|Python|Go|Java|React|SQL|RDBMS|Docker|Kubernetes|Terraform|Datadog|Elasticsearch)", s):
                    items.append(s)
        # Deduplicate
        seen = set()
        uniq = []
        for it in items:
            if it not in seen:
                seen.add(it)
                uniq.append(it)
        return uniq[:cap]

    must = bullets(must_text, 10)
    want = bullets(want_text, 10)
    return must, want


def company_summary(company_features: Optional[str], description: Optional[str], max_chars: int = 120) -> str:
    if company_features:
        s = normalize_text(company_features)
    else:
        s = normalize_text(description or "")
    # Take the first 1-2 sentences
    sentences = split_sentences(s)
    joined = "。".join(sentences[:2])
    if len(joined) > max_chars:
        joined = joined[: max_chars - 1] + "…"
    return joined


def truncate_by_chars(s: str, max_chars: int) -> str:
    if len(s) <= max_chars:
        return s
    return s[: max_chars - 1] + "…"


def join_compact(items: List[str], sep: str = "、", max_total_chars: int = 120) -> str:
    out: List[str] = []
    total = 0
    for it in items:
        it = normalize_text(it)
        if not it:
            continue
        add = (sep if out else "") + it
        if total + len(add) > max_total_chars and out:
            break
        out.append(it)
        total += len(add)
    return sep.join(out)


def build_summary(job: Dict[str, Any], max_chars: int = 300, include_company: bool = True) -> str:
    j = job.get("content", {}).get("job", {})
    comp = job.get("content", {}).get("company", {})
    title = j.get("title") or ""
    description = j.get("description") or ""
    requirements = j.get("requirements") or ""
    company_features = comp.get("company_features") if isinstance(comp, dict) else None

    must, want = extract_requirements(requirements)
    responsibilities = extract_bullets(description, max_items=6)
    comp_sum = company_summary(company_features, description, max_chars=100) if include_company else ""

    # Compose sections compactly
    parts: List[str] = []
    if responsibilities:
        works = join_compact(responsibilities[:4], max_total_chars=120)
        if works:
            parts.append(f"業務:{works}")
    if must:
        musts = join_compact(must[:3], max_total_chars=100)
        if musts:
            parts.append(f"必須:{musts}")
    if want:
        wants = join_compact(want[:2], max_total_chars=80)
        if wants:
            parts.append(f"歓迎:{wants}")
    if include_company and comp_sum:
        parts.append(f"会社:{comp_sum}")

    # Optionally include a very short title hint when space allows
    prefix = ""
    if title and len(title) <= 35:
        prefix = f"『{normalize_text(title)}』"

    text = (prefix + (" " if prefix else "") + " ".join(parts)).strip()
    return truncate_by_chars(text, max_chars)


def process_file(path: str, max_chars: int = 300, include_company: bool = True) -> Tuple[int, int]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    jobs = data.get("jobs", [])
    updated = 0
    total = len(jobs)
    for job in jobs:
        summary = build_summary(job, max_chars=max_chars, include_company=include_company)
        job.setdefault("content", {})["summary"] = summary
        updated += 1

    # Backup
    backup_path = path + ".bak"
    shutil.copy2(path, backup_path)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    return updated, total


def main():
    parser = argparse.ArgumentParser(description="Append summarized fields to MIXED jobs JSON.")
    parser.add_argument("--input", default=INPUT_DEFAULT, help="Input JSON path (will be updated in-place)")
    parser.add_argument("--max-chars", type=int, default=300, help="Max characters for compact summary (default: 300)")
    parser.add_argument("--exclude-company", action="store_true", help="Exclude company overview from summary")
    args = parser.parse_args()

    path = args.input
    if not os.path.exists(path):
        raise SystemExit(f"Input not found: {path}")

    updated, total = process_file(path, max_chars=args.max_chars, include_company=not args.exclude_company)
    print(f"Summaries appended: {updated}/{total} -> {path} (backup: {path}.bak)")


if __name__ == "__main__":
    main()
