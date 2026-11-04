"""Re-plot LFVD data figures from the archived CSVs (Drive snapshot 2026-11-01).

Inputs (data dir):
  control_curve.csv                -> fig3a_lighting_response, fig3b_mead_response
  family_scaling.csv (ablation v2) -> fig5a_representation, fig5b_control, family_scaling
  representation_bottleneck.csv    -> frozen-VAE reference line in fig5a / family_scaling
"""
import sys, os
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

DATA, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)

plt.rcParams.update({
    "font.family": "STIXGeneral", "mathtext.fontset": "stix",
    "font.size": 12, "axes.labelsize": 13, "xtick.labelsize": 11, "ytick.labelsize": 11,
    "legend.fontsize": 10, "axes.linewidth": 1.0,
    "axes.spines.top": False, "axes.spines.right": False,
    "pdf.fonttype": 42, "savefig.bbox": "tight", "savefig.pad_inches": 0.03,
})
RED, LRED, BLUE, GREY = "#E8141E", "#F0505A", "#1060F0", "#808080"
STYLE = {
    "target":   dict(color=GREY, ls="--", marker="D", ms=5, lw=1.6, label="Target (measured)"),
    "Pointwise shared-noise": dict(color=RED, ls="-", marker="s", ms=7, lw=2.0, label="Baseline (per-control)"),
    "Endpoint latent interpolation": dict(color=LRED, ls="--", marker="^", ms=7, lw=1.6, label="Latent interpolation"),
    "LFVD":     dict(color=BLUE, ls="-", marker="o", ms=7, lw=2.0, label="Ours (LFVD)"),
}
ORDER = ["target", "Pointwise shared-noise", "Endpoint latent interpolation", "LFVD"]
B, RNG = 10_000, np.random.default_rng(20261102)


def grid(ax):
    ax.grid(True, ls="--", lw=0.6, color="#d9d9d9", alpha=0.9)
    ax.set_axisbelow(True)


def cluster_ci(df, col):
    """Mean and 95% cluster-bootstrap CI over (fold, family_id) clusters, per control."""
    df = df.assign(cluster=df["fold"].astype(str) + "/" + df["family_id"].astype(str))
    piv = df.groupby(["cluster", "control"])[col].mean().unstack("control")  # clusters x controls
    vals = piv.to_numpy()
    n = vals.shape[0]
    idx = RNG.integers(0, n, size=(B, n))
    boots = vals[idx].mean(axis=1)                                          # B x controls
    lo, hi = np.percentile(boots, [2.5, 97.5], axis=0)
    return piv.columns.to_numpy(), vals.mean(axis=0), lo, hi, n


def response_plot(dataset, fname, xlabel, xticks_labeled):
    cc = pd.read_csv(f"{DATA}/control_curve.csv")
    d = cc[cc.dataset == dataset]
    fig, ax = plt.subplots(figsize=(4.8, 3.6))
    rows = []
    for key in ORDER:
        st = dict(STYLE[key])
        if key == "target":
            x, m, lo, hi, n = cluster_ci(d[d.method == "LFVD"], "normalized_target_response")
            ax.plot(x, m, zorder=2, **st)
        else:
            x, m, lo, hi, n = cluster_ci(d[d.method == key], "normalized_prediction_response")
            ax.errorbar(x, m, yerr=[m - lo, hi - m], capsize=3, elinewidth=1.1, capthick=1.1,
                        zorder=3 if key == "LFVD" else 2.5, **st)
        for xi, mi, l, h in zip(x, m, lo, hi):
            rows.append(dict(dataset=dataset, series=st["label"], control=xi, mean=mi,
                             ci_low=l, ci_high=h, clusters=n))
    ax.set_xticks(x)
    ax.set_xticklabels([f"{v:.3f}" if (round(v, 3) in xticks_labeled) else "" for v in x]
                       if dataset == "Lighting" else [f"{v:g}" for v in x])
    ax.set_xlim(x.min() - 0.04, x.max() + 0.04)
    ax.set_ylim(-0.04, 1.08)
    ax.set_yticks(np.arange(0, 1.01, 0.2))
    ax.set_xlabel(xlabel)
    ax.set_ylabel("Normalized measured response")
    grid(ax)
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.01), ncol=2, frameon=True,
              fancybox=True, edgecolor="#bbbbbb", handlelength=2.6, columnspacing=1.2)
    fig.savefig(f"{OUT}/{fname}.pdf"); fig.savefig(f"{OUT}/{fname}.png", dpi=200)
    plt.close(fig)
    return rows


