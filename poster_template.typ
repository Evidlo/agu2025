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

    // --- Styles ---
    show heading: set align(center)
    // show heading: set text(
    //     size: 13pt,
    //     weight: "regular",
    // )
    // show heading: smallcaps


    grid(
        columns: (30%, 50%, 20%),
        rows: (15%, auto, 1fr),
        column-gutter: 0%,

        // --- Diagonal Stripes ---
        box(
            {
                let x = -25%
                let dx = 25%

                for (i, col) in (navy, navy, purple, cloud, peach, lpeach).enumerate() {
                    place(
                        top + left,
                        polygon(
                            fill: col,
                            (x + i*dx - 1%, 0%),
                            (x + i*dx + dx, 0%),
                            (x + i*dx + 6%, 100%),
                            (x + i*dx + -dx + 5%, 100%),
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
            // stroke: lpeach,
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
                inset: (top: 0.5in, left: 1in, bottom: 1in, right: 1in),
                {
                    set text(size: 1.3em)
                    body
                }
            )
        ),
    )
}


// --- Example Usage ---
//
//
// #poster(
//     title: [Efficient Uncertainty Quantification for\ Iterative Retrieval of Exospheric Density],
//     title_typeface: "Helvetica",
//     title_size: 2.6em,
//     authors: [Evan Widloski and Lara Waldrop — University of Illinois Urbana-Champaign],
//     logo-left: "nasa.svg",
//     logo-right: "illinois.svg"
// )[#columns(3, gutter: 2em)[
// = Summary
// - foo
// - bar
// = Another Section
// ]]
