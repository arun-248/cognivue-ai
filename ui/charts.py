"""
ui/charts.py
------------
Interactive Plotly charts in the Cognivue visual style. Every chart is shown
with show(fig, key). Hover tooltips carry the exact values; a caption under
each chart (written by the page) describes it in words for accessibility.
"""

from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st

NAVY, MUTED, BLUE, PURPLE, CYAN, AMBER, GREY = "#142B55", "#425B82", "#3478F6", "#8757E8", "#0F8F80", "#D97706", "#B9C9E6"
GRID = "#DCE6F5"
FONT = "Inter, Segoe UI, Arial, sans-serif"
LIKERT_COLORS = ["#D97706", "#F3B77A", "#D6DDEB", "#8DB4F8", "#3478F6"]


def _style(fig: go.Figure, height: int, legend: bool = False, margin=None) -> go.Figure:
    fig.update_layout(
        height=height, paper_bgcolor="white", plot_bgcolor="white",
        font=dict(family=FONT, size=12, color=NAVY),
        margin=margin or dict(l=8, r=12, t=28, b=8),
        showlegend=legend, hoverlabel=dict(font_family=FONT, bgcolor="white", bordercolor=GRID),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
    )
    fig.update_xaxes(gridcolor=GRID, zerolinecolor=MUTED, linecolor=GRID, tickfont=dict(color=MUTED))
    fig.update_yaxes(gridcolor=GRID, zerolinecolor=MUTED, linecolor=GRID, tickfont=dict(color=MUTED))
    return fig


def show(fig: go.Figure, key: str) -> None:
    st.plotly_chart(fig, key=key, width="stretch", config={"displayModeBar": False, "responsive": True})


def hbar(labels, values, colors, xlabel, fmt="{:.3f}", errors=None, xrange=None, height=None) -> go.Figure:
    fig = go.Figure(go.Bar(
        x=values, y=labels, orientation="h", marker_color=colors,
        error_x=dict(type="data", array=errors, color=MUTED, thickness=1.2) if errors else None,
        text=[fmt.format(v) for v in values], textposition="outside", cliponaxis=False,
        hovertemplate="%{y}: %{x:.4f}<extra></extra>",
    ))
    fig.update_yaxes(autorange="reversed", showgrid=False)
    fig.update_xaxes(title_text=xlabel, range=xrange)
    return _style(fig, height or max(180, 46 * len(labels) + 70), margin=dict(l=8, r=60, t=14, b=8))


def vbar_grouped(categories, series: dict, colors: dict, ylabel, yrange=None, fmt="{:.2f}", height=320) -> go.Figure:
    fig = go.Figure()
    for name, values in series.items():
        fig.add_bar(name=name, x=categories, y=values, marker_color=colors[name],
                    text=[fmt.format(v) for v in values], textposition="outside", cliponaxis=False,
                    hovertemplate="%{x} (" + name + "): %{y:.3f}<extra></extra>")
    fig.update_layout(barmode="group")
    fig.update_yaxes(title_text=ylabel, range=yrange)
    fig.update_xaxes(showgrid=False)
    return _style(fig, height, legend=len(series) > 1)


def line(xs, ys, color, ylabel, xlabel, xtick_text=None, height=260) -> go.Figure:
    fig = go.Figure(go.Scatter(x=xs, y=ys, mode="lines+markers", line=dict(color=color, width=2.5), marker=dict(size=8),
                               hovertemplate="%{x}: %{y:.4f}<extra></extra>"))
    fig.update_xaxes(title_text=xlabel, tickvals=xs, ticktext=xtick_text)
    fig.update_yaxes(title_text=ylabel)
    return _style(fig, height)


def multi_line(xs, series: dict, colors: dict, ylabel, xlabel, yrange=None, height=300) -> go.Figure:
    fig = go.Figure()
    for name, ys in series.items():
        fig.add_scatter(x=xs, y=ys, name=name, mode="lines+markers", line=dict(color=colors[name], width=2.5),
                        marker=dict(size=8), hovertemplate=name + ": %{y:.2f}<extra></extra>")
    fig.update_xaxes(title_text=xlabel, tickvals=xs)
    fig.update_yaxes(title_text=ylabel, range=yrange)
    return _style(fig, height, legend=True)


