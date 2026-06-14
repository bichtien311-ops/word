# -*- coding: utf-8 -*-
"""Генератор рисунков для пособия «Трансформаторы» (PNG 300 dpi).

Запуск:  .\.venv\Scripts\python.exe figures\gen_figures.py
Рисунки сохраняются рядом со скриптом и вставляются в master через ![](figures/...).
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch, Arc
import schemdraw
import schemdraw.elements as elm

OUT = os.path.dirname(os.path.abspath(__file__))
DPI = 300

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 12,
    "axes.unicode_minus": False,
})


def _save(fig, name):
    fig.savefig(os.path.join(OUT, name), dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print("OK", name)


def _clean(ax, lim_x, lim_y):
    ax.set_xlim(*lim_x); ax.set_ylim(*lim_y)
    ax.set_xticks([]); ax.set_yticks([])
    ax.set_aspect("equal")
    for s in ax.spines.values():
        s.set_visible(False)


# =====================================================================
# МОДУЛЬ I
# =====================================================================

def fig_transformer_device():
    """Л1: принцип действия — магнитопровод, две обмотки, поток."""
    fig, ax = plt.subplots(figsize=(5.6, 4.2))
    # магнитопровод (прямоугольная рамка с окном)
    ax.add_patch(Rectangle((0, 0), 6, 5, fill=False, lw=10, ec="0.4"))
    # обмотка W1 (левый стержень)
    for k in range(5):
        ax.add_patch(Rectangle((0.4, 1.0 + k*0.6), 0.6, 0.35,
                     facecolor="tab:orange", ec="k", lw=0.8))
    # обмотка W2 (правый стержень)
    for k in range(5):
        ax.add_patch(Rectangle((5.0, 1.0 + k*0.6), 0.6, 0.35,
                     facecolor="tab:blue", ec="k", lw=0.8))
    ax.text(0.7, 4.3, "w\u2081", ha="center", fontsize=14, color="tab:orange")
    ax.text(5.3, 4.3, "w\u2082", ha="center", fontsize=14, color="tab:blue")
    # стрелка потока Φ в верхнем ярме
    ax.annotate("", xy=(3.8, 4.6), xytext=(2.2, 4.6),
                arrowprops=dict(arrowstyle="-|>", color="tab:red", lw=2.2))
    ax.text(3.0, 4.85, "\u03a6", color="tab:red", fontsize=15, ha="center")
    # подвод U1 и нагрузка U2
    ax.annotate("U\u2081", xy=(-0.2, 2.5), fontsize=14, ha="right", color="tab:orange")
    ax.annotate("U\u2082", xy=(6.2, 2.5), fontsize=14, ha="left", color="tab:blue")
    _clean(ax, (-1.2, 7.2), (-0.5, 5.6))
    _save(fig, "fig_transformer_device.png")


def fig_core_types():
    """Л2: стержневой и броневой магнитопроводы."""
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.6))
    # Стержневой
    ax = axes[0]
    ax.add_patch(Rectangle((0, 0), 4, 4, fill=False, lw=9, ec="0.4"))
    for k in range(4):
        ax.add_patch(Rectangle((0.35, 0.8 + k*0.7), 0.5, 0.45, facecolor="tab:orange", ec="k", lw=0.6))
        ax.add_patch(Rectangle((3.15, 0.8 + k*0.7), 0.5, 0.45, facecolor="tab:blue", ec="k", lw=0.6))
    ax.set_title("Стержневой", fontsize=12)
    _clean(ax, (-0.6, 4.6), (-0.6, 4.8))
    # Броневой
    ax = axes[1]
    ax.add_patch(Rectangle((0, 0), 5, 4, fill=False, lw=9, ec="0.4"))
    ax.plot([2.5, 2.5], [0, 4], lw=9, color="0.4")  # центральный стержень
    for k in range(4):
        ax.add_patch(Rectangle((2.0, 0.8 + k*0.7), 1.0, 0.45,
                     facecolor="tab:green", ec="k", lw=0.6))
    ax.set_title("Броневой", fontsize=12)
    _clean(ax, (-0.6, 5.6), (-0.6, 4.8))
    _save(fig, "fig_core_types.png")


def fig_hysteresis():
    """Л2: петля гистерезиса B = f(H)."""
    fig, ax = plt.subplots(figsize=(5.0, 4.6))
    H = np.linspace(-1, 1, 400)
    # модель петли
    def loop(H, up):
        return np.tanh(3*(H + (0.18 if up else -0.18)))
    ax.plot(H, loop(H, True), color="tab:blue", lw=2)
    ax.plot(H, loop(H, False), color="tab:blue", lw=2)
    ax.axhline(0, color="0.6", lw=0.8); ax.axvline(0, color="0.6", lw=0.8)
    # обозначения Br, Hc, Bs
    ax.annotate("B\u209b", xy=(1.0, loop(np.array([1.0]), True)[0]), xytext=(0.6, 1.05),
                fontsize=12)
    ax.plot(0, np.tanh(3*0.18), "o", color="tab:red", ms=5)
    ax.annotate("B\u1d63", xy=(0, np.tanh(3*0.18)), xytext=(0.08, 0.62), fontsize=12, color="tab:red")
    Hc = -0.18
    ax.plot(Hc, 0, "o", color="tab:green", ms=5)
    ax.annotate("\u2212H\u1d04", xy=(Hc, 0), xytext=(Hc-0.05, -0.28), fontsize=12, color="tab:green")
    ax.set_xlabel("H, А/м"); ax.set_ylabel("B, Тл")
    ax.set_xlim(-1.1, 1.1); ax.set_ylim(-1.2, 1.2)
    ax.set_xticks([]); ax.set_yticks([])
    _save(fig, "fig_hysteresis.png")


def fig_cooling():
    """Л3: бак с расширителем (упрощённая конструкция)."""
    fig, ax = plt.subplots(figsize=(4.8, 4.6))
    # бак
    ax.add_patch(Rectangle((0, 0), 4, 4, fill=False, lw=2.5, ec="0.3"))
    ax.add_patch(Rectangle((0.2, 0.2), 3.6, 3.4, facecolor="#e8f0ff", ec="none"))  # масло
    ax.text(2, 0.6, "масло", ha="center", fontsize=11, color="tab:blue")
    # активная часть
    ax.add_patch(Rectangle((1.2, 1.2), 1.6, 2.0, fill=False, lw=6, ec="0.45"))
    ax.text(2.0, 2.2, "активная\nчасть", ha="center", va="center", fontsize=9)
    # расширитель
    ax.add_patch(Rectangle((2.6, 4.3), 1.6, 0.7, fill=False, lw=2, ec="0.3"))
    ax.add_patch(Rectangle((2.6, 4.3), 1.6, 0.35, facecolor="#e8f0ff", ec="none"))
    ax.text(3.4, 4.65, "расширитель", ha="center", fontsize=9)
    ax.plot([3.2, 3.2], [4.0, 4.3], lw=2, color="0.3")  # маслопровод
    # ввод
    ax.plot([1.0, 1.0], [4.0, 4.8], lw=3, color="tab:orange")
    ax.text(0.8, 4.9, "ввод ВН", ha="center", fontsize=9, color="tab:orange")
    _clean(ax, (-0.5, 4.8), (-0.4, 5.3))
    _save(fig, "fig_cooling.png")


# =====================================================================
# МОДУЛЬ II
# =====================================================================

def fig_leakage_flux():
    """Л4: основной поток Φ и потоки рассеяния Φσ1, Φσ2."""
    fig, ax = plt.subplots(figsize=(5.6, 4.2))
    ax.add_patch(Rectangle((0, 0), 6, 5, fill=False, lw=10, ec="0.4"))
    for k in range(5):
        ax.add_patch(Rectangle((0.4, 1.0 + k*0.6), 0.6, 0.35, facecolor="tab:orange", ec="k", lw=0.6))
        ax.add_patch(Rectangle((5.0, 1.0 + k*0.6), 0.6, 0.35, facecolor="tab:blue", ec="k", lw=0.6))
    # основной поток (по магнитопроводу)
    ax.annotate("", xy=(3.8, 4.6), xytext=(2.2, 4.6),
                arrowprops=dict(arrowstyle="-|>", color="tab:red", lw=2.2))
    ax.text(3.0, 4.85, "\u03a6", color="tab:red", fontsize=15, ha="center")
    # потоки рассеяния (петли у обмоток)
    ax.add_patch(FancyArrowPatch((0.7, 3.6), (0.7, 2.0), connectionstyle="arc3,rad=0.8",
                 arrowstyle="-|>", color="tab:green", lw=1.6, mutation_scale=12))
    ax.text(1.5, 2.8, "\u03a6\u03c3\u2081", color="tab:green", fontsize=13)
    ax.add_patch(FancyArrowPatch((5.3, 2.0), (5.3, 3.6), connectionstyle="arc3,rad=0.8",
                 arrowstyle="-|>", color="tab:purple", lw=1.6, mutation_scale=12))
    ax.text(4.3, 2.8, "\u03a6\u03c3\u2082", color="tab:purple", fontsize=13)
    _clean(ax, (-0.8, 6.8), (-0.5, 5.6))
    _save(fig, "fig_leakage_flux.png")


def fig_three_winding():
    """Л5: трёхлучевая звезда сопротивлений (трёхобмоточный)."""
    fig, ax = plt.subplots(figsize=(5.0, 4.6))
    # центральный узел
    cx, cy = 0, 0
    ang = {"ВН": 90, "СН": -30, "НН": 210}
    col = {"ВН": "tab:red", "СН": "tab:green", "НН": "tab:blue"}
    for name, a in ang.items():
        ar = np.deg2rad(a)
        x, y = 1.6*np.cos(ar), 1.6*np.sin(ar)
        ax.plot([0, x], [0, y], color=col[name], lw=3)
        # резистор-прямоугольник посередине
        mx, my = 0.8*np.cos(ar), 0.8*np.sin(ar)
        ax.add_patch(Rectangle((mx-0.18, my-0.18), 0.36, 0.36, angle=0,
                     facecolor="white", ec=col[name], lw=2))
        ax.text(1.9*np.cos(ar), 1.9*np.sin(ar), f"X$_{{{name}}}$",
                ha="center", va="center", fontsize=13, color=col[name])
    ax.plot(0, 0, "ko", ms=6)
    _clean(ax, (-2.4, 2.4), (-2.2, 2.4))
    _save(fig, "fig_three_winding.png")


# =====================================================================
# МОДУЛЬ III
# =====================================================================

def fig_kapp_triangle():
    """Л7: треугольник напряжений КЗ (Каппа)."""
    fig, ax = plt.subplots(figsize=(5.2, 4.0))
    # катеты
    Ir = 3.0   # I*r (горизонталь)
    Ix = 2.0   # I*x (вертикаль)
    ax.annotate("", xy=(Ir, 0), xytext=(0, 0),
                arrowprops=dict(arrowstyle="-|>", color="tab:blue", lw=2))
    ax.annotate("", xy=(Ir, Ix), xytext=(Ir, 0),
                arrowprops=dict(arrowstyle="-|>", color="tab:green", lw=2))
    ax.annotate("", xy=(Ir, Ix), xytext=(0, 0),
                arrowprops=dict(arrowstyle="-|>", color="tab:red", lw=2.4))
    ax.text(Ir/2, -0.28, "İ$_к$·r$_к$", color="tab:blue", fontsize=13, ha="center")
    ax.text(Ir+0.12, Ix/2, "jİ$_к$·x$_к$", color="tab:green", fontsize=13, va="center")
    ax.text(Ir/2-0.4, Ix/2+0.25, "U̇$_к$", color="tab:red", fontsize=14)
    # угол φк
    th = np.linspace(0, np.arctan2(Ix, Ir), 30)
    ax.plot(0.8*np.cos(th), 0.8*np.sin(th), color="0.4", lw=1)
    ax.text(0.95, 0.28, "\u03c6\u2096", fontsize=12)
    _clean(ax, (-0.6, Ir+1.0), (-0.7, Ix+0.6))
    _save(fig, "fig_kapp_triangle.png")


def fig_efficiency():
    """Л8: зависимость КПД η = f(β)."""
    fig, ax = plt.subplots(figsize=(6.0, 4.0))
    beta = np.linspace(0.02, 1.2, 200)
    Pxx, Pk, S, cosf = 1.0, 3.0, 100.0, 0.9   # условные о.е.
    eta = 1 - (Pxx + beta**2*Pk) / (beta*S*cosf + Pxx + beta**2*Pk)
    b_opt = np.sqrt(Pxx/Pk)
    ax.plot(beta, eta*100, color="tab:blue", lw=2)
    ax.axvline(b_opt, color="tab:red", ls="--", lw=1.5)
    ax.text(b_opt+0.02, 0.5+ax.get_ylim()[0], f"\u03b2_opt\u2248{b_opt:.2f}",
            color="tab:red", fontsize=11)
    ax.set_xlabel("\u03b2 = I\u2082 / I\u2082\u043d\u043e\u043c")
    ax.set_ylabel("\u03b7, %")
    ax.set_xlim(0, 1.2)
    ax.grid(True, color="0.9")
    _save(fig, "fig_efficiency.png")


def fig_inrush():
    """Л10: бросок тока намагничивания при включении."""
    fig, ax = plt.subplots(figsize=(6.2, 3.6))
    t = np.linspace(0, 0.12, 1000)
    f = 50
    env = 7*np.exp(-t/0.03) + 1.0
    i = env * (1 - np.cos(2*np.pi*f*t)) / 2 * 2  # пикообразный, односторонний
    i = (7*np.exp(-t/0.035)) * (0.5*(1-np.cos(2*np.pi*f*t))) + 0.2*np.sin(2*np.pi*f*t)
    ax.plot(t*1000, i, color="tab:red", lw=1.6)
    ax.axhline(1.0, color="0.6", ls=":", lw=1)
    ax.text(95, 1.15, "I\u043d\u043e\u043c", fontsize=10, color="0.4")
    ax.set_xlabel("t, мс"); ax.set_ylabel("i / I\u043d\u043e\u043c")
    ax.set_xlim(0, 120)
    ax.grid(True, color="0.92")
    _save(fig, "fig_inrush.png")


def fig_shock_current():
    """Л10: ударный ток внезапного КЗ."""
    fig, ax = plt.subplots(figsize=(6.2, 3.6))
    t = np.linspace(0, 0.1, 1000)
    f = 50
    Ik = 1.0
    aper = Ik*np.sqrt(2)*np.exp(-t/0.05)
    per = -Ik*np.sqrt(2)*np.cos(2*np.pi*f*t)
    i = aper + per
    ax.plot(t*1000, i, color="tab:blue", lw=1.6, label="ток КЗ")
    ax.plot(t*1000, aper, color="tab:green", ls="--", lw=1.2, label="апериодическая сост.")
    # ударный ток в районе 10 мс
    idx = np.argmax(i)
    ax.plot(t[idx]*1000, i[idx], "o", color="tab:red")
    ax.annotate("i\u0443\u0434", xy=(t[idx]*1000, i[idx]), xytext=(t[idx]*1000+6, i[idx]),
                fontsize=12, color="tab:red")
    ax.set_xlabel("t, мс"); ax.set_ylabel("i / I\u043d\u043e\u043c")
    ax.legend(fontsize=9, frameon=False, loc="lower right")
    ax.grid(True, color="0.92")
    _save(fig, "fig_shock_current.png")


def fig_clock_groups():
    """Л9: часовой циферблат групп соединения (0 и 11)."""
    fig, ax = plt.subplots(figsize=(4.6, 4.6))
    th = np.linspace(0, 2*np.pi, 200)
    ax.plot(np.cos(th), np.sin(th), color="0.5", lw=1.2)
    for h in range(12):
        a = np.deg2rad(90 - h*30)
        ax.text(1.15*np.cos(a), 1.15*np.sin(a), str(h if h else 12),
                ha="center", va="center", fontsize=10, color="0.4")
    # ВН (минутная) на 12
    ax.annotate("", xy=(0, 0.9), xytext=(0, 0),
                arrowprops=dict(arrowstyle="-|>", color="tab:red", lw=2.5))
    ax.text(0.05, 1.0, "ВН (12)", color="tab:red", fontsize=11)
    # НН группа 11 -> на 11 часов
    a11 = np.deg2rad(90 - 11*30)
    ax.annotate("", xy=(0.75*np.cos(a11), 0.75*np.sin(a11)), xytext=(0, 0),
                arrowprops=dict(arrowstyle="-|>", color="tab:blue", lw=2.5))
    ax.text(0.85*np.cos(a11)-0.2, 0.85*np.sin(a11)+0.1, "НН (11)", color="tab:blue", fontsize=11)
    ax.plot(0, 0, "ko", ms=5)
    _clean(ax, (-1.4, 1.4), (-1.4, 1.4))
    _save(fig, "fig_clock_groups.png")


def fig_connections_ydz():
    """Л9: схемы соединения обмоток — звезда, треугольник, зигзаг."""
    fig, axes = plt.subplots(1, 3, figsize=(8.4, 3.2))
    # Звезда
    ax = axes[0]
    for a in (90, 210, 330):
        ar = np.deg2rad(a)
        ax.plot([0, np.cos(ar)], [0, np.sin(ar)], color="tab:blue", lw=2.5)
    ax.plot(0, 0, "ko", ms=5)
    ax.set_title("Звезда (Y)", fontsize=12)
    _clean(ax, (-1.4, 1.4), (-1.3, 1.4))
    # Треугольник
    ax = axes[1]
    pts = np.array([[0, 1], [-0.87, -0.5], [0.87, -0.5], [0, 1]])
    ax.plot(pts[:, 0], pts[:, 1], color="tab:green", lw=2.5)
    ax.set_title("Треугольник (\u0394)", fontsize=12)
    _clean(ax, (-1.4, 1.4), (-1.1, 1.4))
    # Зигзаг
    ax = axes[2]
    for a in (90, 210, 330):
        ar = np.deg2rad(a)
        x1, y1 = 0.55*np.cos(ar), 0.55*np.sin(ar)
        ar2 = np.deg2rad(a+40)
        x2, y2 = x1 + 0.55*np.cos(ar2), y1 + 0.55*np.sin(ar2)
        ax.plot([0, x1], [0, y1], color="tab:purple", lw=2.5)
        ax.plot([x1, x2], [y1, y2], color="tab:orange", lw=2.5)
    ax.plot(0, 0, "ko", ms=5)
    ax.set_title("Зигзаг (Z)", fontsize=12)
    _clean(ax, (-1.5, 1.5), (-1.4, 1.5))
    _save(fig, "fig_connections_ydz.png")


# =====================================================================
# СХЕМЫ ЦЕПЕЙ (schemdraw)
# =====================================================================

def fig_vd_xx():
    """Л6: векторная диаграмма режима холостого хода."""
    fig, ax = plt.subplots(figsize=(5.2, 5.2))
    d_ang = np.deg2rad(18)
    ax.annotate("", xy=(1.0, 0.0), xytext=(0, 0),
                arrowprops=dict(arrowstyle="-|>", color="tab:red", lw=2))
    ax.text(1.08, 0.04, "\u03a6\u2098", color="tab:red", fontsize=14)
    ax.annotate("", xy=(0.85*np.cos(d_ang), 0.85*np.sin(d_ang)), xytext=(0, 0),
                arrowprops=dict(arrowstyle="-|>", color="tab:green", lw=2))
    ax.text(0.95*np.cos(d_ang), 0.95*np.sin(d_ang)+0.06, "I\u0307\u2080",
            color="tab:green", fontsize=14)
    th = np.linspace(0, d_ang, 30)
    ax.plot(0.35*np.cos(th), 0.35*np.sin(th), color="gray", lw=1)
    ax.text(0.42*np.cos(d_ang/2), 0.42*np.sin(d_ang/2), "\u03b4", fontsize=12)
    ax.annotate("", xy=(0.0, -0.9), xytext=(0, 0),
                arrowprops=dict(arrowstyle="-|>", color="tab:blue", lw=2))
    ax.text(0.16, -0.85, "E\u0307\u2081 = E\u0307\u2082", color="tab:blue", fontsize=13)
    ax.annotate("", xy=(0.0, 0.9), xytext=(0, 0),
                arrowprops=dict(arrowstyle="-|>", color="tab:purple", lw=2))
    ax.text(0.16, 0.85, "U\u0307\u2081", color="tab:purple", fontsize=14)
    ax.axhline(0, color="0.7", lw=0.6); ax.axvline(0, color="0.7", lw=0.6)
    _clean(ax, (-1.25, 1.25), (-1.25, 1.25))
    _save(fig, "fig_vd_xx.png")


def fig_ext_char():
    """Л8: внешние характеристики U2 = f(I2)."""
    fig, ax = plt.subplots(figsize=(6.0, 4.2))
    beta = np.linspace(0, 1.2, 50)
    ax.plot(beta, 1.0 - 0.018*beta, "-",  color="tab:blue",  lw=2, label="активная (cos\u03c6\u2082 = 1)")
    ax.plot(beta, 1.0 - 0.06*beta,  "--", color="tab:red",   lw=2, label="активно-индуктивная")
    ax.plot(beta, 1.0 + 0.03*beta,  "-.", color="tab:green", lw=2, label="активно-ёмкостная")
    ax.axhline(1.0, color="0.8", lw=0.8, ls=":")
    ax.set_xlabel("I\u2082 / I\u2082\u043d\u043e\u043c")
    ax.set_ylabel("U\u2082 / U\u2082\u043d\u043e\u043c")
    ax.set_xlim(0, 1.2); ax.set_ylim(0.9, 1.05)
    ax.legend(loc="lower left", fontsize=10, frameon=False)
    ax.grid(True, color="0.9")
    _save(fig, "fig_ext_char.png")


def fig_t_equiv():
    """Л5: Т-образная схема замещения."""
    with schemdraw.Drawing(file=os.path.join(OUT, "fig_t_equiv.png"),
                           dpi=DPI, show=False) as d:
        d.config(fontsize=12)
        d += elm.Dot().label("U\u0307\u2081", loc="left")
        d += (L1 := elm.Line().up().length(0.5))
        d += elm.Resistor().right().label("r\u2081")
        d += elm.Inductor().right().label("x\u2081")
        d += elm.Dot()
        d.push()
        d += elm.Resistor().down().label("r\u2080", loc="bottom")
        d += elm.Inductor().down().label("x\u2080", loc="bottom")
        d += elm.Dot()
        d += elm.Line().left().length(d.unit)
        d.pop()
        d += elm.Resistor().right().label("r\u2082\u2032")
        d += elm.Inductor().right().label("x\u2082\u2032")
        d += elm.Dot().label("U\u0307\u2082\u2032", loc="right")
        d += elm.Line().down().length(0.5)
        d += elm.Line().left().tox(L1.start)
        d += elm.Line().up().toy(L1.start)
    print("OK fig_t_equiv.png")


def fig_xx_test():
    """Л6: схема опыта холостого хода."""
    with schemdraw.Drawing(file=os.path.join(OUT, "fig_xx_test.png"),
                           dpi=DPI, show=False) as d:
        d.config(fontsize=12)
        d += (src := elm.SourceSin().up().label("U\u2081"))
        d += elm.Line().right().length(1)
        d += (A := elm.MeterA().right().label("A"))
        d += elm.Line().right().length(0.5)
        d += (T := elm.Transformer(loop=False).right().label("ХХ: I\u2082 = 0", loc="top"))
        # вольтметр на вторичной (разомкнута)
        d += elm.Line().at(T.s2).right().length(0.8)
        d += elm.MeterV().down().label("V")
        d += elm.Line().left().tox(T.s1)
        d += elm.Line().up().toy(T.s1)
        # замыкание первичной цепи
        d += elm.Line().at(T.p2).down().toy(src.start)
        d += elm.Line().left().tox(src.start)
    print("OK fig_xx_test.png")


def fig_kz_test():
    """Л7: схема опыта короткого замыкания."""
    with schemdraw.Drawing(file=os.path.join(OUT, "fig_kz_test.png"),
                           dpi=DPI, show=False) as d:
        d.config(fontsize=12)
        d += (src := elm.SourceSin().up().label("U\u043a"))
        d += elm.Line().right().length(1)
        d += elm.MeterA().right().label("A")
        d += elm.Line().right().length(0.5)
        d += (T := elm.Transformer(loop=False).right().label("КЗ: U\u2082 = 0", loc="top"))
        # вторичная замкнута накоротко
        d += elm.Line().at(T.s2).right().length(0.6)
        d += elm.Line().down().toy(T.s1)
        d += elm.Line().left().tox(T.s1)
        d += elm.Line().up().toy(T.s1)
        d += elm.Line().at(T.p2).down().toy(src.start)
        d += elm.Line().left().tox(src.start)
    print("OK fig_kz_test.png")


def fig_ct_connection():
    """Л7: включение трансформатора тока (ТТ)."""
    with schemdraw.Drawing(file=os.path.join(OUT, "fig_ct_connection.png"),
                           dpi=DPI, show=False) as d:
        d.config(fontsize=12)
        # первичная линия в рассечку
        d += elm.Line().right().length(1.5).label("Л1 (сеть)", loc="left")
        d += (T := elm.Transformer(loop=False).right())
        d += elm.Line().right().length(1.5).label("Л2", loc="right")
        # вторичная на амперметр
        d += elm.Line().at(T.s1).down().length(1)
        d += elm.MeterA().right().label("A (реле, 5 А)")
        d += elm.Line().up().toy(T.s2)
        d += elm.Line().left().tox(T.s2)
    print("OK fig_ct_connection.png")


def fig_autotransformer():
    """Л9: схема автотрансформатора."""
    with schemdraw.Drawing(file=os.path.join(OUT, "fig_autotransformer.png"),
                           dpi=DPI, show=False) as d:
        d.config(fontsize=12)
        d += elm.Dot().label("ВН", loc="left")
        d += (top := elm.Line().right().length(1))
        d += (L := elm.Inductor2(loops=4).down().label("последоват.\nобмотка", loc="left"))
        d += (tap := elm.Dot().label("СН/НН", loc="right"))
        d += (L2 := elm.Inductor2(loops=4).down().label("общая\nобмотка", loc="left"))
        d += elm.Dot()
        d += elm.Line().left().length(1)
        d += elm.Line().up().toy(top.end)
        # вывод СН вправо от tap
        d += elm.Line().at(tap.center).right().length(1.2).label("НН", loc="right")
    print("OK fig_autotransformer.png")


if __name__ == "__main__":
    # matplotlib
    fig_transformer_device()
    fig_core_types()
    fig_hysteresis()
    fig_cooling()
    fig_leakage_flux()
    fig_three_winding()
    fig_vd_xx()
    fig_kapp_triangle()
    fig_ext_char()
    fig_efficiency()
    fig_connections_ydz()
    fig_clock_groups()
    fig_inrush()
    fig_shock_current()
    # schemdraw
    fig_t_equiv()
    fig_xx_test()
    fig_kz_test()
    fig_ct_connection()
    fig_autotransformer()
    print("=== ВСЕ РИСУНКИ ГОТОВЫ ===")
