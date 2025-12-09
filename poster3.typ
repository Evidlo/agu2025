#set page(
    width: 36in,
    height: 24in,
    margin: 0pt,
)

#set text(
    font: "New Computer Modern",
    size: 24pt,
)

// Define colors matching the poster
#let navy = rgb("#092264")
#let purple = rgb("#373773")
#let cloud = rgb("#5277a1")
#let peach = rgb("#faac86")
#let lpeach = rgb("#fdd4c0")

#grid(
    columns: (25%, 50%, 25%),
    rows: (12%, 2%, 1fr),

    // Row 1, Column 1: Diagonal stripes
    box(
        {
            let x = -10%
            let dx = 22%

            for (i, col) in (navy, navy, purple, cloud, peach, lpeach).enumerate() {
                place(
                    top + left,
                    polygon(
                        fill: col,
                        (x + i*dx + 0%, 0%),
                        (x + i*dx + dx + 1%, 0%),
                        (x + i*dx + 1%, 100%),
                        (x + i*dx + -dx, 100%),
                    )
                )
            }
        }
    ),

    // --- Title ---
    block(
        width: 100%,
        height: 100%,
        fill: lpeach,
        align(center + horizon)[
            #text(
                size: 100%,
                weight: "bold",
                [Efficient Uncertainty Quantification for\ Iterative Retrieval of Exospheric Density]
            )
        ]
    ),

    // --- Logos ---
    block(
        fill: lpeach,
        inset: 10%,
        grid(
            columns: (1fr, 1fr),
            column-gutter: 5%,
            row-gutter: 0%,
            // NASA logo placeholder
            image("nasa.svg", height:100%),
            // University logo placeholder
            image("illinois.svg", height:100%),
        )
    ),

    // --- Authors ---
    grid.cell(
        align: center + horizon,
        colspan: 3,
        text(
            size: 1.75em,
            style: "italic",
            fill: rgb("#444444"),
            [Evan Widloski and Lara Waldrop — University of Illinois Urbana-Champaign, Electrical and Computer Engineering]
        )
    ),

    // --- Content ---
    grid.cell(
        colspan: 3,
        block(
            width: 100%,
            height: 100%,
            fill: white,
            inset: 1in,
            {
                set text(size: 1.3em)

                [
                    = Introduction

                    Add your content sections here...

                    = Methods

                    = Results

                    = Conclusion
                ]
            }
        )
    ),
)
