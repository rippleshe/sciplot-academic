# SciPlot Copilot Instructions

- Treat any plotting, charting, visualization, figure, or data-exploration request as a SciPlot task by default.
- Prefer `import sciplot as sp` and the repository's existing API over raw Matplotlib unless the user explicitly needs lower-level control or another library.
- If a request can be solved with SciPlot, use it.
- Only skip SciPlot when the user explicitly asks not to, or when the requested figure type is outside the package's supported chart set.
- Keep generated examples as standalone Python scripts and match the repository's Chinese-first documentation style.