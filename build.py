#!/usr/bin/env python3
"""
build.py — 从 data.json + templates 生成 Sprint Dashboard HTML 页面
用法: python3 build.py [--data data.json] [--outdir .]
"""

import json
import argparse
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

ROOT = Path(__file__).parent
TEMPLATES_DIR = ROOT / "templates"
DEFAULT_DATA = ROOT / "data.json"


def load_css():
    css_path = TEMPLATES_DIR / "base.css"
    return css_path.read_text()


def build(data_path: Path, outdir: Path):
    with open(data_path) as f:
        data = json.load(f)

    css = load_css()
    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))

    # Count stats
    all_tasks = []
    for u in data["users"]:
        all_tasks.extend(u["tasks"])
    all_tasks.extend(data.get("backlog", []))

    urgent_count = sum(1 for t in all_tasks if t.get("priority") == "urgent")
    twoweek_count = sum(1 for t in all_tasks if t.get("priority") == "normal")
    total_count = len(all_tasks)

    # Build project lookup
    project_map = {p["name"]: p for p in data["projects"]}

    # Render index.html
    index_tpl = env.get_template("index.html")
    index_html = index_tpl.render(
        css=css,
        enumerate=enumerate,
        **data,
        urgent_count=urgent_count,
        twoweek_count=twoweek_count,
        total_count=total_count,
    )
    (outdir / "index.html").write_text(index_html)
    print(f"✓ index.html")

    # Render user pages
    user_tpl = env.get_template("user.html")
    for user in data["users"]:
        project = project_map.get(user.get("project")) if user.get("project") else None
        user_html = user_tpl.render(
            css=css,
            enumerate=enumerate,
            user=user,
            project=project,
            sprint=data["sprint"],
            week=data["week"],
        )
        out_path = outdir / f"{user['id']}.html"
        out_path.write_text(user_html)
        print(f"✓ {user['id']}.html")

    print(f"\nDone! {1 + len(data['users'])} pages generated.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build Sprint Dashboard")
    parser.add_argument("--data", "-d", default=str(DEFAULT_DATA))
    parser.add_argument("--outdir", "-o", default=str(ROOT))
    args = parser.parse_args()

    build(Path(args.data), Path(args.outdir))
