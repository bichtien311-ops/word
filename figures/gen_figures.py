# -*- coding: utf-8 -*-
"""Генератор рисунков для пособия «Режимы нейтрали электрических сетей» (PNG 300 dpi)."""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch

OUT = os.path.dirname(os.path.abspath(__file__))
DPI = 300
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 12, "axes.unicode_minus": False})


def _save(fig, name):
    fig.savefig(os.path.join(OUT, name), dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print("OK", name)


def _clean(ax, lx, ly):
    ax.set_xlim(*lx); ax.set_ylim(*ly)
    ax.set_xticks([]); ax.set_yticks([]); ax.set_aspect("equal")
    for s in ax.spines.values():
        s.set_visible(False)


def _arrow(ax, x, y, color, lw=2, x0=0, y0=0):
    ax.annotate("", xy=(x, y), xytext=(x0, y0),
                arrowprops=dict(arrowstyle="-|>", color=color, lw=lw))


def fig_neutral_modes():
    """Л1: пять режимов заземления нейтрали."""
    fig, axes = plt.subplots(1, 5, figsize=(10.5, 2.6))
    titles = ["Изолированная\nZ_N = ∞", "Компенсиров.\nZ_N = jX_L",
              "Резистивная\nZ_N = R_N", "Эффективно\nзаземл.", "Глухозаземл.\nZ_N = 0"]
    for ax, t in zip(axes, titles):
        # трёхфазный источник (звезда)
        ax.plot([0, 0], [1.2, 2.0], color="0.3", lw=2)
        for a in (90, 210, 330):
            ar = np.deg2rad(a)
            ax.plot([0, 0.6*np.cos(ar)], [2.0, 2.0+0.6*np.sin(ar)], color="0.3", lw=2)
        ax.plot(0, 2.0, "ko", ms=4)
        # нейтраль вниз к земле
        ax.plot([0, 0], [1.2, 0.5], color="tab:blue", lw=2)
        ax.set_title(t, fontsize=9)
        ax.hlines(0.3, -0.5, 0.5, color="0.3", lw=2)  # земля
        ax.vlines([-0.3, 0, 0.3], 0.18, 0.3, color="0.3", lw=1.2)
        _clean(ax, (-0.9, 0.9), (0.1, 2.8))
    # элемент в нейтрали
    axes[0].plot([0, 0], [0.5, 0.85], color="white")  # разрыв
    axes[0].text(0.12, 0.7, "∞", fontsize=11)
    axes[1].add_patch(Rectangle((-0.12, 0.55), 0.24, 0.35, fill=False, ec="tab:green", lw=2))
    axes[2].add_patch(Rectangle((-0.12, 0.55), 0.24, 0.35, fill=False, ec="tab:red", lw=2))
    _save(fig, "fig_neutral_modes.png")


def fig_symmetrical_components():
    """Л2: системы прямой, обратной и нулевой последовательностей."""
    fig, axes = plt.subplots(1, 3, figsize=(9.0, 3.4))
    cols = ["tab:red", "tab:green", "tab:blue"]
    # прямая: A 90, B -30, C 210 (A-B-C против часовой)
    ax = axes[0]
    for a, lab, c in zip([90, 330, 210], ["A", "B", "C"], cols):
        ar = np.deg2rad(a)
        _arrow(ax, np.cos(ar), np.sin(ar), c)
        ax.text(1.15*np.cos(ar), 1.15*np.sin(ar), lab, color=c, ha="center", fontsize=12)
    ax.set_title("Прямая (1)", fontsize=11)
    _clean(ax, (-1.4, 1.4), (-1.4, 1.4))
    # обратная: A 90, B 210, C 330 (A-C-B)
    ax = axes[1]
    for a, lab, c in zip([90, 210, 330], ["A", "B", "C"], cols):
        ar = np.deg2rad(a)
        _arrow(ax, np.cos(ar), np.sin(ar), c)
        ax.text(1.15*np.cos(ar), 1.15*np.sin(ar), lab, color=c, ha="center", fontsize=12)
    ax.set_title("Обратная (2)", fontsize=11)
    _clean(ax, (-1.4, 1.4), (-1.4, 1.4))
    # нулевая: три совпадающих вектора (слегка раздвинуты для видимости)
    ax = axes[2]
    for dx, lab, c in zip([-0.12, 0, 0.12], ["A", "B", "C"], cols):
        _arrow(ax, dx, 1.0, c, x0=dx, y0=0)
        ax.text(dx, 1.12, lab, color=c, ha="center", fontsize=10)
    ax.set_title("Нулевая (0)", fontsize=11)
    _clean(ax, (-1.0, 1.0), (-0.3, 1.4))
    _save(fig, "fig_symmetrical_components.png")


def fig_ozz_vectors():
    """Л3/Л4: векторная диаграмма напряжений при ОЗЗ фазы А."""
    fig, ax = plt.subplots(figsize=(5.2, 5.2))
    # нормальные фазы (пунктир)
    norm = {"A": 90, "B": 210, "C": 330}
    for lab, a in norm.items():
        ar = np.deg2rad(a)
        ax.plot([0, np.cos(ar)], [0, np.sin(ar)], color="0.7", lw=1, ls="--")
    # при ОЗЗ: U_A = 0; нейтраль смещается в -E_A (вниз)
    # новый центр (нейтраль) в точке -E_A = (0,-1)
    N = np.array([0, -1.0])
    _arrow(ax, N[0], N[1], "tab:purple")  # U_N
    ax.text(0.12, -0.6, "U\u0307_N", color="tab:purple", fontsize=13)
    # здоровые фазы из нейтрали к вершинам B, C (теперь линейные, ×√3)
    for lab, a, c in zip(["B", "C"], [210, 330], ["tab:green", "tab:blue"]):
        ar = np.deg2rad(a)
        tip = np.array([np.cos(ar), np.sin(ar)])
        _arrow(ax, tip[0], tip[1], c, x0=N[0], y0=N[1])
        ax.text(1.15*np.cos(ar), 1.15*np.sin(ar), "U\u0307_"+lab, color=c, ha="center", fontsize=12)
    # точка А (бывшая вершина) совпадает с нулём
    ax.plot(0, 1.0, "o", color="0.7", ms=4)
    ax.text(0.12, 1.05, "A (норма)", color="0.6", fontsize=9)
    ax.plot(0, 0, "ko", ms=5)
    ax.text(0.1, 0.08, "U\u0307_A=0", color="tab:red", fontsize=11)
    ax.axhline(0, color="0.85", lw=0.6); ax.axvline(0, color="0.85", lw=0.6)
    _clean(ax, (-1.4, 1.4), (-1.5, 1.4))
    _save(fig, "fig_ozz_vectors.png")


def fig_zero_seq_circuit():
    """Л3: схема замещения нулевой последовательности при ОЗЗ."""
    fig, ax = plt.subplots(figsize=(5.6, 3.6))
    # источник U_к0 слева
    ax.add_patch(Rectangle((0.2, 1.2), 0.5, 1.0, fill=False, ec="0.3", lw=1.8))
    ax.text(0.45, 1.7, "U\u2096\u2080", ha="center", va="center", fontsize=12)
    ax.text(0.45, 2.4, "точка ОЗЗ", ha="center", fontsize=8, color="0.4")
    # верхняя шина
    ax.plot([0.7, 5.0], [2.1, 2.1], color="0.3", lw=2)
    # ветвь ёмкости 3C0
    ax.plot([2.0, 2.0], [2.1, 1.3], color="tab:blue", lw=2)
    ax.plot([1.8, 2.2], [1.3, 1.3], color="tab:blue", lw=3)
    ax.plot([1.8, 2.2], [1.15, 1.15], color="tab:blue", lw=3)
    ax.text(2.25, 1.5, "3C\u2080", color="tab:blue", fontsize=11)
    # ветвь нейтрали 3R_N / j3X_L
    ax.plot([4.0, 4.0], [2.1, 1.4], color="tab:red", lw=2)
    ax.add_patch(Rectangle((3.85, 0.95), 0.3, 0.45, fill=False, ec="tab:red", lw=2))
    ax.text(4.25, 1.15, "3R_N / j3X_L", color="tab:red", fontsize=10)
    # нижняя шина (земля)
    ax.plot([0.45, 4.0], [0.5, 0.5], color="0.3", lw=2)
    ax.plot([0.45, 0.45], [1.2, 0.5], color="0.3", lw=1.8)
    ax.plot([2.0, 2.0], [1.15, 0.5], color="tab:blue", lw=2)
    ax.plot([4.0, 4.0], [0.95, 0.5], color="tab:red", lw=2)
    ax.text(2.2, 0.3, "земля (нулевой потенциал)", ha="center", fontsize=8, color="0.4")
    _clean(ax, (0, 5.6), (0, 2.7))
    _save(fig, "fig_zero_seq_circuit.png")


def fig_isolated_net():
    """Л4: сеть с изолированной нейтралью и ёмкостные токи фаз."""
    fig, ax = plt.subplots(figsize=(6.0, 3.8))
    # источник звезда
    ax.plot(0.6, 2.0, "ko", ms=5)
    for a, lab, yo in zip([90, 210, 330], ["A", "B", "C"], [0, 0, 0]):
        pass
    # три фазных провода вправо
    ys = [2.6, 2.0, 1.4]
    cols = ["tab:red", "tab:green", "tab:blue"]
    labs = ["A", "B", "C"]
    for y, c, lab in zip(ys, cols, labs):
        ax.plot([0.6, 4.5], [y, y], color=c, lw=2)
        ax.text(4.6, y, lab, color=c, fontsize=12, va="center")
        # ёмкость на землю
        ax.plot([3.8, 3.8], [y, 0.7], color=c, lw=1.2, ls=":")
        ax.plot([3.7, 3.9], [0.7, 0.7], color=c, lw=3)
        ax.plot([3.7, 3.9], [0.58, 0.58], color=c, lw=3)
    ax.plot([0.6, 0.6], [2.6, 1.4], color="0.3", lw=2)  # звезда
    # нейтраль изолирована
    ax.plot([0.6, 0.6], [2.0, 1.0], color="0.5", lw=1.5, ls="--")
    ax.text(0.7, 1.0, "нейтраль\nизолирована", fontsize=8, color="0.4")
    # земля
    ax.plot([0.3, 4.5], [0.4, 0.4], color="0.3", lw=2)
    for x in (3.7, 3.8, 3.9):
        pass
    ax.text(3.8, 0.15, "C\u2080 (ёмкости фаз)", ha="center", fontsize=8, color="0.4")
    _clean(ax, (0, 5.2), (0, 3.0))
    _save(fig, "fig_isolated_net.png")


def fig_arc_overvoltage():
    """Л5: эскалация дуговых перенапряжений до 3,5 U_ф."""
    fig, ax = plt.subplots(figsize=(6.4, 3.6))
    t = np.linspace(0, 0.1, 2000)
    f = 50
    u = np.sin(2*np.pi*f*t)
    # ступенчатый рост огибающей перенапряжений
    env = np.ones_like(t)
    peaks = [(0.02, 2.4), (0.04, 2.9), (0.06, 3.2), (0.08, 3.5)]
    sig = np.sin(2*np.pi*f*t)
    for i, ti in enumerate(t):
        e = 1.0
        for tp, val in peaks:
            if ti >= tp:
                e = val
        env[i] = e
    ax.plot(t*1000, env*sig, color="tab:red", lw=1.3)
    ax.plot(t*1000, env, color="0.5", ls="--", lw=1, label="огибающая")
    for tp, val in peaks:
        ax.annotate(f"{val} U\u0444", xy=(tp*1000, val), fontsize=9, color="tab:red")
    ax.axhline(1, color="0.8", ls=":", lw=1)
    ax.set_xlabel("t, мс"); ax.set_ylabel("u / U\u0444")
    ax.set_xlim(0, 100); ax.set_ylim(-3.8, 4.0)
    ax.grid(True, color="0.93")
    _save(fig, "fig_arc_overvoltage.png")


def fig_compensation():
    """Л6: компенсированная нейтраль — ДГР и резонансный контур токов."""
    fig, axes = plt.subplots(1, 2, figsize=(9.0, 3.6))
    # схема
    ax = axes[0]
    ax.plot(0.6, 2.0, "ko", ms=5)
    ys = [2.6, 2.0, 1.4]; cols = ["tab:red", "tab:green", "tab:blue"]
    for y, c in zip(ys, cols):
        ax.plot([0.6, 4.2], [y, y], color=c, lw=2)
        ax.plot([3.6, 3.6], [y, 0.8], color=c, lw=1, ls=":")
        ax.plot([3.5, 3.7], [0.8, 0.8], color=c, lw=3)
    ax.plot([0.6, 0.6], [2.6, 1.4], color="0.3", lw=2)
    # ДГР в нейтрали
    ax.plot([0.6, 0.6], [2.0, 1.3], color="tab:purple", lw=2)
    ax.add_patch(Rectangle((0.45, 0.85), 0.3, 0.45, fill=False, ec="tab:purple", lw=2))
    ax.text(0.85, 1.05, "ДГР (L_N)", color="tab:purple", fontsize=9)
    ax.plot([0.2, 4.2], [0.5, 0.5], color="0.3", lw=2)
    ax.plot([0.6, 0.6], [0.85, 0.5], color="tab:purple", lw=2)
    ax.set_title("Схема включения ДГР", fontsize=10)
    _clean(ax, (0, 4.8), (0.2, 3.0))
    # векторная диаграмма компенсации
    ax = axes[1]
    _arrow(ax, 0, -1.0, "tab:purple"); ax.text(0.08, -0.6, "U_N", color="tab:purple", fontsize=12)
    _arrow(ax, 0, 1.0, "tab:blue");   ax.text(0.08, 0.85, "I_C", color="tab:blue", fontsize=12)
    _arrow(ax, 0, -0.85, "tab:red", lw=3); ax.text(-0.55, -0.5, "I_L", color="tab:red", fontsize=12)
    _arrow(ax, 0.5, 0.0, "tab:green"); ax.text(0.55, 0.1, "I_ост", color="tab:green", fontsize=11)
    ax.axhline(0, color="0.85", lw=0.6); ax.axvline(0, color="0.85", lw=0.6)
    ax.set_title("Компенсация I_C и I_L", fontsize=10)
    _clean(ax, (-1.1, 1.1), (-1.3, 1.3))
    _save(fig, "fig_compensation.png")


def fig_resonance_curve():
    """Л7: резонансная кривая напряжения смещения нейтрали."""
    fig, ax = plt.subplots(figsize=(6.0, 3.8))
    nu = np.linspace(-0.3, 0.3, 400)
    d = 0.05
    Un = 1.0 / np.sqrt(nu**2 + d**2) * d  # нормировано, max=1 при ν=0
    ax.plot(nu*100, Un, color="tab:blue", lw=2)
    ax.axvline(0, color="tab:red", ls="--", lw=1.5)
    ax.text(1, 0.4, "резонанс\n\u03bd = 0", color="tab:red", fontsize=10)
    ax.text(-27, 0.85, "недо-\nкомпенс.", fontsize=9, color="0.4")
    ax.text(18, 0.85, "пере-\nкомпенс.", fontsize=9, color="0.4")
    ax.set_xlabel("Расстройка \u03bd, %")
    ax.set_ylabel("U_н / U_н.макс")
    ax.set_xlim(-30, 30); ax.set_ylim(0, 1.1)
    ax.grid(True, color="0.93")
    _save(fig, "fig_resonance_curve.png")


def fig_resistive_grounding():
    """Л9: резистивное заземление — схема и векторная диаграмма токов."""
    fig, axes = plt.subplots(1, 2, figsize=(9.0, 3.6))
    ax = axes[0]
    ax.plot(0.6, 2.0, "ko", ms=5)
    ys = [2.6, 2.0, 1.4]; cols = ["tab:red", "tab:green", "tab:blue"]
    for y, c in zip(ys, cols):
        ax.plot([0.6, 4.2], [y, y], color=c, lw=2)
        ax.plot([3.6, 3.6], [y, 0.8], color=c, lw=1, ls=":")
        ax.plot([3.5, 3.7], [0.8, 0.8], color=c, lw=3)
    ax.plot([0.6, 0.6], [2.6, 1.4], color="0.3", lw=2)
    ax.plot([0.6, 0.6], [2.0, 1.3], color="tab:red", lw=2)
    ax.add_patch(Rectangle((0.45, 0.85), 0.3, 0.45, fill=False, ec="tab:red", lw=2))
    ax.text(0.85, 1.05, "R_N", color="tab:red", fontsize=11)
    ax.plot([0.2, 4.2], [0.5, 0.5], color="0.3", lw=2)
    ax.plot([0.6, 0.6], [0.85, 0.5], color="tab:red", lw=2)
    ax.set_title("Заземление через резистор R_N", fontsize=10)
    _clean(ax, (0, 4.8), (0.2, 3.0))
    # векторная диаграмма
    ax = axes[1]
    _arrow(ax, 0, -1.0, "tab:purple"); ax.text(0.08, -0.6, "U_N", color="tab:purple", fontsize=12)
    _arrow(ax, 0, 0.9, "tab:blue");   ax.text(-0.35, 0.7, "I_C", color="tab:blue", fontsize=12)
    _arrow(ax, 0.9, 0.0, "tab:red");  ax.text(0.55, -0.18, "I_R", color="tab:red", fontsize=12)
    _arrow(ax, 0.9, 0.9, "tab:green", lw=2.4); ax.text(0.7, 1.0, "I_зам", color="tab:green", fontsize=11)
    ax.axhline(0, color="0.85", lw=0.6); ax.axvline(0, color="0.85", lw=0.6)
    ax.set_title("Токи I_C, I_R, I_зам", fontsize=10)
    _clean(ax, (-0.7, 1.3), (-1.3, 1.3))
    _save(fig, "fig_resistive_grounding.png")


if __name__ == "__main__":
    fig_neutral_modes()
    fig_symmetrical_components()
    fig_ozz_vectors()
    fig_zero_seq_circuit()
    fig_isolated_net()
    fig_arc_overvoltage()
    fig_compensation()
    fig_resonance_curve()
    fig_resistive_grounding()
    print("=== ВСЕ РИСУНКИ (нейтрали) ГОТОВЫ ===")
