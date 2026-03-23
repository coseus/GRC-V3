from io import BytesIO
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def score_to_hex(score):
    if score < 50:
        return "#d32f2f"
    if score < 75:
        return "#f9a825"
    return "#2e7d32"

def generate_bar_chart(scores: dict):
    fig, ax = plt.subplots(figsize=(10, 5))
    labels = list(scores.keys())
    values = list(scores.values())
    ax.barh(labels, values)
    ax.set_xlim(0, 100)
    ax.set_xlabel("Score")
    ax.set_title("Domain Scores")
    plt.tight_layout()
    buf = BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf

def generate_comparison_heatmap(df: pd.DataFrame):
    if df.empty:
        fig, ax = plt.subplots(figsize=(8,2))
        ax.text(0.5,0.5,"No data", ha="center", va="center")
        ax.axis("off")
        buf=BytesIO(); plt.savefig(buf, format="png", bbox_inches="tight"); plt.close(fig); buf.seek(0); return buf
    values = df.fillna(np.nan).values
    fig, ax = plt.subplots(figsize=(max(8, len(df.columns)*1.5), max(3, len(df.index)*0.5+1)))
    cax=ax.imshow(values, cmap="RdYlGn", aspect="auto", vmin=0, vmax=100)
    ax.set_xticks(range(len(df.columns))); ax.set_xticklabels(df.columns, rotation=25, ha="right")
    ax.set_yticks(range(len(df.index))); ax.set_yticklabels(df.index)
    for i in range(values.shape[0]):
        for j in range(values.shape[1]):
            val=values[i,j]
            if not np.isnan(val):
                ax.text(j,i,f"{val:.0f}",ha="center",va="center",fontsize=8)
    fig.colorbar(cax, ax=ax, fraction=0.03, pad=0.04)
    plt.tight_layout()
    buf=BytesIO(); plt.savefig(buf, format="png", bbox_inches="tight"); plt.close(fig); buf.seek(0); return buf