def radar(labels, series: dict, colors: dict, rmin=1, rmax=5, midpoint=3.0, height=470, accent_index=None, accent_name="Direct Overreliance", accent_color="#D6336C") -> go.Figure:
    """Radar chart. Long labels are wrapped, margins leave room for them, and the legend sits below the plot.
    accent_index marks one axis (e.g. the direct overreliance measure) with a distinct marker."""
    fig = go.Figure()
    def _wrap(label: str) -> str:
        label = str(label).replace(" (", "<br>(").replace(" and ", "<br>and ")
        parts = []
        for line in label.split("<br>"):
            words = line.split(" ")
            if len(line) > 14 and len(words) > 1:
                half = len(words) // 2 or 1
                line = " ".join(words[:half]) + "<br>" + " ".join(words[half:])
            parts.append(line)
        return "<br>".join(parts)

    wrapped = [_wrap(l) for l in labels]
    theta = wrapped + [wrapped[0]]
    if midpoint is not None:
        fig.add_scatterpolar(r=[midpoint] * len(theta), theta=theta, mode="lines", name="Neutral midpoint (3.0)",
                             line=dict(color=MUTED, dash="dash", width=1.2), hoverinfo="skip")
    for name, values in series.items():
        fig.add_scatterpolar(r=list(values) + [values[0]], theta=theta, name=name, fill="toself", opacity=0.55,
                             line=dict(color=colors[name], width=2.5), hovertemplate="%{theta}: %{r:.2f}<extra>" + name + "</extra>")
        if accent_index is not None:
            fig.add_scatterpolar(r=[values[accent_index]], theta=[wrapped[accent_index]], mode="markers", name=accent_name,
                                 marker=dict(color=accent_color, size=14, symbol="diamond", line=dict(color="white", width=2)),
                                 hovertemplate="%{theta}: %{r:.2f}<extra>" + accent_name + "</extra>")
    fig.update_layout(polar=dict(radialaxis=dict(range=[rmin, rmax], tickvals=list(range(rmin, rmax + 1)), gridcolor=GRID, linecolor=GRID,
                                                 tickfont=dict(size=11, color=NAVY)),
                                 angularaxis=dict(gridcolor=GRID, linecolor=GRID, tickfont=dict(size=12, color=NAVY)), bgcolor="white"))
    _style(fig, height, legend=True, margin=dict(l=100, r=100, t=40, b=120))
    fig.update_layout(legend=dict(orientation="h", yanchor="top", y=-0.02, xanchor="center", x=0.5, font=dict(size=12, color=NAVY)))
    return fig


def construct_bars(labels, values, colors, height=300, midpoint_label="neutral midpoint (3.0)") -> go.Figure:
    """Horizontal bars (1-5). `colors` may differ per bar so one measure can be visually distinct."""
    fig = go.Figure(go.Bar(x=values, y=labels, orientation="h", marker_color=colors,
                           text=[f"{v:.2f}" for v in values], textposition="outside", cliponaxis=False,
                           textfont=dict(color=NAVY, size=13),
                           hovertemplate="%{y}: %{x:.2f} / 5<extra></extra>"))
    fig.add_vline(x=3.0, line_dash="dash", line_color=MUTED, annotation_text=midpoint_label,
                  annotation_position="top", annotation_font=dict(size=11, color=NAVY))
    fig.update_xaxes(range=[1, 5.5], title_text="Your average (1\u20135)")
    fig.update_yaxes(autorange="reversed", showgrid=False, automargin=True, tickfont=dict(color=NAVY, size=12))
    return _style(fig, height, margin=dict(l=8, r=44, t=40, b=8))


def waterfall(baseline: float, contributions, prediction: float, height=420) -> go.Figure:
    """Baseline -> one step per feature -> estimate. contributions = [(label, shap), ...] in the given order."""
    names = ["Baseline"] + [c[0] for c in contributions] + ["Your estimate"]
    fig = go.Figure(go.Waterfall(
        orientation="v", x=names, measure=["absolute"] + ["relative"] * len(contributions) + ["total"],
        y=[baseline] + [c[1] for c in contributions] + [prediction],
        text=[f"{baseline:.2f}"] + [f"{c[1]:+.3f}" for c in contributions] + [f"{prediction:.2f}"], textposition="outside",
        increasing=dict(marker=dict(color=AMBER)), decreasing=dict(marker=dict(color=CYAN)),
        totals=dict(marker=dict(color=BLUE)), connector=dict(line=dict(color=GRID)),
        hovertemplate="%{x}: %{text}<extra></extra>",
    ))
    fig.update_yaxes(title_text="Model output (estimated score)")
    fig.update_xaxes(tickangle=-30, showgrid=False)
    return _style(fig, height, margin=dict(l=8, r=8, t=24, b=8))


