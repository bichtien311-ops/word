# -*- coding: utf-8 -*-
"""Генератор рисунков для пособия «Трансформаторы» (PNG 300 dpi).

POC: 3 показательных рисунка
  fig_t_equiv.png  — Т-образная схема замещения (Лекция 5)
  fig_vd_xx.png    — векторная диаграмма холостого хода (Лекция 6)
  fig_ext_char.png — внешние характеристики U2=f(I2) (Лекция 8)
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import schemdraw
import schemdraw.elements as elm

OUT = os.path.dirname(os.path.abspath(__file__))
DPI = 300

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 12,
    "axes.unicode_minus": False,
})


def fig_t_equiv():
    """Т-образная схема замещения трансформатора."""
    with schemdraw.Drawing(file=os.path.join(OUT, "fig_t_equiv.png"),
                           dpi=DPI, show=False) as d:
        d.config(fontsize=12)
        # Вход U1 (слева)
        d += elm.Dot().label("U\u0307\u2081", loc="left")
        d += (L1 := elm.Line().up().length(0.5))
        # Верхняя ветвь: r1, x1 -> узел A
        d += elm.Resistor().right().label("r\u2081")
        d += elm.Inductor().right().label("x\u2081")
        d += (A := elm.Dot())
        # Шунтирующая ветвь намагничивания вниз: r0, x0
        d.push()
        d += elm.Resistor().down().label("r\u2080", loc="bottom")
        d += elm.Inductor().down().label("x\u2080", loc="bottom")
        d += elm.Dot()
        d += (Bmid := elm.Line().left().length(d.unit))  # к нижней шине влево
        d.pop()
        # Продолжение верхней ветви: r2', x2' -> выход
        d += elm.Resistor().right().label("r\u2082\u2032")
        d += elm.Inductor().right().label("x\u2082\u2032")
        d += elm.Dot().label("U\u0307\u2082\u2032", loc="right")
        d += elm.Line().down().length(0.5)
        # Нижняя шина обратно ко входу
        d += elm.Line().left().tox(L1.start)
        d += elm.Line().up().toy(L1.start)


def fig_vd_xx():
    """Векторная диаграмма режима холостого хода."""
    fig, ax = plt.subplots(figsize=(5.2, 5.2))
    ax.set_aspect("equal")

    def arrow(x, y, txt, color, tx=None, ty=None):
        ax.annotate("", xy=(x, y), xytext=(0, 0),
                    arrowprops=dict(arrowstyle="-|>", color=color, lw=2))
        ax.text(tx if tx is not None else x, ty if ty is not None else y,
                txt, color=color, fontsize=14, ha="center", va="center")

    # Φ_m по оси +x
    arrow(1.0, 0.0, "", "tab:red", )
    ax.text(1.08, 0.04, "\u03a6\u2098", color="tab:red", fontsize=14)
    # I0 опережает Φ_m на угол δ (показан увеличенным ~18°)
    d_ang = np.deg2rad(18)
    arrow(0.85*np.cos(d_ang), 0.85*np.sin(d_ang), "", "tab:green")
    ax.text(0.95*np.cos(d_ang), 0.95*np.sin(d_ang)+0.06, "I\u0307\u2080",
            color="tab:green", fontsize=14)
    # дуга угла δ
    th = np.linspace(0, d_ang, 30)
    ax.plot(0.35*np.cos(th), 0.35*np.sin(th), color="gray", lw=1)
    ax.text(0.42*np.cos(d_ang/2), 0.42*np.sin(d_ang/2), "\u03b4", fontsize=12)
    # E1=E2 вниз (-90°)
    arrow(0.0, -0.9, "", "tab:blue")
    ax.text(0.16, -0.85, "E\u0307\u2081 = E\u0307\u2082", color="tab:blue", fontsize=13)
    # U1 вверх (+90°), = -E1
    arrow(0.0, 0.9, "", "tab:purple")
    ax.text(0.16, 0.85, "U\u0307\u2081", color="tab:purple", fontsize=14)

    lim = 1.25
    ax.set_xlim(-lim, lim); ax.set_ylim(-lim, lim)
    ax.axhline(0, color="0.7", lw=0.6); ax.axvline(0, color="0.7", lw=0.6)
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "fig_vd_xx.png"), dpi=DPI)
    plt.close(fig)


def fig_ext_char():
    """Внешние характеристики U2 = f(I2) при трёх типах нагрузки."""
    fig, ax = plt.subplots(figsize=(6.0, 4.2))
    beta = np.linspace(0, 1.2, 50)
    U_act = 1.0 - 0.018*beta            # активная: лёгкое снижение
    U_ind = 1.0 - 0.06*beta             # активно-индуктивная: круче вниз
    U_cap = 1.0 + 0.03*beta             # активно-ёмкостная: вверх

    ax.plot(beta, U_act, "-",  color="tab:blue",   lw=2, label="активная (cos\u03c6\u2082 = 1)")
    ax.plot(beta, U_ind, "--", color="tab:red",    lw=2, label="активно-индуктивная")
    ax.plot(beta, U_cap, "-.", color="tab:green",  lw=2, label="активно-ёмкостная")

    ax.axhline(1.0, color="0.8", lw=0.8, ls=":")
    ax.set_xlabel("I\u2082 / I\u2082\u043d\u043e\u043c")
    ax.set_ylabel("U\u2082 / U\u2082\u043d\u043e\u043c")
    ax.set_xlim(0, 1.2); ax.set_ylim(0.9, 1.05)
    ax.legend(loc="lower left", fontsize=10, frameon=False)
    ax.grid(True, color="0.9")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "fig_ext_char.png"), dpi=DPI)
    plt.close(fig)


if __name__ == "__main__":
    fig_t_equiv()
    print("OK fig_t_equiv")
    fig_vd_xx()
    print("OK fig_vd_xx")
    fig_ext_char()
    print("OK fig_ext_char")
