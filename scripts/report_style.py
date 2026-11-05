# -*- coding: utf-8 -*-
"""Shared CSS for group daily-report pages (detail + index)."""

CSS = """
  :root {
    --green: #07c160;
    --green-dark: #059048;
    --green-light: #e8f8ef;
    --ink: #1a1d23;
    --ink-2: #5a6472;
    --ink-3: #9aa3b0;
    --bg: #f4f6f8;
    --card: #ffffff;
    --line: #e8ebef;
    --orange: #ff8f1f;
    --blue: #4a7dff;
    --purple: #8f6bff;
    --red: #ff5b5b;
    --gold: #c9a24b;
    --radius: 16px;
  }
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    font-family: -apple-system, "PingFang SC", "Microsoft YaHei", "Segoe UI", sans-serif;
    background: var(--bg);
    color: var(--ink);
    line-height: 1.6;
    font-size: 15px;
  }
  .wrap { max-width: 980px; margin: 0 auto; padding: 24px 16px 60px; }

  /* Header */
  header {
    background: linear-gradient(135deg, #07c160 0%, #059048 60%, #04753a 100%);
    border-radius: var(--radius);
    color: #fff;
    padding: 32px 28px;
    margin-bottom: 20px;
    position: relative;
    overflow: hidden;
  }
  header::after {
    content: "";
    position: absolute; right: -60px; top: -60px;
    width: 220px; height: 220px; border-radius: 50%;
    background: rgba(255,255,255,.08);
  }
  header::before {
    content: "";
    position: absolute; right: 40px; bottom: -90px;
    width: 180px; height: 180px; border-radius: 50%;
    background: rgba(255,255,255,.06);
  }
  header .tag {
    display: inline-block; font-size: 12px; letter-spacing: 2px;
    background: rgba(255,255,255,.2); padding: 4px 12px; border-radius: 999px;
    margin-bottom: 12px;
  }
  header h1 { font-size: 26px; font-weight: 700; }
  header .sub { font-size: 15px; opacity: .85; margin-top: 6px; }

  /* KPI */
  .kpis { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 20px; }
  .kpi {
    background: var(--card); border-radius: var(--radius);
    padding: 18px 16px; box-shadow: 0 1px 3px rgba(0,0,0,.04);
    border: 1px solid var(--line);
  }
  .kpi .num { font-size: 30px; font-weight: 800; color: var(--green-dark); }
  .kpi .num small { font-size: 15px; font-weight: 500; color: var(--ink-3); margin-left: 2px; }
  .kpi .label { font-size: 14px; color: var(--ink-2); margin-top: 2px; }
  .kpi .hint { font-size: 13px; color: var(--ink-3); margin-top: 4px; }
  .kpi.peak .num { color: var(--orange); }
  .kpi.star .num { color: var(--purple); }

  /* Cards */
  .card {
    background: var(--card); border-radius: var(--radius);
    border: 1px solid var(--line);
    box-shadow: 0 1px 3px rgba(0,0,0,.04);
    padding: 22px; margin-bottom: 20px;
  }
  .card h2 {
    font-size: 17px; font-weight: 700; margin-bottom: 16px;
    display: flex; align-items: center; gap: 8px;
  }
  .card h2 .dot { width: 8px; height: 8px; border-radius: 50%; background: var(--green); }
  .card h2 .right { margin-left: auto; font-size: 12px; color: var(--ink-3); font-weight: 400; }

  /* Hour chart */
  .hour-chart { display: flex; align-items: flex-end; gap: 4px; height: 160px; padding-top: 8px; }
  .hour-col { flex: 1; display: flex; flex-direction: column; align-items: center; gap: 6px; height: 100%; justify-content: flex-end; }
  .hour-bar {
    width: 100%; max-width: 34px; border-radius: 6px 6px 2px 2px;
    background: linear-gradient(180deg, #2bd47e, #07c160);
    position: relative; transition: .2s;
    min-height: 3px;
  }
  .hour-bar.peak { background: linear-gradient(180deg, #ffb45e, #ff8f1f); }
  .hour-bar:hover { filter: brightness(1.1); }
  .hour-bar .tip {
    position: absolute; bottom: calc(100% + 6px); left: 50%; transform: translateX(-50%);
    background: var(--ink); color: #fff; font-size: 12px; padding: 3px 8px;
    border-radius: 6px; white-space: nowrap; opacity: 0; pointer-events: none; transition: .15s;
  }
  .hour-bar:hover .tip { opacity: 1; }
  .hour-x { font-size: 12px; color: var(--ink-3); }

  /* Speakers */
  .speaker-row { display: flex; align-items: center; gap: 10px; margin-bottom: 12px; }
  .speaker-row .rank {
    width: 22px; height: 22px; border-radius: 6px; font-size: 12px; font-weight: 700;
    display: flex; align-items: center; justify-content: center;
    background: var(--bg); color: var(--ink-3); flex-shrink: 0;
  }
  .speaker-row:nth-child(1) .rank { background: #fff3e0; color: var(--orange); }
  .speaker-row:nth-child(2) .rank { background: #eceff1; color: #607d8b; }
  .speaker-row:nth-child(3) .rank { background: #fdeee0; color: #c97a3d; }
  .speaker-row .name { font-size: 14px; width: 150px; flex-shrink: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .speaker-row .bar-wrap { flex: 1; background: var(--bg); border-radius: 999px; height: 14px; overflow: hidden; }
  .speaker-row .bar { height: 100%; border-radius: 999px; background: linear-gradient(90deg, #2bd47e, #07c160); }
  .speaker-row.host .bar { background: linear-gradient(90deg, #b39dff, #8f6bff); }
  .speaker-row .count { font-size: 13px; color: var(--ink-2); width: 56px; text-align: right; flex-shrink: 0; }
  .legend { display: flex; gap: 16px; font-size: 13px; color: var(--ink-2); margin-top: 8px; }
  .legend i { display: inline-block; width: 10px; height: 10px; border-radius: 3px; margin-right: 4px; }

  /* Donut */
  .type-flex { display: flex; align-items: center; gap: 24px; flex-wrap: wrap; }
  .donut { position: relative; width: 150px; height: 150px; flex-shrink: 0; }
  .donut .center { position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; }
  .donut .center b { font-size: 22px; }
  .donut .center span { font-size: 12px; color: var(--ink-3); }
  .type-list { flex: 1; min-width: 200px; }
  .type-item { display: flex; align-items: center; gap: 8px; font-size: 14px; margin-bottom: 8px; }
  .type-item i { width: 10px; height: 10px; border-radius: 3px; flex-shrink: 0; }
  .type-item .t-count { margin-left: auto; color: var(--ink-2); font-variant-numeric: tabular-nums; }

  /* Timeline */
  .timeline { position: relative; padding-left: 22px; }
  .timeline::before {
    content: ""; position: absolute; left: 5px; top: 6px; bottom: 6px;
    width: 2px; background: var(--line);
  }
  .tl-item { position: relative; margin-bottom: 18px; }
  .tl-item::before {
    content: ""; position: absolute; left: -22px; top: 5px;
    width: 12px; height: 12px; border-radius: 50%;
    background: var(--card); border: 3px solid var(--green);
  }
  .tl-item.gold::before { border-color: var(--orange); }
  .tl-item .tl-time { font-size: 13px; color: var(--ink-3); }
  .tl-item .tl-title { font-size: 16px; font-weight: 700; margin: 2px 0; }
  .tl-item .tl-desc { font-size: 14px; color: var(--ink-2); }

  /* Image digest */
  .img-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 14px; }
  .img-cell { background: #fafafa; border: 1px solid #eee; border-radius: 12px; padding: 8px; }
  .img-frame { height: 150px; display: flex; align-items: center; justify-content: center; overflow: hidden; border-radius: 8px; background: #fff; }
  .img-frame img { max-width: 100%; max-height: 150px; object-fit: contain; }
  .img-meta { display: flex; justify-content: space-between; margin-top: 6px; font-size: 12px; color: var(--ink-3); }
  .img-sender { color: var(--green); font-weight: 600; }
  .img-cap { font-size: 13px; color: var(--ink-2); margin-top: 3px; line-height: 1.45; }

  /* Media digest (text-only) */
  .media-list { display: flex; flex-direction: column; gap: 10px; }
  .ml-line { background: #fafafa; border: 1px solid #eee; border-radius: 10px; padding: 10px 14px; font-size: 14px; color: var(--ink-2); line-height: 1.6; }
  .ml-line.ml-hl { background: var(--green-light); border-color: var(--green); color: var(--ink-1); font-weight: 600; }

  /* Highlights */
  .hl {
    border-left: 4px solid var(--green);
    background: var(--green-light);
    border-radius: 0 12px 12px 0;
    padding: 16px 18px; margin-bottom: 16px;
  }
  .hl.orange { border-color: var(--orange); background: #fff6ec; }
  .hl.purple { border-color: var(--purple); background: #f4f0ff; }
  .hl.blue { border-color: var(--blue); background: #eef4ff; }
  .hl.gold { border-color: var(--gold); background: #fdf8ec; }
  .hl .hl-tag {
    display: inline-block; font-size: 12px; font-weight: 700; color: #fff;
    background: var(--green); border-radius: 4px; padding: 2px 8px; margin-bottom: 8px;
  }
  .hl.orange .hl-tag { background: var(--orange); }
  .hl.purple .hl-tag { background: var(--purple); }
  .hl.blue .hl-tag { background: var(--blue); }
  .hl.gold .hl-tag { background: var(--gold); }
  .hl h3 { font-size: 16px; margin-bottom: 8px; }
  .hl p, .hl li { font-size: 15px; color: var(--ink-2); }
  .hl ul { padding-left: 18px; margin-top: 6px; }
  .hl .quote {
    margin-top: 10px; font-size: 14px; color: var(--ink);
    background: rgba(255,255,255,.75); border-radius: 8px; padding: 10px 14px;
    font-style: italic;
  }
  .quote-words { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 10px; }
  .quote-words span {
    font-size: 13.5px; background: rgba(255,255,255,.85); color: var(--ink);
    padding: 5px 12px; border-radius: 999px; border: 1px solid var(--line);
  }

  /* Index page (multi-group summary) */
  .group-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; }
  .group-card {
    display: block; text-decoration: none; color: inherit;
    background: var(--card); border: 1px solid var(--line);
    border-radius: var(--radius); padding: 20px;
    box-shadow: 0 1px 3px rgba(0,0,0,.04);
    transition: transform .15s, box-shadow .15s;
  }
  .group-card:hover { transform: translateY(-2px); box-shadow: 0 6px 16px rgba(0,0,0,.08); }
  .group-card .gc-name { font-size: 18px; font-weight: 700; margin-bottom: 2px; }
  .group-card .gc-range { font-size: 13px; color: var(--ink-3); margin-bottom: 12px; }
  .gc-stats { display: flex; gap: 8px; margin-bottom: 12px; flex-wrap: wrap; }
  .gc-stat {
    flex: 1; min-width: 72px; background: var(--bg); border-radius: 10px;
    padding: 8px 10px; text-align: center;
  }
  .gc-stat b { display: block; font-size: 18px; color: var(--green-dark); }
  .gc-stat span { font-size: 12px; color: var(--ink-3); }
  .group-card .gc-hl-title { font-size: 13px; color: var(--ink-3); margin-bottom: 4px; }
  .group-card .gc-hl { font-size: 14px; color: var(--ink-2); padding: 2px 0 2px 14px; position: relative; }
  .group-card .gc-hl::before {
    content: ""; position: absolute; left: 2px; top: 9px;
    width: 6px; height: 6px; border-radius: 50%; background: var(--green);
  }
  .group-card .gc-open {
    margin-top: 12px; font-size: 14px; font-weight: 700; color: var(--green-dark);
  }

  footer { text-align: center; font-size: 13px; color: var(--ink-3); margin-top: 24px; }

  /* Mobile: bigger fonts and roomier layout for phone reading */
  @media (max-width: 640px) {
    body { font-size: 16px; }
    .wrap { padding: 14px 10px 40px; }
    header { padding: 24px 18px; }
    header h1 { font-size: 22px; }
    header .sub { font-size: 14px; }
    header .tag { font-size: 11px; }
    .kpis { grid-template-columns: repeat(2, 1fr); gap: 10px; }
    .kpi { padding: 14px 12px; }
    .kpi .num { font-size: 25px; }
    .kpi .num small { font-size: 13px; }
    .kpi .label { font-size: 13px; }
    .kpi .hint { font-size: 12px; }
    .card { padding: 16px 14px; }
    .card h2 { font-size: 16px; }
    .card h2 .right { display: none; }
    .hour-chart { height: 130px; gap: 2px; }
    .hour-x { font-size: 9px; }
    .speaker-row .name { font-size: 13px; width: 92px; }
    .speaker-row .count { font-size: 12px; width: 48px; }
    .legend { font-size: 12px; }
    .type-item { font-size: 14px; }
    .tl-item .tl-time { font-size: 12px; }
    .tl-item .tl-title { font-size: 15px; }
    .tl-item .tl-desc { font-size: 14px; }
    .hl { padding: 14px; }
    .hl h3 { font-size: 15.5px; }
    .hl p, .hl li { font-size: 14.5px; }
    .hl .quote { font-size: 14px; }
    .quote-words span { font-size: 13px; }
    .group-grid { grid-template-columns: 1fr; }
    .group-card .gc-name { font-size: 17px; }
    .group-card .gc-hl { font-size: 14px; }
    footer { font-size: 12px; }
  }
"""
