import streamlit as st
import json
import glob
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(
    page_title="Local SLM Observatory",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;600;700&family=Syne:wght@400;700;800&display=swap');

html, body, [data-testid="stAppViewContainer"] {
  background-color: #050810 !important;
  color: #e2e8f0 !important;
  font-family: 'JetBrains Mono', monospace !important;
}
[data-testid="block-container"] { padding-top: 2rem !important; }
[data-testid="stMetricValue"] {
  font-family: 'Syne', sans-serif !important;
  font-size: 2rem !important;
  color: #00f5c4 !important;
}
[data-testid="stMetricLabel"] {
  font-size: 0.65rem !important;
  letter-spacing: 2px !important;
  text-transform: uppercase !important;
  color: #4a5568 !important;
}
[data-testid="metric-container"] {
  background: #0a0f1e !important;
  border: 1px solid #1a2444 !important;
  border-radius: 8px !important;
  padding: 16px !important;
}
footer { visibility: hidden; }
#MainMenu { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Load data ──────────────────────────────────────────────────────────────────
files = glob.glob("results/runs/*.json")
if not files:
    st.error("No benchmark results found. Run `python run_all.py` first.")
    st.stop()

with open(max(files)) as f:
    data = json.load(f)

df = pd.DataFrame(data)

MODEL_COLORS = {
    "phi3:mini": "#00f5c4",
    "llama3.2:3b": "#7b61ff",
    "mistral:7b-instruct-q4_K_M": "#ff6b6b",
}

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="display:flex;align-items:flex-start;justify-content:space-between;
            border-bottom:1px solid #1a2444;padding-bottom:20px;margin-bottom:28px">
  <div>
    <div style="display:inline-flex;align-items:center;gap:6px;
                background:rgba(0,245,196,0.08);border:1px solid rgba(0,245,196,0.2);
                border-radius:4px;padding:3px 10px;font-size:10px;color:#00f5c4;
                letter-spacing:2px;text-transform:uppercase;margin-bottom:8px">
      ● LIVE BENCHMARK
    </div>
    <h1 style="font-family:Syne,sans-serif;font-size:32px;font-weight:800;
               background:linear-gradient(135deg,#fff 0%,#00f5c4 100%);
               -webkit-background-clip:text;-webkit-text-fill-color:transparent;
               background-clip:text;margin:0">
      Local SLM Observatory
    </h1>
    <div style="font-size:11px;color:#4a5568;letter-spacing:1px;margin-top:4px">
      phi3:mini · llama3.2:3b · mistral:7b — Windows CPU · Ollama 0.22.1
    </div>
  </div>
  <div style="text-align:right;font-size:10px;color:#4a5568;line-height:1.9">
    <div>Models <span style="color:#00f5c4">3 compared</span></div>
    <div>Tasks <span style="color:#00f5c4">4 × 2 runs</span></div>
    <div>Hardware <span style="color:#00f5c4">Windows CPU-only</span></div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── KPI row ────────────────────────────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)

fastest = df.loc[df["avg_tokens_per_sec"].idxmax()]
slowest_ttft = df.loc[df["avg_ttft_ms"].idxmax()]
fastest_ttft = df.loc[df["avg_ttft_ms"].idxmin()]
scored = df[df["avg_quality_score"].notna()]

k1.metric("⚡ Best Throughput",
          f"{fastest['avg_tokens_per_sec']:.1f} t/s",
          fastest["model"].split(":")[0])
k2.metric("🚀 Fastest TTFT",
          f"{fastest_ttft['avg_ttft_ms']/1000:.1f}s",
          fastest_ttft["model"].split(":")[0])
k3.metric("🐢 Slowest TTFT",
          f"{slowest_ttft['avg_ttft_ms']/1000:.1f}s",
          slowest_ttft["model"].split(":")[0])
k4.metric("🎯 Top Quality Score",
          f"{scored['avg_quality_score'].max():.2f}",
          "llama + mistral")

st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)

