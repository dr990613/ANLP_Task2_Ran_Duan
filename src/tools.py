# src/tools.py
from typing import List
from pathlib import Path
from datetime import datetime
import re

# 尝试导入 BeaconExtractor（假设你把上面的长代码放在 src/Beacon.py 里）
# 如果你的文件路径不同，可以把这一行改成 from Beacon import BeaconExtractor 等
try:
    from .Beacon import BeaconExtractor  # src/Beacon.py
except Exception:
    BeaconExtractor = None


# =========================
# 2. 笔记检索（保留）
# =========================

def search_notes(query: str, notes: List[str], max_results: int = 2) -> str:
    """
    在 notes 列表中根据 query 做最简单的关键词匹配检索。

    参数:
        query: 用户当前的查询文本
        notes: 预先存储的笔记列表，每个元素是一段文本
        max_results: 返回的最多匹配条目数量

    返回:
        连接后的匹配笔记字符串，如果没有匹配则返回空字符串。
    """
    q = query.lower().strip()
    if not q:
        return ""

    matched = []
    for note in notes:
        if q in note.lower():
            matched.append(note)
        if len(matched) >= max_results:
            break

    if not matched:
        return ""

    return "\n\n".join(matched)


# =========================
# 3. Beacon 推理工具
# =========================

def beacon_analyze_code(code: str,
                        max_per_func: int = 20,
                        mode: str = "compact") -> str:
    """
    对一段 Python 源码字符串执行 Beacon 推理，返回一个简要的文本总结。

    设计用途：
        - 由 coding_agent 在生成代码后调用
        - 不依赖文件路径，直接处理字符串（不同于 CLI 用法）
        - 返回一个可直接附加到回答后的 “Beacon summary” 文本

    如果 BeaconExtractor 无法导入，则返回提示信息。
    """
    if BeaconExtractor is None:
        return ("[Beacon] BeaconExtractor not available. "
                "Please check that `src/Beacon.py` exists and is importable.")

    try:
        extractor = BeaconExtractor(code)
        extractor.visit(extractor.tree)

        # 这里走 program-level beacons，和你 CLI 版本逻辑一致（但更简化）
        program_beacons = extractor.compute_program_beacons(
            max_per_func=max_per_func,
            mode=mode,
            explicit_entry=None,
        )

        lines: List[str] = []
        lines.append("### Beacon summary")
        lines.append("")
        lines.append("Program-level beacons (entry-driven):")

        for entry, nodes in program_beacons.items():
            reachable = extractor.reachable_functions_from(entry)
            reachable_str = ", ".join(sorted(reachable))
            lines.append(f"- Entry `{entry}` (reachable functions: {reachable_str})")

            for nid in nodes:
                lineno = extractor.node_lines.get(nid)
                func = extractor.node_func.get(nid, "<module>")
                code_line = extractor._safe_get_line(nid).strip()
                if not code_line:
                    continue
                lines.append(f"  - [{func}] line {lineno}: {code_line}")

        if len(lines) == 3:  # 没有任何 beacon
            lines.append("  (No significant beacons found for this code.)")

        return "\n".join(lines)

    except Exception as e:
        # 不让整个 Agent 崩掉，只返回一个错误说明
        return f"[Beacon] Error while analyzing code: {e}"


# =========================
# 4. Markdown 写作 / 保存工具
# =========================

def format_as_markdown(title: str, content: str) -> str:
    """
    将一段理论解释包装成标准 Markdown 文本。
    设计用途：
        - Theory Agent 可以先生成内容，再用这个函数转换为 markdown 结构。
    """
    title = title.strip() or "Notes"
    md = f"# {title}\n\n{content.strip()}\n"
    return md


def save_markdown_note(title: str,
                       content: str,
                       base_dir: str = "notes") -> str:
    """
    将内容保存为一个 .md 文件，并返回文件路径（字符串）。

    设计用途：
        - Theory Agent 在回答结束后，可以将该回答保存为一份本地 Markdown 笔记。
        - 方便你后续整理课程笔记 / 理论解释。

    参数:
        title: 笔记标题，会用于生成文件名
        content: 纯文本或已是 markdown 的内容
        base_dir: 相对于项目根目录的保存目录，例如 "notes"

    返回:
        保存的 markdown 文件的绝对路径（字符串）
    """
    # 生成安全的文件名
    safe_title = re.sub(r"[^a-zA-Z0-9_-]+", "_", title).strip("_")
    if not safe_title:
        safe_title = "note"

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{safe_title}_{timestamp}.md"

    # 项目根目录：src 的上一级
    project_root = Path(__file__).resolve().parents[1]
    notes_dir = project_root / base_dir
    notes_dir.mkdir(parents=True, exist_ok=True)

    path = notes_dir / filename

    # 包装成 markdown
    md_text = format_as_markdown(title, content)

    path.write_text(md_text, encoding="utf-8")
    return str(path)