def signed_bars(labels, values, height=None) -> go.Figure:
    colors = [AMBER if v > 0 else CYAN for v in values]
    fig = go.Figure(go.Bar(x=values, y=labels, orientation="h", marker_color=colors,
                           text=[f"{v:+.3f}" for v in values], textposition="outside", cliponaxis=False,
                           hovertemplate="%{y}: %{x:+.4f}<extra></extra>"))
    span = max(max(abs(v) for v in values), 1e-6)
    fig.add_vline(x=0, line_color=MUTED, line_width=1)
    fig.update_xaxes(range=[-span * 1.5, span * 1.5], title_text="Contribution to the estimate (left lowers, right raises)")
    fig.update_yaxes(autorange="reversed", showgrid=False)
    return _style(fig, height or 46 * len(labels) + 80, margin=dict(l=8, r=60, t=14, b=8))


def stacked_distribution(labels, counts_by_label: dict, totals, height=380) -> go.Figure:
    """100% stacked horizontal bars. counts_by_label: Likert label -> list of counts per item."""
    fig = go.Figure()
    for (name, counts), color in zip(counts_by_label.items(), LIKERT_COLORS):
        pct = [c / t * 100 for c, t in zip(counts, totals)]
        fig.add_bar(name=name, y=labels, x=pct, orientation="h", marker_color=color,
                    text=[f"{p:.0f}%" if p >= 6 else "" for p in pct], textposition="inside",
                    customdata=counts, hovertemplate="%{y}<br>" + name + ": %{customdata} respondents (%{x:.1f}%)<extra></extra>")
    fig.update_layout(barmode="stack")
    fig.update_xaxes(range=[0, 100], title_text="Share of the 249 modelled respondents (%)")
    fig.update_yaxes(autorange="reversed", showgrid=False)
    return _style(fig, height, legend=True, margin=dict(l=8, r=12, t=40, b=8))


def pca_scatter(centroids, labels, student=None, explained=(0, 0), height=360) -> go.Figure:
    fig = go.Figure()
    palette = [CYAN, PURPLE, AMBER, BLUE]
    for i, ((x, y), lab) in enumerate(zip(centroids, labels)):
        fig.add_scatter(x=[x], y=[y], mode="markers+text", text=[f"Cluster {i}"], textposition="top center", name=lab,
                        marker=dict(size=22, color=palette[i % 4], line=dict(color="white", width=2)),
                        hovertemplate=f"Cluster {i} centroid<br>PC1 %{{x:.2f}}, PC2 %{{y:.2f}}<extra></extra>")
    if student is not None:
        fig.add_scatter(x=[student[0]], y=[student[1]], mode="markers+text", text=["You"], textposition="bottom center", name="Your answers",
                        marker=dict(size=16, color="white", symbol="diamond", line=dict(color=NAVY, width=3)),
                        hovertemplate="Your answers<br>PC1 %{x:.2f}, PC2 %{y:.2f}<extra></extra>")
    fig.update_xaxes(title_text=f"PC1 ({explained[0] * 100:.1f}% of variance)", zeroline=True)
    fig.update_yaxes(title_text=f"PC2 ({explained[1] * 100:.1f}% of variance)", zeroline=True)
    return _style(fig, height, legend=True)


def scatter_oof(actual, predicted, height=360) -> go.Figure:
    fig = go.Figure()
    fig.add_scatter(x=[1, 5], y=[1, 5], mode="lines", line=dict(color=CYAN, dash="dash"), name="Perfect prediction", hoverinfo="skip")
    fig.add_scatter(x=list(actual), y=list(predicted), mode="markers", name="Out-of-fold predictions",
                    marker=dict(color=BLUE, opacity=0.7, size=8), hovertemplate="Actual %{x:.2f}, predicted %{y:.2f}<extra></extra>")
    fig.update_xaxes(title_text="Actual overreliance score", range=[0.8, 5.2])
    fig.update_yaxes(title_text="Predicted (out-of-fold)", range=[0.8, 5.2])
    return _style(fig, height, legend=True)


def scatter_residuals(predicted, residuals, height=360) -> go.Figure:
    fig = go.Figure()
    fig.add_hline(y=0, line_dash="dash", line_color=CYAN)
    fig.add_scatter(x=list(predicted), y=list(residuals), mode="markers", name="Residual",
                    marker=dict(color=PURPLE, opacity=0.7, size=8), hovertemplate="Predicted %{x:.2f}, residual %{y:+.2f}<extra></extra>")
    fig.update_xaxes(title_text="Predicted (out-of-fold)")
    fig.update_yaxes(title_text="Residual (actual - predicted)")
    return _style(fig, height)


def histogram(values, xlabel, height=300) -> go.Figure:
    fig = go.Figure(go.Histogram(x=list(values), marker_color=BLUE, nbinsx=20, hovertemplate="%{x}: %{y}<extra></extra>"))
    fig.update_xaxes(title_text=xlabel)
    fig.update_yaxes(title_text="Respondents")
    return _style(fig, height)