# ── Row 2: Scatter + TTFT bar ──────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.markdown("""<div style="font-size:9px;letter-spacing:2px;text-transform:uppercase;
        color:#4a5568;margin-bottom:12px">◉ &nbsp;Speed vs Quality Tradeoff</div>""",
        unsafe_allow_html=True)

    scored_df = df[df["avg_quality_score"].notna()].copy()
    fig1 = go.Figure()
    for model, grp in scored_df.groupby("model"):
        color = MODEL_COLORS.get(model, "#888")
        fig1.add_trace(go.Scatter(
            x=grp["avg_tokens_per_sec"],
            y=grp["avg_quality_score"],
            mode="markers+text",
            name=model,
            text=grp["task"],
            textposition="top center",
            textfont=dict(size=9, color=color),
            marker=dict(size=14, color=color,
                        line=dict(width=1, color="rgba(255,255,255,0.2)")),
        ))
    fig1.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(10,15,30,0.8)",
        font=dict(family="JetBrains Mono", color="#e2e8f0", size=10),
        xaxis=dict(title="Speed (tokens/sec)", gridcolor="#1a2444",
                   zeroline=False, color="#4a5568"),
        yaxis=dict(title="Quality Score (0–1)", range=[-0.05, 1.15],
                   gridcolor="#1a2444", zeroline=False, color="#4a5568"),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=9)),
        margin=dict(l=40, r=20, t=10, b=40),
        height=280,
    )
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.markdown("""<div style="font-size:9px;letter-spacing:2px;text-transform:uppercase;
        color:#4a5568;margin-bottom:12px">◉ &nbsp;Time-to-First-Token (ms) — lower is better</div>""",
        unsafe_allow_html=True)

    fig2 = go.Figure()
    for model, grp in df.groupby("model"):
        color = MODEL_COLORS.get(model, "#888")
        fig2.add_trace(go.Bar(
            name=model, x=grp["task"], y=grp["avg_ttft_ms"],
            marker_color=color, marker_line_width=0, opacity=0.9,
        ))
    fig2.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(10,15,30,0.8)",
        font=dict(family="JetBrains Mono", color="#e2e8f0", size=10),
        barmode="group",
        xaxis=dict(gridcolor="#1a2444", zeroline=False, color="#4a5568"),
        yaxis=dict(title="TTFT (ms)", gridcolor="#1a2444",
                   zeroline=False, color="#4a5568"),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=9)),
        margin=dict(l=40, r=20, t=10, b=40),
        height=280,
    )
    st.plotly_chart(fig2, use_container_width=True)

# ── Throughput full width ──────────────────────────────────────────────────────
st.markdown("""<div style="font-size:9px;letter-spacing:2px;text-transform:uppercase;
    color:#4a5568;margin-bottom:12px">◉ &nbsp;Throughput (tokens/sec) — higher is better</div>""",
    unsafe_allow_html=True)

fig3 = go.Figure()
for model, grp in df.groupby("model"):
    color = MODEL_COLORS.get(model, "#888")
    fig3.add_trace(go.Bar(
        name=model, x=grp["task"], y=grp["avg_tokens_per_sec"],
        marker_color=color, marker_line_width=0, opacity=0.9,
        text=grp["avg_tokens_per_sec"].round(1),
        textposition="outside",
        textfont=dict(size=9, color=color),
    ))
fig3.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(10,15,30,0.8)",
    font=dict(family="JetBrains Mono", color="#e2e8f0", size=10),
    barmode="group",
    xaxis=dict(gridcolor="#1a2444", zeroline=False, color="#4a5568"),
    yaxis=dict(title="Tokens/sec", gridcolor="#1a2444",
               zeroline=False, color="#4a5568"),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=9)),
    margin=dict(l=40, r=20, t=30, b=40),
    height=240,
)
st.plotly_chart(fig3, use_container_width=True)

# ── Verdict + Cost ─────────────────────────────────────────────────────────────
v1, v2 = st.columns([3, 2])

