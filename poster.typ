#import "poster_template.typ": *
#import "@preview/codetastic:0.2.2": qrcode

#set page(
    width: 36in,
    height: 27in,
    margin: 0pt,
)

#set text(
    // font: "New Computer Modern",
    // font: "Inter",
    font: "Helvetica",
    size: 22pt,
)

// ----- Settings -----

// #set par(hanging-indent: 1.5em)
#show math.equation.where(block: false): box

#set math.equation(block: true)

// highlight
#let hl(content) = {
    box(
        outset: 0.5em,
        fill: lpeach,
    )[#content]
}

// simple box
#let boxx(content) = {
    box(
        stroke: black,
        inset: 1em
    )[#content]
}

// vertical text
#let vert(body) = rotate(body, -90deg, reflow:true)

// ----- Template Init -----

#poster(
    title: [Efficient Uncertainty Quantification for\ Iterative Retrieval of Exospheric Density],
    // title_typeface: "Inter Display",
    title_typeface: "Inter",
    // title_typeface: "Helvetica",
    title_size: 2.6em,
    authors: [Evan Widloski and Lara Waldrop — University of Illinois Urbana-Champaign],
    logo-left: "nasa.svg",
    logo-right: "illinois.svg"
// )[#columns(3, gutter: 2em)[
)[#grid(columns: (1fr, 1fr, 1fr), column-gutter: 2em, [

// ----- First Column -----


#figure(boxx([

#set align(left)

= Overview

- Exospheric retrieval is classic tomography problem
- Motivated by launch of Carruthers spacecraft
- Tomographic inverse problem \ Given $y=F(x) + epsilon$, \ find $hat(x) = R(y) = arg min_x ||y - F(x)||$

- Delta method uncertainty quantification (UQ)
    - Goal: Put error bars around estimate $hat(x)$
    - i.e.: Gaussian approximation of $P(X|Y)$

- Jacobian $J_R$ is needed for many UQ methods
    - Expensive when $R$ is iterative optimization

#hl([New idea: Implicit function theorem (IFT) can approximate $J_R$ efficiently, speeding up UQ])

]))


= Formalization of Inverse Problem

#figure(image("figures/flowchart.svg"))

- Inverse problems can often be formalized as
    - $x$ - true system state
    - $F_0$ - actual forward model and physics (unknown)
    - $epsilon$ - additive instrument noise
    - $R$ - retrieval algorithm
    - $F$ - numerical forward model (approximation of $F_0$)


- Uncertainties can be classified into two categories
    - *Epistemic (systemic) uncertainty* - e.g. discrepancy between nature $F$ and numerical approximation $F_0$
    - *Aleatoric uncertainty* - error in measurement constraints $y$ due to noise $epsilon$

- Generally retrieval process $R$ is posed as iterative optimization

#math.equation($
    hat(x) = R(y) = arg min_x ||y - F(x)||
$)



],

// ----- Second Column -----

[

= Overview of UQ Methods

#set text(size: 22pt)

#table(
    columns: 5,
    inset: 0.5em,
    align: center + horizon,
    table.cell(stroke:none)[], [*Delta Method*~@delta], [Monte Carlo], [Post Hoc @posthoc], [Bayesian MCMC],
    // table.cell(stroke:none)[], [#image("figures/montecarlo.svg")], [#image("figures/deltamethod.svg")],

    // [Steps],
    // table.cell(align: top + left,[
    //     #set text(size: 20pt)
    //     1. Generate $y$ ensemble\ (e.g. bootstrap)
    //     2. Reconstruct ensemble
    // ]),
    // table.cell(align: top + left,[
    //     #set text(size: 20pt)
    //     1. hello
    //     2. world
    // ]),
    // table.cell(align: top + left,[
    //     #set text(size: 20pt)
    //     1. hello
    //     2. world
    // ]),
    // table.cell(align: top + left,[
    //     #set text(size: 20pt)
    //     1. hello
    //     2. world
    // ]),

    [Compute Cost],
    [*Low*], [High], [High (once)], [Extremely high],

    [Highly\ Nonlinear?],
    [*No*], [Yes], [Yes], [Yes],

    [Posterior],
    [*Local Gaussian*], [Discrete approx.], [GMM], [Full Posterior],

    [Speedup w/ IFT?],
    [*Yes*], [No], [Yes], [Yes],
    // FIXME - verify MCMC speedup w/ IFT

)

= Delta Method (WIP)

- Assumes Gaussian Noise
- Assumes noise small relative to local curvature of $R(y)$
  $R$ is well-conditioned

= Jacobian of Iterative Functions

#grid(columns: (4fr, 1fr), column-gutter: 1em, [
    - Jacobians of iterative functions hard to compute
        - Recursive nature leads to complex graphs
        - E.g. gradient descent

    #math.equation($
        arg min_x underbrace(||y - F(x)||, "Loss" cal(L)(x, y))
    $)

    #math.equation($
        x_(i+1) ← x_i + eta nabla_x cal(L)(x_i, y)
    $)

    - Graph grows linearly with \# iterations $arrow.r.long$

    - IFT can save us!

    #boxx([
        Assuming

        1. Loss $cal(L)$ is twice-differentiable
        2. We can find $hat(x)$ s.t. $cal(L)(hat(x), y) = 0$

        Then

        #hl(
            $J_R = underbrace(
            -(nabla_(x^2) cal(L)(hat(x), y))^(-1) nabla_(x y) cal(L)(hat(x), y),
            "no dependence on" R
            )
            $
        )
    ])
], [
    #figure(
        image("figures/torchgraph_iterations.svg"),
        supplement: none,
        caption: "PyTorch graph grows linearly with # iterations."
    )
]
)

],

// ----- Third Column -----

[

= Numerical Experiments (WIP)

#math.equation($
    y = F(x) + epsilon \
    F(x) = -(x - 5)^3 - (x - 5)
$)

#grid(columns: 3, align: center + horizon, row-gutter: 1em,
    "", "Monte Carlo", "Delta Method",
    vert("Low Noise"),
    image(width: 100%, "figures/joint_mc_small.png"),
    image(width: 100%, "figures/joint_ift_small.png"),
    vert("High Noise"),
    image(width: 100%, "figures/joint_mc_large.png"),
    image(width: 100%, "figures/joint_ift_large.png"),
    // image("figures/joint_mc_poly.png"),
    // image("figures/joint_ift_poly.png"),
)


#[
    #set text(size:20pt)
    #bibliography("refs.bib", style: "american-physics-society")
]


#figure([
    #grid(columns: 2, align: center + horizon,
        [
            #set align(center + horizon)
            #qrcode(quiet-zone: 0, width: 7em, "https://github.com/evidlo/agu2025")

            #text(size:18pt, [https://github.com/evidlo/agu2025])
        ],
        [
            #image("figures/carruthers_logo.svg")
        ]
    )
])

]

)]
