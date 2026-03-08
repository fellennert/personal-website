# Felix Lennert — Personal Website

Portfolio and academic site built with [Quarto](https://quarto.org): research output, teaching materials, and data projects (web scraping, ML classifiers, RAG, visualizations).

## Contents

- **Home** — Background and what I’m looking for (data analyst / data science roles)
- **About** — More about me
- **Coding Projects** — Reports and dashboards (e.g. Boston Marathon/Strava analysis, RAG assistant for teaching)
- **Research** — Publications and working papers
- **Teaching** — Course materials and resources

## Build

From the repo root, with [Quarto](https://quarto.org/docs/get-started/) installed:

```bash
quarto render
```

Output is in `_site/`.

## Deploy

The site can be published to **GitHub Pages** (or any static host) by serving the `_site/` directory. If you use GitHub Actions, add a workflow that runs `quarto render` and deploys `_site/` to the `gh-pages` branch or to GitHub Pages.

## License

Site content and code are mine unless otherwise noted; reuse as you like with attribution.