def family_plots():
    fs = pd.read_csv(f"{DATA}/family_scaling.csv")
    rb = pd.read_csv(f"{DATA}/representation_bottleneck.csv")
    vae = float(rb.loc[rb.stage == "frozen_vae_target", "lpips"].iloc[0])
    ex = fs[fs.stage == "exact"].sort_values("train_families")
    sa = fs[fs.stage == "sampled"].sort_values("train_families")
    n = ex.train_families.to_numpy()
    xs = np.log2(n)

    def lpips_fig(fname):
        fig, ax = plt.subplots(figsize=(4.8, 3.6))
        ax.plot(xs, np.full_like(xs, vae, dtype=float), color=GREY, ls="--", marker="o", ms=5, lw=1.6,
                label=f"Frozen VAE (target, {vae:.4f})")
        ax.plot(xs, sa.lpips, color=RED, marker="s", ms=7, lw=2.0, label="Sampled family code")
        ax.plot(xs, ex.lpips, color=BLUE, marker="o", ms=7, lw=2.0, label="Exact family code")
        ax.set_ylim(0.0, 0.52)
        ax.set_yticks(np.arange(0, 0.51, 0.1))
        ax.set_xticks(xs); ax.set_xticklabels([str(v) for v in n])
        ax.set_xlabel("Number of training families"); ax.set_ylabel(r"LPIPS $\downarrow$")
        grid(ax)
        ax.legend(loc="center left", bbox_to_anchor=(0.02, 0.48), frameon=True, fancybox=True, edgecolor="#bbbbbb")
        fig.savefig(f"{OUT}/{fname}.pdf"); fig.savefig(f"{OUT}/{fname}.png", dpi=200)
        plt.close(fig)

    lpips_fig("fig5a_representation")
    lpips_fig("family_scaling")

    fig, ax = plt.subplots(figsize=(4.8, 3.6))
    ax.plot(xs, ex.control_spearman, color=GREY, ls="--", lw=1.6, marker="D", ms=5,
            label="Exact family code (reference)")
    ax.plot(xs, sa.control_spearman, color=BLUE, marker="o", ms=7, lw=2.0,
            label="Ours (LFVD, sampled code)")
    ax.set_ylim(0.0, 1.05); ax.set_yticks(np.arange(0, 1.01, 0.2))
    ax.set_xticks(xs); ax.set_xticklabels([str(v) for v in n])
    ax.set_xlabel("Number of training families"); ax.set_ylabel(r"Spearman $\uparrow$")
    grid(ax)
    ax.legend(loc="lower right", frameon=True, fancybox=True, edgecolor="#bbbbbb")
    fig.savefig(f"{OUT}/fig5b_control.pdf"); fig.savefig(f"{OUT}/fig5b_control.png", dpi=200)
    plt.close(fig)

    t = fs[["train_families", "stage", "lpips", "control_spearman"]].copy()
    t["frozen_vae_lpips"] = vae
    return t


rows = response_plot("Lighting", "fig3a_lighting_response", r"Lighting control value $s$",
                     {0.0, 0.228, 0.529, 0.767, 1.0})
rows += response_plot("MEAD", "fig3b_mead_response", r"Expression intensity $s$", set())
pd.DataFrame(rows).to_csv(f"{OUT}/fig3_plotted_values.csv", index=False)
family_plots().to_csv(f"{OUT}/fig5_plotted_values.csv", index=False)
print("done")
