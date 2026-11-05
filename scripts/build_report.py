# -*- coding: utf-8 -*-
"""Build a WeChat group daily-report HTML page from a JSON spec.

Usage:
    python build_report.py <spec.json> <output.html>

The spec JSON contains all report data; this script only handles
rendering (charts, donut, KPI cards) so the caller focuses on content.
"""
import json
import sys
import html
import datetime

from report_style import CSS

PALETTE = ["#07c160", "#4a7dff", "#ff8f1f", "#8f6bff", "#ff5b5b",
           "#c9a24b", "#5ac8a0", "#c9d1d9"]

WEEKDAYS_CN = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]


def esc(text):
    """Escape text for safe HTML insertion."""
    return html.escape(str(text), quote=True)


def build_kpis(kpis):
    """Render the four KPI cards."""
    parts = []
    for k in kpis:
        variant = k.get("variant", "")
        cls = ("kpi " + variant).strip()
        unit = k.get("unit", "")
        unit_html = '<small>%s</small>' % esc(unit) if unit else ""
        parts.append(
            '<div class="%s">\n'
            '      <div class="num">%s%s</div>\n'
            '      <div class="label">%s</div>\n'
            '      <div class="hint">%s</div>\n'
            "    </div>"
            % (cls, esc(k.get("num", "")), unit_html,
               esc(k.get("label", "")), esc(k.get("hint", "")))
        )
    return "\n    ".join(parts)


def build_hours(hours):
    """Render the 24-hour bar chart; peak hour gets the orange accent."""
    counts = [int(hours.get("%02d" % h, 0)) for h in range(24)]
    max_v = max(counts) if counts else 0
    cols = []
    for h, v in enumerate(counts):
        pct = (v / max_v * 100) if max_v else 0
        peak_cls = " peak" if (max_v and v == max_v) else ""
        height = max(pct, 2) if v else 2
        cols.append(
            '<div class="hour-col">\n'
            '      <div class="hour-bar%s" style="height:%.1f%%">\n'
            '        <span class="tip">%02d:00 · %d 条</span></div>\n'
            '      <div class="hour-x">%02d</div>\n'
            "    </div>" % (peak_cls, height, h, v, h)
        )
    return "\n    ".join(cols)


def build_speakers(speakers, host_names):
    """Render the speaker ranking rows; hosts get the purple bar."""
    max_c = max((int(c) for _, c in speakers), default=1)
    rows = []
    for i, (name, count) in enumerate(speakers):
        host_cls = " host" if name in host_names else ""
        width = int(count) / max_c * 100
        rows.append(
            '<div class="speaker-row%s">\n'
            '      <div class="rank">%d</div>\n'
            '      <div class="name" title="%s">%s</div>\n'
            '      <div class="bar-wrap"><div class="bar" style="width:%.1f%%"></div></div>\n'
            '      <div class="count">%d 条</div>\n'
            "    </div>"
            % (host_cls, i + 1, esc(name), esc(name), width, int(count))
        )
    return "\n    ".join(rows)


def build_donut(types, total, center_label):
    """Render the SVG donut chart; colors come from the palette in order."""
    circles = []
    cumulative = 0.0
    for i, (name, count) in enumerate(types):
        pct = count / total * 100 if total else 0
        color = PALETTE[i % len(PALETTE)]
        circles.append(
            '<circle cx="21" cy="21" r="15.9" fill="none" stroke="%s" '
            'stroke-width="6" stroke-dasharray="%.2f %.2f" '
            'stroke-dashoffset="%.2f" opacity=".88"></circle>'
            % (color, pct, 100 - pct, 25 - cumulative)
        )
        cumulative += pct
    center_pct = 0.0
    for name, count in types:
        if name == center_label:
            center_pct = count / total * 100 if total else 0
    svg = "\n          ".join(circles)
    return (
        '<div class="donut">\n'
        "        <svg viewBox=\"0 0 42 42\" width=\"150\" height=\"150\">\n"
        "          %s\n"
        "        </svg>\n"
        '        <div class="center"><b>%d%%</b><span>%s</span></div>\n'
        "      </div>" % (svg, round(center_pct), esc(center_label))
    )


def build_type_list(types, total):
    """Render the legend list next to the donut."""
    items = []
    for i, (name, count) in enumerate(types):
        color = PALETTE[i % len(PALETTE)]
        pct = count / total * 100 if total else 0
        items.append(
            '<div class="type-item"><i style="background:%s"></i>%s\n'
            '      <span class="t-count">%d 条 · %.1f%%</span></div>'
            % (color, esc(name), int(count), pct)
        )
    return "\n      ".join(items)


def build_timeline(events):
    """Render the day timeline; gold marks the most important events."""
    items = []
    for ev in events:
        gold_cls = " gold" if ev.get("gold") else ""
        items.append(
            '<div class="tl-item%s">\n'
            '        <div class="tl-time">%s</div>\n'
            '        <div class="tl-title">%s</div>\n'
            '        <div class="tl-desc">%s</div>\n'
            "      </div>"
            % (gold_cls, esc(ev.get("time", "")),
               esc(ev.get("title", "")), esc(ev.get("desc", "")))
        )
    return "\n      ".join(items)


