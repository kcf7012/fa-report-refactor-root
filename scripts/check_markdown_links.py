#!/usr/bin/env python3
"""Markdown / HTML 相對連結檢查 —— 抓出指向不存在檔案的連結。

## 為什麼需要這支

`docs/handoff/` 底下的交接文件彼此大量交叉引用,而檔名很長又含日期,
打錯一個字連結就死掉,而且**看起來完全正常** —— Markdown 不會告訴你
連結是壞的,要有人真的去點才會發現。

驗收頁 `docs/handoff/screenshots/v3.1.4-visual-review/index.html` 就是
活生生的例子:它引用 3 位數的 `slide-001.png`,磁碟上卻是 2 位數的
`slide-01.png` —— 這頁在任何機器上從來沒有正常顯示過,兩輪稽核才發現。
v3.1.5(柔伊第七輪查證 B2 延伸)指出本工具當時**只查 `.md`,不查 `.html`**,
同一類問題下次仍抓不到 —— 因此擴充到也檢查 HTML 的 `<img src>` / `<a href>`。

## 檢查什麼

只檢查**相對連結**(能在本地驗證的那種):

- Markdown:`[文字](相對路徑)`
- HTML:`<img src="...">`、`<a href="...">`
- 兩者都略過 `http(s)://`、`mailto:`、`tel:`、`data:`、純錨點 `#section`
- 路徑帶錨點時(`docs/x.md#section`)只驗檔案存在
- Markdown 略過程式碼區塊內的內容(``` 圍起來的),那些常是範例而非真連結

## 絕對路徑不在檢查範圍內

本工具只驗證**相對連結的可攜性**,絕對路徑一律跳過不查
(理由見「檢查什麼」)。`docs/handoff/screenshots/` 底下兩份既有的驗收頁
現在就是壞的(寫死開發者本機的絕對路徑,且引用的 PNG 被 `.gitignore` 排除),
但因為是絕對路徑,本來就不會被本工具評估 —— **不是靠特殊豁免放行,
是本來就超出這支工具要管的範圍**。那兩份頁面的修復(重新壓縮 109 張圖、
改純相對路徑、修 zero-padding)是計劃書 P5 的工作。P5 把它們改成相對路徑
之後,本工具會自動開始驗證,不需要額外動作。

## 用法

    python3 scripts/check_markdown_links.py           # 檢查全部追蹤的 .md / .html
    python3 scripts/check_markdown_links.py docs/     # 只檢查某個目錄
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote

# Markdown:[文字](目標) —— 目標不含空白與右括號
MD_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")

# HTML:<img src="..."> 或 <a href="...">(單引號雙引號都收)
HTML_LINK_RE = re.compile(
    r'<(?:img|a)\b[^>]*\b(?:src|href)=["\']([^"\']+)["\']', re.IGNORECASE
)

SKIP_PREFIXES = ("http://", "https://", "mailto:", "#", "tel:", "data:")

FENCE_RE = re.compile(r"^\s*(```|~~~)")


def _tracked_files(pattern: str, roots: list[str]) -> list[Path]:
    out = subprocess.run(
        ["git", "ls-files", pattern, *roots],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    return [Path(line) for line in out.splitlines() if line]


def _md_links_outside_code_fences(text: str):
    """逐行掃 Markdown 連結,跳過 ``` 圍起來的程式碼區塊。"""
    in_fence = False
    for lineno, line in enumerate(text.splitlines(), 1):
        if FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        for match in MD_LINK_RE.finditer(line):
            yield lineno, match.group(1)


def _html_links(text: str):
    """逐行掃 HTML 的 img/a 連結。"""
    for lineno, line in enumerate(text.splitlines(), 1):
        for match in HTML_LINK_RE.finditer(line):
            yield lineno, match.group(1)


def _check_file(path: Path, links) -> tuple[int, list[str]]:
    checked = 0
    broken = []
    for lineno, target in links:
        if target.startswith(SKIP_PREFIXES):
            continue
        path_part = unquote(target.split("#", 1)[0])
        if not path_part or path_part.startswith("/"):
            # 絕對路徑不是「相對連結」,本工具只驗證相對連結的可攜性
            continue
        resolved = (path.parent / path_part).resolve()
        checked += 1
        if not resolved.exists():
            broken.append(f"  {path}:{lineno}\n    → {target}")
    return checked, broken


def main() -> int:
    roots = sys.argv[1:]
    broken: list[str] = []
    checked = 0

    for md in _tracked_files("*.md", roots):
        try:
            text = md.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        c, b = _check_file(md, _md_links_outside_code_fences(text))
        checked += c
        broken.extend(b)

    for html in _tracked_files("*.html", roots):
        try:
            text = html.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        c, b = _check_file(html, _html_links(text))
        checked += c
        broken.extend(b)

    if broken:
        print(f"✗ 連結檢查:{len(broken)} 個壞連結\n", file=sys.stderr)
        for item in broken:
            print(item, file=sys.stderr)
        return 1

    print(f"✓ 連結檢查:{checked} 個相對連結全部有效")
    return 0


if __name__ == "__main__":
    sys.exit(main())
