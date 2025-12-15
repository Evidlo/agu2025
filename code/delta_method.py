#!/usr/bin/env python3
# Simple nonlinear regression problem to test uncertainty quantification
# via implicit function theorem and delta method
#
#  Find best fitting `x`
#  given
#       y = a·x + n ∈ ℕ^M
#  where
#       n ∈ Gaussian(0, Σ),

import scienceplots
import matplotlib.pyplot as plt
plt.style.use('science')
import torch as t
import math
from tqdm import tqdm

# ----- Setup -----

d = {'device': 'cuda'}

# sample data
M = 1
# number of trials (for Monte Carlo approaches)
N = 2000
x = 5 * t.ones((1, N), **d)

# Squared forward model
# This is approximately linear in neighborhood f(x)±σ
def forward_sqr(x):
    return 10 * x**2

# Quarter circle forward model
# This is not approximately linear
def forward_circ(x):
    return t.sqrt(7**2 - x**2)

# Polynomial forward model
# This is not approximately linear
def forward_poly(x):
    return -(x - 5)**3 - (x - 5)

# Exponential forward model (Braverman, 2021)
# This is not approximately linear
def forward_exp(x):
    return 1.75**x

forward = forward_poly
xlim = (2.5, 7.5)

# noisy measurements
noise = t.normal(t.zeros((M, N), **d), σ:=t.sqrt(t.tensor(20, **d)))
y = forward(x * t.ones((1, N), **d)) + noise


# ----- Monte Carlo Variance Estimation -----
# Compute σ² by Monte Carlo simulation
# via iterative reconstruction

def loss_fn(y, x_hat):
    return t.sum((y - forward(x_hat))**2) / y.nelement()

iterations = 200
t.manual_seed(4)
x_hat = t.rand((1, N), requires_grad=True, **d)
optim = t.optim.Adam([x_hat], lr=1e-0)

loss_hist = []
# for _ in range(iterations):
for _ in (bar:=tqdm(range(iterations))):
    optim.zero_grad()
    loss = loss_fn(y, x_hat)
    loss.backward()
    loss_hist.append(float(loss))
    optim.step()
    bar.set_description(f'Loss = {float(loss)}')

# ----- Implicit Function Theorem Variance Estimation -----
# Compute σ² by IFT - focus only on first of N trials

# IFT Term 1: Hessian
h_x = t.func.hessian(loss_fn, 1)(y[:, 0], x_hat[:, 0])
h_x_inv = t.inverse(h_x)

# IFT Term 2: Jacobian
j_y, j_x = t.func.jacrev(loss_fn, (0, 1))(y[:, 0], x_hat[:, 0])

# Compute mixed partial d²L/dxdy using nested jacobian
j_x = lambda y_var: t.func.jacrev(loss_fn, argnums=1)(y_var, x_hat[:, 0])
j_xy = t.func.jacrev(j_x)(y[:, 0])

# Overall retrieval Jacobian
j_R = -h_x_inv @ j_xy

# X̂ uncertainty
Σ_x = j_R @ (t.eye(M, **d) * σ**2) @ j_R.T

# ----- Laplace Approximation Variance Estimation -----
# Compute σ² via Laplace approximation - inverse Hessian approach
# The correct formula relates to the IFT via the structure of j_xy
# For the loss L = (1/M) Σ(y - f(x))², we have:
# j_xy represents how the gradient changes with y
# The full formula should be: Σ_x = H^(-1) @ j_xy @ Σ_noise @ j_xy^T @ H^(-T)
# Which simplifies to the IFT formula when computed correctly
#
# Simple Laplace (just inverse Hessian) - this is INCORRECT for this problem:
Σ_x_laplace_simple = σ**2 * h_x_inv
#
# Correct Laplace (equivalent to IFT):
Σ_x_laplace = h_x_inv @ j_xy @ (t.eye(M, **d) * σ**2) @ j_xy.T @ h_x_inv

print(f'MC Iterative μ:', float(x_hat.mean()))
print('\n--- x̂ Uncertainty ---')
print(f'           MC Iterative σ²: {float(σm:=x_hat.var()):.3e}')
print(f'                    IFT σ²: {float(σi:=Σ_x):.3e}')
print(f'  Laplace (full formula) σ²: {float(σl:=Σ_x_laplace):.3e}')
print(f'Laplace (simple H^-1 only) σ²: {float(σls:=Σ_x_laplace_simple):.3e}')

print(f'\nError vs MC:')
print(f'  IFT:              {float((σi - σm)/σm) * 100:+.2f}%')
print(f'  Laplace (full):   {float((σl - σm)/σm) * 100:+.2f}%')
print(f'  Laplace (simple): {float((σls - σm)/σm) * 100:+.2f}%')
print(f'\nIFT vs Laplace (full) difference: {float(abs(σi - σl)/max(abs(σl), 1e-10)) * 100:+.2f}%')

# ----- Plotting -----
# %% plot

