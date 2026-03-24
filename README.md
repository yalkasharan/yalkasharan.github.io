# Assignment 2: The Great Crime Shift

An interactive data story exploring how COVID-19 transformed crime patterns in San Francisco.

## Files

| File | Description |
|------|-------------|
| `index.html` | Main story page (GitHub Pages ready) |
| `viz1_crime_divergence.png` | Static chart - COVID crime inversion |
| `viz1_crime_divergence.svg` | Vector version for print |
| `viz2_vehicle_theft_map.html` | Plotly choropleth - geographic shift |
| `viz3_crime_trajectory.html` | Plotly time series - long-term trajectory |
| `crime_story_visualizations.py` | Python script to regenerate all visualizations |
| `.nojekyll` | Tells GitHub Pages not to use Jekyll |

## View Locally

```bash
python -m http.server 8000
# Open http://localhost:8000
```

## Deploy to GitHub Pages

1. Push this folder to a GitHub repository
2. Go to Settings > Pages
3. Set source to "Deploy from a branch" > main > / (root)
4. Wait 1-2 minutes, then visit `https://USERNAME.github.io/REPO`

## Regenerate Visualizations

```bash
python crime_story_visualizations.py
```

Requires: pandas, numpy, matplotlib, plotly, requests

## Data Source

San Francisco Police Department Incident Reports (2003-2025)
- 1,048,575 records
- Merged historical (2003-2018) and current (2018-present) datasets
