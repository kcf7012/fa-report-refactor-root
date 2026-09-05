#!/usr/bin/env python3
"""Markdown 相對連結檢查 —— 抓出指向不存在檔案的連結。

## 為什麼需要這支

`docs/handoff/` 底下的交接文件彼此大量交叉引用,而檔名很長又含日期,
打錯一個字連結就死掉,而且**看起來完全正常** —— Markdown 不會告訴你
連結是壞的,要有人真的去點才會發現。

驗收頁 `docs/handoff/screenshots/v3.1.4-visual-review/index.html` 就是
活生生的例子:它引用 3 位數的 `slide-001.png`,磁碟上卻是 2 位數的
`slide-01.png` —— 這頁在任何機器上從來沒有正常顯示過,兩輪稽核才發現。

## 檢查什麼

只檢查**相對連結**(`[文字](相對路徑)`),因為只有那些能在本地驗證:

- 略過 `http://`、`https://`、`mailto:`、純錨點 `#section`
- 路徑帶錨點時(`docs/x.md#section`)只驗檔案存在
- 略過程式碼區塊內的內容(``` 圍起來的),那些常是範例而非真連結

## 用法

    python3 scripts/check_markdown_links.py           # 檢查全部追蹤的 .md
    python3 scripts/check_markdown_links.py docs/     # 只檢查某個目錄
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote

# [文字](目標) —— 目標不含空白與右括號
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")

SKIP_PREFIXES = ("http://", "https://", "mailto:", "#", "tel:", "data:")

FENCE_RE = re.compile(r"^\s*(```|~~~)")


def _tracked_markdown(roots: list[str]) -> list[Path]:
    out = subprocess.run(
        ["git", "ls-files", "*.md", *roots],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    return [Path(line) for line in out.splitlines() if line]


def _links_outside_code_fences(text: str):
    """逐行掃連結,跳過 ``` 圍起來的程式碼區塊。"""
    in_fence = False
    for lineno, line in enumerate(text.splitlines(), 1):
        if FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        for match in LINK_RE.finditer(line):
            yield lineno, match.group(1)


def main() -> int:
    roots = sys.argv[1:]
    broken: list[str] = []
    checked = 0

    for md in _tracked_markdown(roots):
        try:
            text = md.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue

        for lineno, target in _links_outside_code_fences(text):
            if target.startswith(SKIP_PREFIXES):
                continue
            # 去掉錨點,只驗檔案本身
            path_part = unquote(target.split("#", 1)[0])
            if not path_part:
                continue
            resolved = (md.parent / path_part).resolve()
            checked += 1
            if not resolved.exists():
                broken.append(f"  {md}:{lineno}\n    → {target}")

    if broken:
        print(f"✗ Markdown 連結檢查:{len(broken)} 個壞連結\n", file=sys.stderr)
        for item in broken:
            print(item, file=sys.stderr)
        return 1

    print(f"✓ Markdown 連結檢查:{checked} 個相對連結全部有效")
    return 0


if __name__ == "__main__":
    sys.exit(main())