import matplotlib
matplotlib.use('Agg')
from matplotlib.gridspec import GridSpec
from matplotlib.patches import ConnectionPatch, Arrow
from scipy.stats import gaussian_kde
a = lambda arr: arr.detach().cpu().numpy()

xlim_inner, ylim_inner = (float(x_hat.min()), float(x_hat.max())), (float(y.min()), float(y.max()))

# --- Monte Carlo Plot ---

plt.close('all')
fig = plt.figure(figsize=(3, 3))
gs = GridSpec(4, 4)

ax_joint = fig.add_subplot(gs[0:3,1:4])
ax_marg_x = fig.add_subplot(gs[3:,1:4])
ax_marg_y = fig.add_subplot(gs[0:3,0])

# center plot

ax_joint.scatter(a(x_hat[0]), a(y[0]))

def draw_annotation(ax):

    ax.annotate(
        "", xytext=(.1, .4), xy=(.5, .4), xycoords='axes fraction',
        arrowprops=dict(shrinkA=0, shrinkB=0, color='grey', arrowstyle="-"),
    )
    ax.annotate(
        "", xytext=(.5, .4), xy=(.5, .1), xycoords='axes fraction',
        arrowprops=dict(shrinkA=0, shrinkB=0, color='grey', arrowstyle="->"),
    )
    ax.annotate(
        "Retrieval", xy=(.1, .2), xycoords='axes fraction', color='grey'
    )


# plot true function
x_true = t.linspace(*xlim, 1000, **d)
y_true = forward(x_true)
x_true, y_true = a(x_true), a(y_true)
ylim = (y_true.min(), y_true.max())
ax_joint.plot(x_true, y_true, 'r-', label='R(y)')
ax_joint.legend()
draw_annotation(ax_joint)
plt.setp(ax_joint.get_xticklabels(), visible=False)
plt.setp(ax_joint.get_yticklabels(), visible=False)
ax_joint.set_xlim(xlim)
ax_joint.set_ylim(ylim)

# x marginal plot

hist_n, hist_bins, _ = ax_marg_x.hist(a(x_hat[0]), bins=30) #, label=r'Reconstructions $\hat{x}$')
# Add kernel density estimation
kde = gaussian_kde(a(x_hat[0]))
x_kde = t.linspace(x_hat.min(), x_hat.max(), 1000, **d)
kde_vals = kde(a(x_kde))
# Scale KDE to match histogram height
kde_scaled = kde_vals * (hist_n.max() / kde_vals.max())
ax_marg_x.plot(a(x_kde), kde_scaled, 'b-', linewidth=2, label='x Posterior')
# ax_marg_x.vlines(a(x), *ax_marg_x.get_ylim(), 'g', label='Truth x')

# ax_marg_x.legend(loc='upper left')
ax_marg_x.set_xlabel(r'$\hat{x}$')
plt.setp(ax_marg_x.get_yticklabels(), visible=False)

# y marginal plot

hist_n, hist_bins, _ = ax_marg_y.hist(a(y[0]), orientation="horizontal", bins=30, label=r'Noisy $y$')
# Add kernel density estimation
kde = gaussian_kde(a(y[0]))
y_kde = t.linspace(*ylim_inner, 1000, **d)
kde_vals = kde(a(y_kde))
# Scale KDE to match histogram height
kde_scaled = kde_vals * (hist_n.max() / kde_vals.max())
ax_marg_y.plot(kde_scaled, a(y_kde), 'b-', linewidth=2)
# ax_marg_y.hlines(a(forward(x[:, 0])), *ax_marg_y.get_xlim(), 'g', label=r'Noiseless $y$')
# ax_marg_y.legend()
ax_marg_y.set_xlabel('y')
plt.setp(ax_marg_y.get_xticklabels(), visible=False)
ax_marg_y.invert_xaxis()
ax_marg_y.set_ylim(ax_joint.get_ylim())
ax_marg_x.set_xlim(ax_joint.get_xlim())

def draw_outset_lines(fig, ax_joint, ax_marg_x, ax_marg_y):

    # marginal plot limits
    y_ylim = ax_marg_y.get_ylim()
    x_xlim = ax_marg_x.get_xlim()

    style = {'color': 'black', 'linewidth': 0.5}

    # marginal y outset plot lines - bottom
    con = ConnectionPatch(
        xyA=(1, 0), coordsA='axes fraction', axesA=ax_marg_y,
        # xyB=(0, 0), coordsB='axes fraction', axesB=ax_joint,
        xyB=(xlim[0], y_ylim[0]), coordsB='data', axesB=ax_joint,
        **style
    )
    fig.add_artist(con)
    ax_joint.axhline(y_ylim[0], xmax=0.1, **style)

    # marginal y outset plot lines - top
    con = ConnectionPatch(
        xyA=(1, 1), coordsA='axes fraction', axesA=ax_marg_y,
        # xyB=(0, 1), coordsB='axes fraction', axesB=ax_joint,
        xyB=(xlim[0], y_ylim[1]), coordsB='data', axesB=ax_joint,
        **style
    )
    fig.add_artist(con)
    ax_joint.axhline(y_ylim[1], xmax=0.1, **style)

    # marginal x outset plot lines - left
    con = ConnectionPatch(
        xyA=(0, 1), coordsA='axes fraction', axesA=ax_marg_x,
        xyB=(x_xlim[0], ylim[0]), coordsB='data', axesB=ax_joint,
        **style
    )
    fig.add_artist(con)
    ax_joint.axvline(x_xlim[0], ymax=0.1, **style)

    # marginal y outset plot lines - right
    con = ConnectionPatch(
        xyA=(1, 1), coordsA='axes fraction', axesA=ax_marg_x,
        xyB=(x_xlim[1], ylim[0]), coordsB='data', axesB=ax_joint,
        **style
    )
    fig.add_artist(con)
    ax_joint.axvline(x_xlim[1], ymax=0.1, **style)

