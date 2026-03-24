"""
San Francisco Crime Story Visualizations
=========================================
"The Great Crime Shift: How Empty Streets Changed What Got Stolen"

Generates 3 visualizations:
1. Static diverging bar chart (matplotlib) - COVID crime divergence
2. Choropleth map (Folium) - Vehicle theft geographic shift
3. Interactive time series (Plotly) - Long-term trajectory
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json

# =============================================================================
# CONFIGURATION - Visual Consistency
# =============================================================================
COLORS = {
    'increase': '#D62728',      # Red for increases
    'decrease': '#1F77B4',      # Blue for decreases
    'vehicle_theft': '#8B0000', # Dark red (signature color)
    'burglary': '#FF6B6B',      # Light red
    'larceny': '#4A90D9',       # Blue
    'assault': '#2E86AB',       # Darker blue
    'robbery': '#5DA5DA',       # Medium blue
    'neutral': '#7F7F7F',       # Gray
    'background': '#FAFAFA',    # Light background
}

FONT_FAMILY = 'DejaVu Sans'
TITLE_SIZE = 14
LABEL_SIZE = 11
CAPTION_SIZE = 10

# =============================================================================
# LOAD AND PREPARE DATA
# =============================================================================
print("Loading data...")
df = pd.read_csv('assignments/merged_crime_data_2003_2025.csv')

# Normalize district names (fix case inconsistencies)
df['Police_District'] = df['Police_District'].str.upper()

print(f"Loaded {len(df):,} records from {df['Year'].min()} to {df['Year'].max()}")

# =============================================================================
# VISUALIZATION 1: Diverging Bar Chart - COVID Crime Divergence
# =============================================================================
print("\n[1/3] Creating diverging bar chart...")

# Calculate % change from 2019 to 2020
categories = ['Larceny/Theft', 'Assault', 'Robbery', 'Vehicle Theft', 'Burglary', 'Arson']
changes = []

for cat in categories:
    count_2019 = len(df[(df['Year'] == 2019) & (df['Unified_Category'] == cat)])
    count_2020 = len(df[(df['Year'] == 2020) & (df['Unified_Category'] == cat)])
    pct_change = ((count_2020 - count_2019) / count_2019) * 100
    changes.append({
        'category': cat,
        'change': pct_change,
        'color': COLORS['increase'] if pct_change > 0 else COLORS['decrease']
    })

changes_df = pd.DataFrame(changes).sort_values('change')

# Create figure with more width for labels
fig, ax = plt.subplots(figsize=(12, 7), facecolor=COLORS['background'])
ax.set_facecolor(COLORS['background'])

# Add background shading to distinguish crime types
ax.axhspan(-0.5, 2.5, facecolor=COLORS['decrease'], alpha=0.08)  # Blue zone for proximity crimes
ax.axhspan(2.5, 5.5, facecolor=COLORS['increase'], alpha=0.08)  # Red zone for property crimes

# Plot horizontal bars
bars = ax.barh(
    changes_df['category'],
    changes_df['change'],
    color=changes_df['color'],
    edgecolor='white',
    linewidth=1,
    height=0.65
)

# Add value labels on the bars (inside or outside based on size)
for bar, val in zip(bars, changes_df['change']):
    x_pos = bar.get_width()
    ha = 'left' if x_pos >= 0 else 'right'
    offset = 2 if x_pos >= 0 else -2
    ax.text(
        x_pos + offset, bar.get_y() + bar.get_height()/2,
        f'{val:+.1f}%',
        va='center', ha=ha,
        fontsize=12, fontweight='bold',
        color=bar.get_facecolor()
    )

# Add zero line
ax.axvline(x=0, color='black', linewidth=1.5, linestyle='-', alpha=0.4)

# Labels and title
ax.set_xlabel('% Change from 2019 to 2020', fontsize=LABEL_SIZE, fontfamily=FONT_FAMILY, labelpad=10)
ax.set_title(
    'COVID Inverted San Francisco\'s Crime Profile',
    fontsize=16, fontweight='bold', fontfamily=FONT_FAMILY,
    pad=20
)

# Add subtitle
ax.text(
    0.5, 1.02,
    'Proximity crimes dropped while opportunistic property crimes surged',
    transform=ax.transAxes, ha='center', fontsize=11,
    style='italic', color=COLORS['neutral']
)

# Style
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_visible(False)
ax.tick_params(left=False, labelsize=12)
ax.set_xlim(-55, 75)
ax.set_ylim(-0.5, 5.5)

# Add category labels on the right margin
ax.text(
    1.02, 0.22, 'PROXIMITY\nCRIMES',
    transform=ax.transAxes, fontsize=10, fontweight='bold',
    color=COLORS['decrease'], va='center', ha='left',
    bbox=dict(boxstyle='round,pad=0.4', facecolor=COLORS['decrease'], alpha=0.15, edgecolor='none')
)
ax.text(
    1.02, 0.72, 'PROPERTY\nCRIMES',
    transform=ax.transAxes, fontsize=10, fontweight='bold',
    color=COLORS['increase'], va='center', ha='left',
    bbox=dict(boxstyle='round,pad=0.4', facecolor=COLORS['increase'], alpha=0.15, edgecolor='none')
)

# Add dividing line between crime types
ax.axhline(y=2.5, color='gray', linewidth=1, linestyle='--', alpha=0.5)

plt.tight_layout()
plt.subplots_adjust(right=0.85)  # Make room for right-side labels
plt.savefig('assignments/viz1_crime_divergence.png', dpi=150, bbox_inches='tight', facecolor=COLORS['background'])
plt.savefig('assignments/viz1_crime_divergence.svg', bbox_inches='tight', facecolor=COLORS['background'])
print("  > Saved: viz1_crime_divergence.png/svg")

# =============================================================================
# VISUALIZATION 2: Plotly Choropleth Map - Vehicle Theft by District
# =============================================================================
print("\n[2/3] Creating choropleth map...")

import requests

# Calculate vehicle theft change by district
vt_2019 = df[(df['Year'] == 2019) & (df['Unified_Category'] == 'Vehicle Theft')].groupby('Police_District').size()
vt_2020 = df[(df['Year'] == 2020) & (df['Unified_Category'] == 'Vehicle Theft')].groupby('Police_District').size()

district_changes = pd.DataFrame({'2019': vt_2019, '2020': vt_2020}).fillna(0)
district_changes['change_pct'] = ((district_changes['2020'] - district_changes['2019']) / district_changes['2019'] * 100).round(1)

# Download official SFPD GeoJSON shapefile
GEOJSON_URL = 'https://raw.githubusercontent.com/suneman/socialdata2025/main/files/sfpd.geojson'
try:
    geojson_data = requests.get(GEOJSON_URL, timeout=10).json()
    print("  > Downloaded SFPD GeoJSON shapefile")
except:
    # Fallback: use embedded simplified boundaries if download fails
    print("  > Using embedded district boundaries (download failed)")
    geojson_data = {
        "type": "FeatureCollection",
        "features": [
            {"type": "Feature", "id": "BAYVIEW", "properties": {"DISTRICT": "BAYVIEW"}, "geometry": {"type": "Polygon", "coordinates": [[[-122.365, 37.708], [-122.405, 37.708], [-122.410, 37.725], [-122.400, 37.745], [-122.380, 37.755], [-122.360, 37.745], [-122.355, 37.725], [-122.365, 37.708]]]}},
            {"type": "Feature", "id": "CENTRAL", "properties": {"DISTRICT": "CENTRAL"}, "geometry": {"type": "Polygon", "coordinates": [[[-122.390, 37.788], [-122.425, 37.788], [-122.425, 37.810], [-122.390, 37.810], [-122.390, 37.788]]]}},
            {"type": "Feature", "id": "INGLESIDE", "properties": {"DISTRICT": "INGLESIDE"}, "geometry": {"type": "Polygon", "coordinates": [[[-122.410, 37.708], [-122.470, 37.708], [-122.475, 37.730], [-122.465, 37.750], [-122.430, 37.755], [-122.410, 37.745], [-122.410, 37.708]]]}},
            {"type": "Feature", "id": "MISSION", "properties": {"DISTRICT": "MISSION"}, "geometry": {"type": "Polygon", "coordinates": [[[-122.400, 37.745], [-122.430, 37.745], [-122.435, 37.765], [-122.425, 37.775], [-122.405, 37.775], [-122.400, 37.760], [-122.400, 37.745]]]}},
            {"type": "Feature", "id": "NORTHERN", "properties": {"DISTRICT": "NORTHERN"}, "geometry": {"type": "Polygon", "coordinates": [[[-122.425, 37.785], [-122.455, 37.785], [-122.460, 37.800], [-122.445, 37.808], [-122.425, 37.808], [-122.420, 37.795], [-122.425, 37.785]]]}},
            {"type": "Feature", "id": "PARK", "properties": {"DISTRICT": "PARK"}, "geometry": {"type": "Polygon", "coordinates": [[[-122.435, 37.758], [-122.480, 37.758], [-122.485, 37.775], [-122.475, 37.785], [-122.445, 37.785], [-122.435, 37.770], [-122.435, 37.758]]]}},
            {"type": "Feature", "id": "RICHMOND", "properties": {"DISTRICT": "RICHMOND"}, "geometry": {"type": "Polygon", "coordinates": [[[-122.455, 37.772], [-122.515, 37.772], [-122.515, 37.790], [-122.485, 37.800], [-122.460, 37.800], [-122.455, 37.785], [-122.455, 37.772]]]}},
            {"type": "Feature", "id": "SOUTHERN", "properties": {"DISTRICT": "SOUTHERN"}, "geometry": {"type": "Polygon", "coordinates": [[[-122.378, 37.765], [-122.410, 37.765], [-122.415, 37.785], [-122.405, 37.798], [-122.380, 37.798], [-122.375, 37.780], [-122.378, 37.765]]]}},
            {"type": "Feature", "id": "TARAVAL", "properties": {"DISTRICT": "TARAVAL"}, "geometry": {"type": "Polygon", "coordinates": [[[-122.470, 37.715], [-122.510, 37.715], [-122.515, 37.745], [-122.505, 37.760], [-122.475, 37.760], [-122.465, 37.740], [-122.470, 37.715]]]}},
            {"type": "Feature", "id": "TENDERLOIN", "properties": {"DISTRICT": "TENDERLOIN"}, "geometry": {"type": "Polygon", "coordinates": [[[-122.405, 37.778], [-122.420, 37.778], [-122.422, 37.788], [-122.415, 37.792], [-122.405, 37.792], [-122.402, 37.785], [-122.405, 37.778]]]}}
        ]
    }

# Prepare data for Plotly choropleth
SF_DISTRICTS = ['CENTRAL', 'SOUTHERN', 'BAYVIEW', 'MISSION', 'PARK',
                'RICHMOND', 'INGLESIDE', 'TARAVAL', 'NORTHERN', 'TENDERLOIN']

map_df = district_changes.reset_index()
map_df.columns = ['district', '2019', '2020', 'change_pct']
map_df = map_df[map_df['district'].isin(SF_DISTRICTS)]

# Add absolute counts for hover
map_df['2019'] = map_df['2019'].astype(int)
map_df['2020'] = map_df['2020'].astype(int)

# Create Plotly choropleth map
import plotly.express as px

fig_map = px.choropleth_map(
    map_df,
    geojson=geojson_data,
    locations='district',
    featureidkey='properties.DISTRICT',
    color='change_pct',
    color_continuous_scale='RdBu_r',  # Red = increase, Blue = decrease (reversed)
    range_color=(-10, 90),  # Symmetric-ish around small values
    map_style='carto-positron',
    zoom=11.3,
    center={'lat': 37.7749, 'lon': -122.4194},
    opacity=0.75,
    labels={'change_pct': '% Change'},
    hover_data={'district': True, '2019': True, '2020': True, 'change_pct': ':.1f'}
)

fig_map.update_layout(
    title=dict(
        text='<b>Vehicle Theft Change by District (2019 vs 2020)</b>',
        font=dict(size=18, family='Arial'),
        x=0.5
    ),
    margin={'r': 0, 't': 50, 'l': 0, 'b': 0},
    height=600,
    coloraxis_colorbar=dict(
        title='% Change',
        ticksuffix='%',
        len=0.6
    )
)

# Add annotation
fig_map.add_annotation(
    x=0.02, y=0.02,
    xref='paper', yref='paper',
    text='Red = Increase | Blue = Decrease<br>Click districts for details',
    showarrow=False,
    font=dict(size=11, color='#444'),
    align='left',
    bgcolor='rgba(255,255,255,0.8)',
    bordercolor='#ccc',
    borderwidth=1
)

# Save as HTML
fig_map.write_html('assignments/viz2_vehicle_theft_map.html', include_plotlyjs='cdn')
print("  > Saved: viz2_vehicle_theft_map.html")

# =============================================================================
# VISUALIZATION 3: Interactive Plotly - Long-term Trajectory
# =============================================================================
print("\n[3/3] Creating interactive time series...")

# Calculate normalized indices (2019 = 100) for key crime types
crime_types = ['Vehicle Theft', 'Burglary', 'Larceny/Theft', 'Robbery', 'Assault']
yearly_data = {}

for crime in crime_types:
    yearly = df[df['Unified_Category'] == crime].groupby('Year').size()
    baseline = yearly.get(2019, 1)
    normalized = (yearly / baseline * 100).round(1)
    yearly_data[crime] = normalized

# Create combined dataframe
index_df = pd.DataFrame(yearly_data)
index_df = index_df[index_df.index >= 2015]  # Focus on recent years

# Create Plotly figure
fig = go.Figure()

# Color mapping
color_map = {
    'Vehicle Theft': COLORS['vehicle_theft'],
    'Burglary': COLORS['burglary'],
    'Larceny/Theft': COLORS['larceny'],
    'Robbery': COLORS['robbery'],
    'Assault': COLORS['assault'],
}

# Add traces - all visible by default, users can toggle via legend
for crime in crime_types:
    fig.add_trace(go.Scatter(
        x=index_df.index,
        y=index_df[crime],
        name=crime,
        mode='lines+markers',
        line=dict(color=color_map[crime], width=2.5),
        marker=dict(size=8),
        visible=True,
        hovertemplate=f'<b>{crime}</b><br>Year: %{{x}}<br>Index: %{{y:.1f}}<extra></extra>'
    ))

# Add baseline reference line at 100 (2019 level)
fig.add_hline(
    y=100,
    line_dash="dash",
    line_color="gray",
    annotation_text="2019 Baseline",
    annotation_position="bottom right"
)

# Add COVID annotation
fig.add_vline(
    x=2020,
    line_dash="dot",
    line_color="gray",
    annotation_text="COVID-19",
    annotation_position="top"
)

# Add shaded region for COVID period
fig.add_vrect(
    x0=2020, x1=2021,
    fillcolor="rgba(128,128,128,0.1)",
    layer="below",
    line_width=0
)

# Update layout with Week 6 patterns
fig.update_layout(
    title=dict(
        text='<b>The Lasting Shift: Crime Levels Relative to 2019</b><br><sup>Index: 2019 = 100 | Click legend to toggle crime types</sup>',
        font=dict(size=18, family=FONT_FAMILY),
        x=0.5
    ),
    xaxis=dict(
        title='Year',
        tickmode='linear',
        dtick=1,
        gridcolor='#E5E5E5',
        rangeslider=dict(visible=True, thickness=0.05),  # Add range slider
        range=[2015, 2025]
    ),
    yaxis=dict(
        title='Index (2019 = 100)',
        gridcolor='#E5E5E5',
        range=[30, 180],
        zeroline=False
    ),
    plot_bgcolor='white',
    paper_bgcolor='white',
    hovermode='x unified',
    legend=dict(
        orientation='h',
        yanchor='bottom',
        y=1.02,
        xanchor='center',
        x=0.5,
        bgcolor='rgba(255,255,255,0.9)',
        bordercolor='#E5E5E5',
        borderwidth=1
    ),
    # Add dropdown for quick filtering
    updatemenus=[
        dict(
            type='dropdown',
            direction='down',
            x=0.0,
            y=1.15,
            showactive=True,
            buttons=[
                dict(
                    label='All Crime Types',
                    method='update',
                    args=[{'visible': [True] * len(crime_types)}]
                ),
                dict(
                    label='Property Crimes',
                    method='update',
                    args=[{'visible': [True, True, True, False, False]}]
                ),
                dict(
                    label='Violent Crimes',
                    method='update',
                    args=[{'visible': [False, False, False, True, True]}]
                ),
                dict(
                    label='Vehicle Theft Only',
                    method='update',
                    args=[{'visible': [True, False, False, False, False]}]
                ),
            ]
        )
    ],
    margin=dict(b=80, t=100)
)

# Add annotation for key insight - Vehicle theft peak
vt_peak_year = index_df['Vehicle Theft'].idxmax()
vt_peak_value = index_df['Vehicle Theft'].max()

fig.add_annotation(
    x=vt_peak_year,
    y=vt_peak_value,
    text=f"Vehicle theft peaks<br>at {vt_peak_value:.0f}% of 2019",
    showarrow=True,
    arrowhead=2,
    arrowcolor=COLORS['vehicle_theft'],
    arrowsize=1,
    arrowwidth=2,
    font=dict(size=11, color=COLORS['vehicle_theft']),
    bgcolor='white',
    bordercolor=COLORS['vehicle_theft'],
    borderwidth=1,
    borderpad=4
)

# Add annotation for Larceny collapse
lt_min_year = index_df['Larceny/Theft'].idxmin()
lt_min_value = index_df['Larceny/Theft'].min()

fig.add_annotation(
    x=lt_min_year,
    y=lt_min_value,
    text=f"Larceny drops to<br>{lt_min_value:.0f}% of 2019",
    showarrow=True,
    arrowhead=2,
    arrowcolor=COLORS['larceny'],
    arrowsize=1,
    arrowwidth=2,
    font=dict(size=10, color=COLORS['larceny']),
    bgcolor='white',
    bordercolor=COLORS['larceny'],
    borderwidth=1,
    borderpad=4,
    ay=40  # Offset arrow down
)

# Save
fig.write_html('assignments/viz3_crime_trajectory.html', include_plotlyjs='cdn')
print("  > Saved: viz3_crime_trajectory.html")

# =============================================================================
# SUMMARY
# =============================================================================
print("\n" + "=" * 60)
print("VISUALIZATION FILES CREATED:")
print("=" * 60)
print("1. viz1_crime_divergence.png/svg  - Static bar chart")
print("2. viz2_vehicle_theft_map.html    - Interactive Folium map")
print("3. viz3_crime_trajectory.html     - Interactive Plotly chart")
print("\nAll files saved to: assignments/")
print("=" * 60)