def build_images(images):
    """Render the image digest grid: decrypted chat images with captions."""
    cells = []
    for im in images:
        cells.append(
            '<div class="img-cell">\n'
            '        <div class="img-frame"><img src="%s" alt=""></div>\n'
            '        <div class="img-meta"><span class="img-time">%s</span>'
            '<span class="img-sender">%s</span></div>\n'
            '        <div class="img-cap">%s</div>\n'
            "      </div>"
            % (esc(im["src"]), esc(im.get("time", "")),
               esc(im.get("sender", "")), esc(im.get("caption", "")))
        )
    return "\n      ".join(cells)


def build_media_bullets(lines):
    """Render text-only media digest: one bullet per line (already HTML-safe str
    or dict with 'text' and optional 'hl' to highlight)."""
    out = []
    for ln in lines:
        if isinstance(ln, dict):
            cls = ' class="ml-hl"' if ln.get("hl") else ""
            out.append('<div class="ml-line%s">%s</div>' % (cls, ln["text"]))
        else:
            out.append('<div class="ml-line">%s</div>' % ln)
    return "\n      ".join(out)


def build_page(spec):
    """Assemble the full HTML page from the spec dict."""
    report_date = spec["report_date"]  # YYYY-MM-DD
    dt = datetime.date.fromisoformat(report_date)
    weekday = WEEKDAYS_CN[dt.weekday()]
    date_cn = "%s年%d月%d日（%s）" % (dt.year, dt.month, dt.day, weekday)

    types = spec["types"]
    total = sum(int(c) for _, c in types)

    return """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%(group)s · 群聊日报 %(date)s</title>
<style>%(css)s</style>
</head>
<body>
<div class="wrap">

  <header>
    <span class="tag">群聊日报 · DAILY REPORT</span>
    <h1>%(group)s</h1>
    <div class="sub">%(date_cn)s</div>
    <div class="sub">统计范围：%(range_label)s</div>
  </header>

  <div class="kpis">
    %(kpis)s
  </div>

  <div class="card">
    <h2><span class="dot"></span>24 小时活跃分布<span class="right">悬停查看每时段消息数</span></h2>
    <div class="hour-chart">
    %(hours)s
    </div>
  </div>

  <div class="card">
    <h2><span class="dot"></span>发言排行榜 TOP %(top_n)d<span class="right">紫色 = 群主 / 核心成员</span></h2>
    %(speakers)s
    <div class="legend">
      <span><i style="background:linear-gradient(90deg,#b39dff,#8f6bff)"></i>圈主/核心成员</span>
      <span><i style="background:linear-gradient(90deg,#2bd47e,#07c160)"></i>群友</span>
    </div>
  </div>

  <div class="card">
    <h2><span class="dot"></span>消息类型构成</h2>
    <div class="type-flex">
      %(donut)s
      <div class="type-list">
      %(type_list)s
      </div>
    </div>
  </div>

  <div class="card">
    <h2><span class="dot"></span>今日大事记</h2>
    <div class="timeline">
      %(timeline)s
    </div>
  </div>

  %(images_section)s

  %(media_section)s

  <div class="card">
    <h2><span class="dot"></span>今日精华内容</h2>

%(highlights)s
  </div>

  <footer>%(group)s日报 · 由 Claude 自动生成 · %(today)s · Generated by <a href="https://github.com/duxingzhe1979/wechat-group-daily-report" style="color:var(--ink-3);text-decoration:none;border-bottom:1px dotted var(--ink-3)">笃行者AI</a></footer>
</div>
</body>
</html>
""" % {
        "group": esc(spec["group_name"]),
        "date": report_date,
        "date_cn": date_cn,
        "range_label": esc(spec.get("range_label", "")),
        "css": CSS,
        "kpis": build_kpis(spec["kpis"]),
        "hours": build_hours(spec["hours"]),
        "top_n": len(spec["speakers"]),
        "speakers": build_speakers(spec["speakers"], spec.get("host_names", [])),
        "donut": build_donut(types, total, spec.get("center_label", types[0][0])),
        "type_list": build_type_list(types, total),
        "timeline": build_timeline(spec["timeline"]),
        "images_section": (
            '<div class="card">\n'
            '    <h2><span class="dot"></span>图片速览<span class="right">群内图片已自动解密识别</span></h2>\n'
            '    <div class="img-grid">\n      %s\n    </div>\n  </div>'
            % build_images(spec["images"])
            if spec.get("images") else ""
        ),
        "media_section": (
            '<div class="card">\n'
            '    <h2><span class="dot"></span>%s<span class="right">%s</span></h2>\n'
            '    <div class="media-list">\n      %s\n    </div>\n  </div>'
            % (esc(spec.get("media_title", "图片与多媒体速览")),
               esc(spec.get("media_note", "已自动识别转文字")),
               build_media_bullets(spec["media_lines"]))
            if spec.get("media_lines") else ""
        ),
        "highlights": spec["highlights_html"],
        "today": datetime.date.today().isoformat(),
    }


def main():
    if len(sys.argv) != 3:
        print("Usage: python build_report.py <spec.json> <output.html>")
        sys.exit(1)
    with open(sys.argv[1], "r", encoding="utf-8") as f:
        spec = json.load(f)
    page = build_page(spec)
    with open(sys.argv[2], "w", encoding="utf-8") as f:
        f.write(page)
    print("Report written to: %s" % sys.argv[2])


if __name__ == "__main__":
    main()