# draw_outset_lines(fig, ax_joint, ax_marg_x, ax_marg_y)

# plt.suptitle("Monte Carlo")
# plt.tight_layout()
plt.savefig('/www/joint_mc.png', dpi=200)

# --- Delta Method + Implicit Function Theorem Plot ---

plt.close('all')
fig = plt.figure(figsize=(3, 3))
gs = GridSpec(4, 4)

ax_joint = fig.add_subplot(gs[0:3,1:4])
ax_marg_x = fig.add_subplot(gs[3,1:4])
ax_marg_y = fig.add_subplot(gs[0:3,0])

# center plot


# plot true function
xxx = ax_joint.plot(x_true, y_true, 'r-', label='R(y)', zorder=1)
ax_joint.scatter(float(x_hat[0, 0]), float(y[0, 0]), color='blue', zorder=10)
plt.setp(ax_joint.get_xticklabels(), visible=False)
plt.setp(ax_joint.get_yticklabels(), visible=False)
ax_joint.set_xlim(xlim)
ax_joint.set_ylim(ylim)

slope = float(t.func.grad(forward)(x_hat[0, 0]))
ax_joint.axline((float(x_hat[0, 0]), float(y[0, 0])), slope=slope, color='lightpink', linestyle='--', label=r'$J_R$')
ax_joint.legend()
draw_annotation(ax_joint)

# x marginal plot

# plot IFT gaussian posterior
x_gaus = t.linspace(x_hat.min(), x_hat.max(), 1000, **d)
# Compute Gaussian PDF: N(x̂, Σ_x)
x_mu = x_hat[0, 0]  # mean of posterior (reconstruction for first trial)
x_sigma_sq = Σ_x.squeeze()  # variance from IFT
xpdf_gaus = (1 / t.sqrt(2 * math.pi * x_sigma_sq)) * t.exp(-0.5 * (x_gaus - x_mu)**2 / x_sigma_sq)
# Scale to match histogram height for visibility
xpdf_scaled = xpdf_gaus * (hist_n.max() / xpdf_gaus.max())
ax_marg_x.plot(a(x_gaus), a(xpdf_scaled), 'b-', linewidth=2, label='Posterior dist. of x')
ax_marg_x.vlines(float(x_hat[0, 0]), *ax_marg_x.get_ylim(), 'b')

# ax_marg_x.legend()
ax_marg_x.set_xlabel(r'$\hat{x}$')
plt.setp(ax_marg_x.get_yticklabels(), visible=False)

# y marginal plot

# ax_marg_y.hlines(a(forward(x)), *[0, 1], 'g', label=r'Noiseless $y$')
ax_marg_y.hlines(a(y[0, 0]), *[0, 1], 'b', label=r'Noisy $y$')

# plot gaussian posterior predictive dist
y_gaus = t.linspace(y.min(), y.max(), 1000, **d)
y_mu = y[0, 0]  # mean of posterior (for first trial)
y_sigma_sq = σ**2  # variance
ypdf_gaus = (1 / t.sqrt(2 * math.pi * y_sigma_sq)) * t.exp(-0.5 * (y_gaus - y_mu)**2 / y_sigma_sq)
# Scale to for visibility
ypdf_scaled = ypdf_gaus * (1 / ypdf_gaus.max())
ax_marg_y.plot(a(ypdf_scaled), a(y_gaus), 'b-', linewidth=2, label='Posterior')

# ax_marg_y.legend()
ax_marg_y.set_xlabel('y')
plt.setp(ax_marg_y.get_xticklabels(), visible=False)
ax_marg_y.invert_xaxis()
ax_marg_y.set_ylim(ax_joint.get_ylim())
ax_marg_x.set_xlim(ax_joint.get_xlim())

# draw_outset_lines(fig, ax_joint, ax_marg_x, ax_marg_y)

# plt.suptitle(f'Delta Method w/ IFT')
# plt.tight_layout()
plt.savefig('/www/joint_ift.png', dpi=200)

plt.close()
plt.semilogy(loss_hist)
plt.ylabel('Loss')
plt.xlabel('Iteration')
plt.title('Loss History')
plt.savefig('/www/loss.png', dpi=200)