with v1:
    st.markdown("""
    <div style="font-size:9px;letter-spacing:2px;text-transform:uppercase;
                color:#4a5568;margin-bottom:12px">◉ &nbsp;Model Verdicts</div>
    <div style="display:flex;flex-direction:column;gap:10px">
      <div style="border:1px solid rgba(123,97,255,0.35);border-radius:8px;padding:14px;
                  background:rgba(123,97,255,0.06)">
        <div style="font-size:9px;color:#7b61ff;letter-spacing:2px;text-transform:uppercase;
                    margin-bottom:4px">🏆 Overall Winner</div>
        <div style="font-family:Syne,sans-serif;font-size:18px;font-weight:800;color:#7b61ff">
          llama3.2:3b</div>
        <div style="font-size:10px;color:#4a5568;margin-top:4px;line-height:1.6">
          Fastest TTFT, best throughput, perfect quality on all scored tasks.
          Only model that passes code generation. Best for interactive CPU apps.</div>
      </div>
      <div style="border:1px solid rgba(255,107,107,0.35);border-radius:8px;padding:14px;
                  background:rgba(255,107,107,0.06)">
        <div style="font-size:9px;color:#ff6b6b;letter-spacing:2px;text-transform:uppercase;
                    margin-bottom:4px">🎯 Quality Ceiling</div>
        <div style="font-family:Syne,sans-serif;font-size:18px;font-weight:800;color:#ff6b6b">
          mistral:7b-instruct</div>
        <div style="font-size:10px;color:#4a5568;margin-top:4px;line-height:1.6">
          Matches llama quality but 4× slower on CPU. Justified only for
          batch pipelines where latency doesn't matter.</div>
      </div>
      <div style="border:1px solid rgba(0,245,196,0.2);border-radius:8px;padding:14px;
                  background:rgba(0,245,196,0.04)">
        <div style="font-size:9px;color:#00f5c4;letter-spacing:2px;text-transform:uppercase;
                    margin-bottom:4px">⚠️ Specialist Only</div>
        <div style="font-family:Syne,sans-serif;font-size:18px;font-weight:800;color:#00f5c4">
          phi3:mini</div>
        <div style="font-size:10px;color:#4a5568;margin-top:4px;line-height:1.6">
          Perfect JSON extraction but completely failed code generation (0.0).
          Use only for simple structured extraction tasks.</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

with v2:
    st.markdown("""<div style="font-size:9px;letter-spacing:2px;text-transform:uppercase;
        color:#4a5568;margin-bottom:12px">◉ &nbsp;Cost Analysis — 1000 req/day</div>""",
        unsafe_allow_html=True)

    fig4 = go.Figure(go.Bar(
        x=[75, 45, 3],
        y=["GPT-4o (cloud)", "Claude Sonnet", "Local (this)"],
        orientation="h",
        marker_color=["#ff6b6b", "#ffc107", "#00f5c4"],
        marker_line_width=0,
        text=["$75/mo", "$45/mo", "$3/mo"],
        textposition="outside",
        textfont=dict(size=11, family="Syne"),
    ))
    fig4.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(10,15,30,0.8)",
        font=dict(family="JetBrains Mono", color="#e2e8f0", size=10),
        xaxis=dict(gridcolor="#1a2444", zeroline=False,
                   color="#4a5568", title="$/month"),
        yaxis=dict(gridcolor="#1a2444", zeroline=False, color="#4a5568"),
        margin=dict(l=10, r=60, t=10, b=40),
        height=200,
    )
    st.plotly_chart(fig4, use_container_width=True)

    st.markdown("""
    <div style="background:rgba(0,245,196,0.05);border:1px solid rgba(0,245,196,0.15);
                border-radius:6px;padding:12px;font-size:10px;color:#4a5568;line-height:1.8">
      Break-even at <span style="color:#00f5c4">~200 req/day</span> vs cloud APIs.<br>
      Privacy cost = <span style="color:#00f5c4">$0</span>. Zero tokens leave the machine.<br>
      Latency: all models >8s TTFT on CPU —
      <span style="color:#ffc107">batch use only</span>.
    </div>
    """, unsafe_allow_html=True)

# ── Raw data ───────────────────────────────────────────────────────────────────
st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
st.markdown("""<div style="font-size:9px;letter-spacing:2px;text-transform:uppercase;
    color:#4a5568;margin-bottom:12px">◉ &nbsp;Raw Benchmark Data</div>""",
    unsafe_allow_html=True)

display_df = df[["model", "task", "avg_ttft_ms", "avg_total_ms",
                  "avg_tokens_per_sec", "avg_quality_score"]].copy()
display_df.columns = ["Model", "Task", "TTFT (ms)", "Total (ms)", "Tok/s", "Quality"]
st.dataframe(display_df, use_container_width=True, hide_index=True)

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-top:24px;padding-top:16px;border-top:1px solid #1a2444;
            display:flex;justify-content:space-between;font-size:9px;color:#4a5568">
  <div>local-slm-benchmark · Ollama 0.22.1 · Windows CPU · 2026</div>
  <div>3 models · 4 tasks · 2 runs each · 24 total inferences</div>
</div>
""", unsafe_allow_html=True)