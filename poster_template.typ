// Define colors matching the poster
#let navy = rgb("#092264")
#let purple = rgb("#373773")
#let cloud = rgb("#5277a1")
#let peach = rgb("#faac86")
#let lpeach = rgb("#fdd4c0")

// Poster template function
#let poster(
    title: [],
    title_size: 2.0em,
    title_typeface: "New Computer Modern",
    authors: [],
    logo-left: none,
    logo-right: none,
    body
) = {
    grid(
        columns: (25%, 55%, 20%),
        rows: (15%, auto, 1fr),
        column-gutter: 0%,

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
                    size: title_size,
                    font: title_typeface,
                    weight: "bold",
                    title
                )
            ]
        ),

        // --- Logos ---
        block(
            fill: lpeach,
            inset: (top: 20%, bottom: 20%),
            grid(
                columns: (1fr, 1fr),
                column-gutter: 5%,
                row-gutter: 0%,
                // Left logo
                if logo-left != none {
                    image(logo-left, height: 100%, fit: "contain")
                },
                // Right logo
                if logo-right != none {
                    image(logo-right, height: 100%, fit: "contain")
                },
            )
        ),

        // --- Authors ---
        grid.cell(
            align: center + horizon,
            colspan: 3,
            box(
                inset: (top: 25%, bottom: 25%),
                text(
                    size: 1.75em,
                    style: "italic",
                    fill: rgb("#444444"),
                    authors
                )
            )
        ),

        // --- Content ---
        grid.cell(
            colspan: 3,
            block(
                width: 100%,
                height: 100%,
                // fill: white,
                inset: 1in,
                {
                    set text(size: 1.3em)
                    body
                }
            )
        ),
    )
}
