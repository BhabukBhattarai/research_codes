import os
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.lines import Line2D
import warnings
warnings.filterwarnings("ignore")


# =========================
# 1) STYLE (journal + colorblind safe)
# =========================
def set_style():
    mpl.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
        "font.size": 10,
        "axes.titlesize": 12,
        "axes.labelsize": 10,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "axes.linewidth": 1.0,
        "savefig.dpi": 800,
        "savefig.format": "pdf",
        "savefig.bbox": "tight",
        "figure.facecolor": "white",
        "axes.facecolor": "white",
    })

    # Okabe–Ito palette (colorblind safe)
    global C
    C = {
        "obs": "#111111",   # near black
        "hbv": "#0072B2",   # blue
        "hec": "#D55E00",   # vermillion
        "grid": "#CFCFCF",
        "rms":  "#9E9E9E",
        "txt":  "#222222",
    }


# =========================
# 2) IO helpers
# =========================
def read_excel_first_sheet(path: str) -> pd.DataFrame:
    xls = pd.ExcelFile(path)
    return pd.read_excel(path, sheet_name=xls.sheet_names[0])

def clean_df(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [c.strip() for c in df.columns]

    needed = ["Date", "Runoff", "Simulated Runoff(HBV)", "Simulated Runoff(HECHMS)"]
    for col in needed:
        if col not in df.columns:
            raise ValueError(f"Missing required column: '{col}'")

    df["Date"] = pd.to_datetime(df["Date"])
    for col in ["Runoff", "Simulated Runoff(HBV)", "Simulated Runoff(HECHMS)"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.sort_values("Date")
    return df

def _pair(o, s):
    o = np.asarray(o, float)
    s = np.asarray(s, float)
    m = np.isfinite(o) & np.isfinite(s)
    return o[m], s[m]


# =========================
# 3) Taylor statistics (normalized)
# =========================
def taylor_stats(obs, sim):
    """
    Returns:
      std_ratio = std(sim)/std(obs)
      corr      = corr(obs, sim)
      crmsd     = centered RMSE / std(obs)    (normalized)
    """
    o, s = _pair(obs, sim)
    if len(o) < 2:
        return None

    so = np.std(o, ddof=1)
    ss = np.std(s, ddof=1)
    if so == 0 or ss == 0:
        return None

    r = np.corrcoef(o, s)[0, 1]
    r = float(np.clip(r, -1.0, 1.0))

    # centered RMSE: remove mean
    oc = o - np.mean(o)
    sc = s - np.mean(s)
    crmsd = np.sqrt(np.mean((sc - oc) ** 2)) / so

    return {"std_ratio": ss / so, "corr": r, "crmsd": crmsd, "n": len(o)}


# =========================
# 4) Taylor diagram drawing (Cartesian quarter-circle)
# =========================
def draw_taylor_base(ax,
                     rmax=1.6,
                     corr_ticks=(0.2, 0.4, 0.6, 0.8, 0.9, 0.95, 0.99),
                     std_ticks=(0.0, 0.5, 1.0, 1.5),
                     rms_levels=(0.2, 0.4, 0.6, 0.8, 1.0),
                     title=""):
    """
    Quarter-circle Taylor diagram in Cartesian coordinates.
    x = std_ratio * corr
    y = std_ratio * sqrt(1 - corr^2)
    Reference (obs) at (1, 0).
    """
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlim(0, rmax)
    ax.set_ylim(0, rmax)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # --- Std deviation circles (r = std_ratio)
    theta = np.linspace(0, np.pi/2, 400)
    for r in np.linspace(0.2, rmax, int(rmax/0.2)):
        ax.plot(r*np.cos(theta), r*np.sin(theta),
                color=C["grid"], lw=0.8, alpha=0.7)

    # label a few std circles (bottom axis)
    for r in std_ticks:
        if r <= 0:
            continue
        ax.text(r, -0.05*rmax, f"{r:.1f}", ha="center", va="top",
                fontsize=9, color=C["txt"])

    # --- Correlation rays
    for c in corr_ticks:
        th = np.arccos(c)
        ax.plot([0, rmax*np.cos(th)], [0, rmax*np.sin(th)],
                color=C["grid"], lw=0.8, alpha=0.7)

    # --- Correlation labels on outer arc
    for c in corr_ticks:
        th = np.arccos(c)
        x = (rmax + 0.06) * np.cos(th)
        y = (rmax + 0.06) * np.sin(th)
        ax.text(x, y, f"{c:.2f}".rstrip("0").rstrip("."),
                ha="center", va="center", fontsize=9, color=C["txt"])

    # Outer boundary arc (thicker)
    ax.plot(rmax*np.cos(theta), rmax*np.sin(theta), color="black", lw=1.2)

    # --- RMSD contours (centered RMSE) around reference point (1,0)
    # CRMSD^2 = 1^2 + r^2 - 2*r*c  (in normalized space where std(obs)=1)
    # In Cartesian: points (x,y) at std_ratio=r and corr=c.
    # We draw locus for constant CRMSD: for each r, solve for c and plot.
    rr = np.linspace(0.001, rmax, 600)
    for e in rms_levels:
        # c = (1 + r^2 - e^2) / (2r)
        c = (1 + rr**2 - e**2) / (2*rr)
        mask = (c >= 0) & (c <= 1)  # only plot valid in [0,1]
        r_ok = rr[mask]
        c_ok = c[mask]
        x = r_ok * c_ok
        y = r_ok * np.sqrt(1 - c_ok**2)
        ax.plot(x, y, color=C["rms"], lw=0.9, ls="--", alpha=0.9)
        # label one spot
        if len(x) > 10:
            idx = int(len(x) * 0.7)
            ax.text(x[idx], y[idx], f"{e:.1f}", fontsize=8,
                    color=C["rms"], ha="left", va="bottom")

    # Reference point (Observed): std_ratio=1, corr=1 => (1,0)
    ax.plot(1, 0, marker="o", ms=7, color=C["obs"], zorder=5)

    # Axis labels like reference style
    ax.set_xlabel("Standardized deviations (Normalized)")
    ax.set_ylabel("Standardized deviations (Normalized)")

    # "Correlation" label along arc (optional)
    ax.text(rmax*0.82, rmax*0.55, "Correlation", rotation=-35,
            fontsize=10, color=C["txt"], ha="center", va="center")

    ax.set_title(title, fontweight="bold", pad=10)
    ax.set_xticks([])
    ax.set_yticks([])


def plot_model_point(ax, st, label, color, marker):
    """
    Convert stats to Taylor Cartesian coordinates and plot.
    x = r*c
    y = r*sqrt(1-c^2)
    """
    if st is None:
        return None

    r = st["std_ratio"]
    c = st["corr"]
    x = r * c
    y = r * np.sqrt(max(0.0, 1 - c**2))

    ax.plot(x, y, marker=marker, ms=9,
            markerfacecolor=color, markeredgecolor="white",
            markeredgewidth=1.0, linestyle="None", zorder=10)

    # subtle label
    ax.text(x + 0.03, y + 0.03, label, fontsize=9, color=C["txt"])
    return (x, y)


# =========================
# 5) Make figure (two panels)
# =========================
def make_taylor_figure(df_cal, df_val, out_pdf, rmax=1.6):
    # compute stats (RAW)
    st_hbv_cal = taylor_stats(df_cal["Runoff"], df_cal["Simulated Runoff(HBV)"])
    st_hec_cal = taylor_stats(df_cal["Runoff"], df_cal["Simulated Runoff(HECHMS)"])
    st_hbv_val = taylor_stats(df_val["Runoff"], df_val["Simulated Runoff(HBV)"])
    st_hec_val = taylor_stats(df_val["Runoff"], df_val["Simulated Runoff(HECHMS)"])

    fig = plt.figure(figsize=(10.6, 5.0))
    gs = GridSpec(1, 2, figure=fig, wspace=0.25)

    ax_cal = fig.add_subplot(gs[0, 0])
    ax_val = fig.add_subplot(gs[0, 1])

    draw_taylor_base(ax_cal, rmax=rmax, title="Calibration")
    draw_taylor_base(ax_val, rmax=rmax, title="Validation")

    # calibration points
    plot_model_point(ax_cal, st_hbv_cal, "HBV", C["hbv"], "o")
    plot_model_point(ax_cal, st_hec_cal, "HEC-HMS", C["hec"], "s")

    # validation points (different markers)
    plot_model_point(ax_val, st_hbv_val, "HBV", C["hbv"], "^")
    plot_model_point(ax_val, st_hec_val, "HEC-HMS", C["hec"], "D")

    # legend (clean)
    legend_items = [
        Line2D([0],[0], marker="o", color="none", markerfacecolor=C["obs"],
               markeredgecolor=C["obs"], markersize=7, label="Observed (REF)"),
        Line2D([0],[0], marker="o", color="none", markerfacecolor=C["hbv"],
               markeredgecolor="white", markeredgewidth=1.0, markersize=9, label="HBV (Cal)"),
        Line2D([0],[0], marker="s", color="none", markerfacecolor=C["hec"],
               markeredgecolor="white", markeredgewidth=1.0, markersize=9, label="HEC-HMS (Cal)"),
        Line2D([0],[0], marker="^", color="none", markerfacecolor=C["hbv"],
               markeredgecolor="white", markeredgewidth=1.0, markersize=9, label="HBV (Val)"),
        Line2D([0],[0], marker="D", color="none", markerfacecolor=C["hec"],
               markeredgecolor="white", markeredgewidth=1.0, markersize=9, label="HEC-HMS (Val)"),
        Line2D([0],[0], linestyle="--", color=C["rms"], lw=1.0, label="CRMSD contours"),
    ]
    fig.legend(handles=legend_items, loc="lower center", ncol=3,
               frameon=False, bbox_to_anchor=(0.5, -0.02))

    fig.suptitle("Taylor Diagram — HBV vs HEC-HMS (RAW daily discharge)",
                 fontweight="bold", y=1.03)

    fig.savefig(out_pdf)
    plt.close(fig)
    print("Saved:", out_pdf)

    # print simple stats (so you can verify)
    def _print_one(name, st):
        if st is None:
            print(f"{name}: not enough data")
            return
        print(f"{name}: std_ratio={st['std_ratio']:.3f}, corr={st['corr']:.3f}, CRMSD={st['crmsd']:.3f}, n={st['n']}")

    print("\n--- Taylor stats (normalized; RAW) ---")
    _print_one("HBV Cal", st_hbv_cal)
    _print_one("HEC Cal", st_hec_cal)
    _print_one("HBV Val", st_hbv_val)
    _print_one("HEC Val", st_hec_val)


# =========================
# 6) RUN
# =========================
if __name__ == "__main__":
    set_style()

    cal_path = r"************.xlsx"
    val_path = r"************.xlsx"
    out_dir  = r"*************"
    os.makedirs(out_dir, exist_ok=True)

    df_cal = clean_df(read_excel_first_sheet(cal_path))
    df_val = clean_df(read_excel_first_sheet(val_path))

    out_pdf = os.path.join(out_dir, "Figure_Taylor_Diagram_JournalStyle_RAW.pdf")
    make_taylor_figure(df_cal, df_val, out_pdf, rmax=1.6)
