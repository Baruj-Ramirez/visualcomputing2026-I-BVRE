import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
import imageio
import io

# ─────────────────────────────────────────────
# 1.  DEFINE THE 2D FIGURE  (homogeneous coords)
# ─────────────────────────────────────────────
# A simple arrow-like star shape defined as vertices (x, y)
def make_star(n_points=5, r_outer=1.0, r_inner=0.45):
    """Return (2, N) array of star vertices in homogeneous 2-D."""
    angles = np.linspace(0, 2 * np.pi, 2 * n_points, endpoint=False) - np.pi / 2
    radii  = np.array([r_outer if i % 2 == 0 else r_inner
                       for i in range(2 * n_points)])
    x = radii * np.cos(angles)
    y = radii * np.sin(angles)
    return np.vstack([x, y, np.ones(len(x))])   # shape (3, N)

# ─────────────────────────────────────────────
# 2.  TRANSFORMATION MATRICES  (3×3 homogeneous)
# ─────────────────────────────────────────────
def translation_matrix(tx, ty):
    return np.array([[1, 0, tx],
                     [0, 1, ty],
                     [0, 0,  1]], dtype=float)

def rotation_matrix(theta):          # theta in radians
    c, s = np.cos(theta), np.sin(theta)
    return np.array([[ c, -s, 0],
                     [ s,  c, 0],
                     [ 0,  0, 1]], dtype=float)

def scaling_matrix(sx, sy):
    return np.array([[sx,  0, 0],
                     [ 0, sy, 0],
                     [ 0,  0, 1]], dtype=float)

def apply_transform(M, pts):
    """Apply 3×3 matrix M to (3, N) homogeneous points."""
    return M @ pts

# ─────────────────────────────────────────────
# 3.  ANIMATION PARAMETERS
# ─────────────────────────────────────────────
N_FRAMES   = 60          # total frames
FPS        = 20          # frames per second in GIF

# Interpolation helpers  (t goes from 0 → 1)
def lerp(a, b, t):
    return a + (b - a) * t

def ease_inout(t):
    """Smooth step: slow start, fast middle, slow end."""
    return t * t * (3 - 2 * t)

# ─────────────────────────────────────────────
# 4.  GENERATE FRAMES
# ─────────────────────────────────────────────
star_pts = make_star()          # original shape

frames = []

for frame in range(N_FRAMES):
    t  = frame / (N_FRAMES - 1)   # 0 … 1
    te = ease_inout(t)             # eased parameter

    # --- Interpolate transform parameters ---
    tx    = lerp(0.0,  2.5, te)         # translate  right
    ty    = lerp(0.0,  1.5, te)         # translate  up
    theta = lerp(0.0,  2 * np.pi, te)   # full 360° rotation
    sx    = lerp(1.0,  2.0, te)         # scale x  ×2
    sy    = lerp(1.0,  0.5, te)         # scale y  ×0.5  (squish)

    # --- Build combined matrix  T · R · S ---
    T = translation_matrix(tx, ty)
    R = rotation_matrix(theta)
    S = scaling_matrix(sx, sy)
    M = T @ R @ S                       # order: scale → rotate → translate

    # Apply to original shape
    transformed = apply_transform(M, star_pts)
    x_t, y_t = transformed[0], transformed[1]

    # --- Draw ---
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_facecolor('#0d0d1a')
    fig.patch.set_facecolor('#0d0d1a')

    # Original shape (ghost)
    ghost = Polygon(np.column_stack([star_pts[0], star_pts[1]]),
                    closed=True, fill=True,
                    facecolor='#ffffff18', edgecolor='#ffffff44', lw=1.5)
    ax.add_patch(ghost)

    # Transformed shape
    poly = Polygon(np.column_stack([x_t, y_t]),
                   closed=True, fill=True,
                   facecolor='#4fc3f7', edgecolor='#ffffff', lw=2,
                   alpha=0.85)
    ax.add_patch(poly)

    # Dots at vertices
    ax.scatter(x_t, y_t, color='white', s=25, zorder=5)

    # Annotations
    ax.set_xlim(-4, 7); ax.set_ylim(-4, 7)
    ax.set_aspect('equal')
    ax.grid(True, color='#ffffff22', linestyle='--', linewidth=0.5)
    ax.tick_params(colors='#aaaaaa')
    for spine in ax.spines.values():
        spine.set_edgecolor('#444444')

    info = (f"Frame {frame+1:02d}/{N_FRAMES}   t={t:.2f}\n"
            f"Translate ({tx:+.2f}, {ty:+.2f})   "
            f"Rotate {np.degrees(theta):.1f}°   "
            f"Scale ({sx:.2f}, {sy:.2f})")
    ax.set_title(info, color='white', fontsize=9, pad=8)
    ax.set_xlabel("x", color='#aaaaaa'); ax.set_ylabel("y", color='#aaaaaa')

    # Save frame to buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100, bbox_inches='tight',
                facecolor=fig.get_facecolor())
    plt.close(fig)
    buf.seek(0)
    frames.append(imageio.v3.imread(buf))

# ─────────────────────────────────────────────
# 5.  EXPORT AS ANIMATED GIF
# ─────────────────────────────────────────────

output_path = "transformation_animation.gif"
imageio.mimsave(output_path, frames, fps=FPS, loop=0)
print(f"GIF saved → {output_path}  ({N_FRAMES} frames @ {FPS} fps)")
