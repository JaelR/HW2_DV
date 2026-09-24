# app_s11_compare.py
#
# Assignment:
# Pick one dataset and create three charts of the same question
# using different channel choices.
#
# Run from Anaconda Prompt or the VS Code terminal:
# conda activate dataviz
# cd "YOUR_ASSIGNMENT_FOLDER"
# python -m streamlit run app_s11_compare.py

from pathlib import Path

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt


# ------------------------------------------------------------
# PAGE CONFIGURATION
# ------------------------------------------------------------
st.set_page_config(
    page_title="S11 Simulation vs. Measurement",
    page_icon="📡",
    layout="wide"
)

st.title("Tri-Band Feed Horn: Simulated and Measured $S_{11}$")
st.caption(
    "A visualization-encoding comparison for a circular feed horn antenna."
)


# ------------------------------------------------------------
# DATA DESCRIPTION FOR THE ASSIGNMENT
# ------------------------------------------------------------
with st.expander("Dataset and research context", expanded=True):
    st.markdown(
        """
        **Dataset.** This app compares the simulated and measured \(S_{11}\)
        responses of a proposed circular feed horn antenna. The simulated response
        was obtained during antenna design, while the measured response was obtained
        in an anechoic-chamber test.

        The feed horn was developed through simulation to evaluate antenna
        performance parameters. This visualization focuses only on the
        \(S_{11}\) parameter, also called the reflection coefficient or return loss.
        More-negative \(S_{11}\) values indicate lower reflected power and better
        impedance matching.

        **Design requirement.** The target criterion is:

        \[
        S_{11} \leq -15\ \mathrm{dB}
        \]

        **Target tri-band operation.**

        - Band 1: 1.40–1.47 GHz
        - Band 2: 1.55–1.65 GHz
        - Band 3: 1.80–1.86 GHz

        **Underlying visualization question.**
        *How consistently do the simulated and anechoic-chamber measured \(S_{11}\)
        responses satisfy the \(-15\) dB criterion within the three intended
        frequency subbands?*
        """
    )


# ------------------------------------------------------------
# FILE LOCATIONS
# ------------------------------------------------------------
# Change this directory only if your two files are elsewhere.
directory = Path(
    "E:/TESISDOCTORADO/Pythontests/Feed_pattern/"
    "Angel-simulations/sim-may2024/"
)

simulation_path = directory / "S11.txt"
measurement_path = directory / "s11_sim_measure.txt"


# ------------------------------------------------------------
# HELPER FUNCTION: LOAD TWO-COLUMN S11 FILE
# ------------------------------------------------------------
@st.cache_data
def load_s11_data(file_path, source_name):
    """
    Reads a whitespace-separated text file with:
    column 1 = frequency in Hz
    column 2 = S11 in dB

    It automatically ignores blank lines and lines beginning with #.
    """

    df = pd.read_csv(
        file_path,
        sep=r"\s+",
        header=None,
        names=["frequency_hz", "s11_db"],
        usecols=[0, 1],
        comment="#",
        engine="python"
    )

    # Ensure numeric values and remove invalid rows if any exist.
    df["frequency_hz"] = pd.to_numeric(df["frequency_hz"], errors="coerce")
    df["s11_db"] = pd.to_numeric(df["s11_db"], errors="coerce")
    df = df.dropna()

    # Convert to GHz to make the x-axis readable.
    df["frequency_ghz"] = df["frequency_hz"] / 1e9
    df["source"] = source_name

    return df


# ------------------------------------------------------------
# LOAD THE TWO DATASETS
# ------------------------------------------------------------
try:
    simulation_df = load_s11_data(simulation_path, "Simulation")
except FileNotFoundError:
    st.error(
        f"Simulation file not found:\n\n`{simulation_path}`\n\n"
        "Check the directory and confirm that `S11.txt` exists."
    )
    st.stop()
except Exception as error:
    st.error(f"Could not read the simulation file: {error}")
    st.stop()

try:
    measurement_df = load_s11_data(measurement_path, "Anechoic-chamber measurement")
except FileNotFoundError:
    st.error(
        f"Measurement file not found:\n\n`{measurement_path}`\n\n"
        "Check the filename. If your measurement file has another name, update "
        "`measurement_path` near the top of this script."
    )
    st.stop()
except Exception as error:
    st.error(f"Could not read the measurement file: {error}")
    st.stop()


# Combine the files into one long-format dataset.
s11_df = pd.concat(
    [simulation_df, measurement_df],
    ignore_index=True
)

# Sort so each line is drawn smoothly from low to high frequency.
s11_df = s11_df.sort_values(["source", "frequency_ghz"])


# ------------------------------------------------------------
# DEFINE TRI-BAND OPERATING RANGES
# ------------------------------------------------------------
bands = pd.DataFrame({
    "band": ["Band 1", "Band 2", "Band 3"],
    "start_ghz": [1.40, 1.55, 1.80],
    "end_ghz": [1.47, 1.65, 1.86],
    "frequency_range": [
        "1.40–1.47 GHz",
        "1.55–1.65 GHz",
        "1.80–1.86 GHz"
    ]
})

# Colors selected to be distinct and readable.
source_scale = alt.Scale(
    domain=["Simulation", "Anechoic-chamber measurement"],
    range=["#2166AC", "#D6604D"]
)

band_scale = alt.Scale(
    domain=["Band 1", "Band 2", "Band 3"],
    range=["#B8E0D2", "#C9D8F0", "#F8D6A3"]
)

# Frequency domain based on the requested operating range and data extent.
x_min = min(1.35, s11_df["frequency_ghz"].min())
x_max = max(1.90, s11_df["frequency_ghz"].max())

# Keep the y-axis consistent between all three charts.
y_min = min(-40, s11_df["s11_db"].min() - 2)
y_max = max(0, s11_df["s11_db"].max() + 2)

x_encoding = alt.X(
    "frequency_ghz:Q",
    title="Frequency (GHz)",
    scale=alt.Scale(domain=[x_min, x_max]),
    axis=alt.Axis(format=".2f", grid=True)
)

y_encoding = alt.Y(
    "s11_db:Q",
    title="S11 (dB)",
    scale=alt.Scale(domain=[y_min, y_max]),
    axis=alt.Axis(grid=True)
)

tooltip_fields = [
    alt.Tooltip("source:N", title="Data source"),
    alt.Tooltip("frequency_ghz:Q", title="Frequency (GHz)", format=".4f"),
    alt.Tooltip("s11_db:Q", title="S11 (dB)", format=".2f")
]


# ------------------------------------------------------------
# COMMON CHART LAYERS
# ------------------------------------------------------------
# Requirement at -15 dB
requirement_df = pd.DataFrame({"s11_limit": [-15]})

requirement_line = alt.Chart(requirement_df).mark_rule(
    color="#4D4D4D",
    strokeDash=[7, 5],
    strokeWidth=1.6
).encode(
    y=alt.Y("s11_limit:Q")
)

requirement_text = alt.Chart(
    pd.DataFrame({
        "frequency_ghz": [x_min + 0.01],
        "s11_limit": [-15],
        "label": ["Requirement: S11 ≤ −15 dB"]
    })
).mark_text(
    align="left",
    baseline="bottom",
    dx=4,
    dy=-4,
    color="#4D4D4D",
    fontSize=12
).encode(
    x="frequency_ghz:Q",
    y="s11_limit:Q",
    text="label:N"
)

# Shaded subband intervals
band_regions = alt.Chart(bands).mark_rect(
    opacity=0.22
).encode(
    x=alt.X(
        "start_ghz:Q",
        scale=alt.Scale(domain=[x_min, x_max])
    ),
    x2="end_ghz:Q",
    y=alt.value(y_min),
    y2=alt.value(y_max),
    color=alt.Color(
        "band:N",
        title="Target subbands",
        scale=band_scale
    ),
    tooltip=[
        alt.Tooltip("band:N", title="Subband"),
        alt.Tooltip("frequency_range:N", title="Frequency range"),
        alt.Tooltip("start_ghz:Q", title="Start (GHz)", format=".2f"),
        alt.Tooltip("end_ghz:Q", title="End (GHz)", format=".2f")
    ]
)

# Labels centered on each shaded band
band_labels = alt.Chart(bands).mark_text(
    baseline="top",
    dy=8,
    color="#333333",
    fontSize=12,
    fontWeight="bold"
).encode(
    x=alt.X(
        "start_ghz:Q",
        scale=alt.Scale(domain=[x_min, x_max])
    ),
    x2="end_ghz:Q",
    y=alt.value(y_max),
    text="band:N"
)


# ------------------------------------------------------------
# SIDEBAR CONTROLS
# ------------------------------------------------------------
st.sidebar.header("Controls")

show_raw_data = st.sidebar.checkbox("Show raw data preview", value=False)

selected_sources = st.sidebar.multiselect(
    "Show response",
    options=["Simulation", "Anechoic-chamber measurement"],
    default=["Simulation", "Anechoic-chamber measurement"]
)

filtered_df = s11_df[s11_df["source"].isin(selected_sources)]

if filtered_df.empty:
    st.warning("Select at least one response in the sidebar.")
    st.stop()


# ------------------------------------------------------------
# DATA PREVIEW
# ------------------------------------------------------------
if show_raw_data:
    st.subheader("Data preview")
    st.dataframe(
        filtered_df[
            ["source", "frequency_hz", "frequency_ghz", "s11_db"]
        ].head(20),
        use_container_width=True
    )


# ------------------------------------------------------------
# THREE CHARTS FOR THE ASSIGNMENT
# ------------------------------------------------------------
st.header("Three Encodings of the Same Question")

st.markdown(
    """
    Each chart below represents the same variables—frequency, \(S_{11}\), and
    data source—but changes the visual encoding used to distinguish simulation
    from measurement or communicate the operating subbands.
    """
)


# ============================================================
# CHART 1: BEST / STRONGEST ENCODING
# ============================================================
st.subheader("Chart 1 — Position + Color: Direct Comparison")

simulation_line = alt.Chart(
    filtered_df[filtered_df["source"] == "Simulation"]
).mark_line(
    color="#2166AC",
    strokeWidth=2.8
).encode(
    x=x_encoding,
    y=y_encoding,
    tooltip=tooltip_fields
)

measurement_line = alt.Chart(
    filtered_df[filtered_df["source"] == "Anechoic-chamber measurement"]
).mark_line(
    color="#D6604D",
    strokeWidth=2.8
).encode(
    x=x_encoding,
    y=y_encoding,
    tooltip=tooltip_fields
)

source_legend = alt.Chart(
    pd.DataFrame({
        "source": ["Simulation", "Anechoic-chamber measurement"],
        "x": [x_min, x_min],
        "y": [y_max, y_max]
    })
).mark_line().encode(
    color=alt.Color(
        "source:N",
        title="Response",
        scale=source_scale
    )
)

chart_1 = (
    band_regions
    + simulation_line
    + measurement_line
    + requirement_line
    + requirement_text
    + band_labels
    + source_legend
).properties(
    width=850,
    height=430,
    title=alt.Title(
        "Simulated and Measured S11 Across the Three Target Bands",
        subtitle=(
            "Compare response level and agreement using vertical position; "
            "shaded areas show the operating intervals."
        ),
        anchor="start"
    )
).configure_axis(
    labelFontSize=12,
    titleFontSize=14,
    gridColor="#D9D9D9"
).configure_legend(
    orient="top",
    labelFontSize=12,
    titleFontSize=12
).interactive()

st.altair_chart(chart_1, use_container_width=True)

st.markdown(
    """
    **Encoding justification.** This is the strongest chart for the scientific
    comparison. Frequency and \(S_{11}\) use position on aligned Cartesian axes.
    Position along a common scale is highly accurate for comparing exact response
    levels, locating resonant minima, and judging whether either response falls
    below the \(-15\) dB criterion. Hue distinguishes the two nominal data sources:
    blue for simulation and red/orange for the anechoic-chamber measurement.

    **Gestalt/preattentive principle.** **Similarity** is used: all simulated
    values have the same blue hue, while all measured values have the same
    red/orange hue. The viewer can immediately group the two response curves before
    reading individual values.
    """
)


# ============================================================
# CHART 2: LINE STYLE + POSITION
# ============================================================
st.subheader("Chart 2 — Position + Line Style: Grayscale-Friendly Comparison")

line_style_chart = alt.Chart(filtered_df).mark_line(
    color="#202020",
    strokeWidth=2.8
).encode(
    x=x_encoding,
    y=y_encoding,
    strokeDash=alt.StrokeDash(
        "source:N",
        title="Response",
        scale=alt.Scale(
            domain=["Simulation", "Anechoic-chamber measurement"],
            range=[[1, 0], [8, 4]]
        )
    ),
    tooltip=tooltip_fields
)

chart_2 = (
    band_regions
    + line_style_chart
    + requirement_line
    + requirement_text
    + band_labels
).properties(
    width=850,
    height=430,
    title=alt.Title(
        "S11 Comparison Using Solid and Dashed Line Styles",
        subtitle=(
            "Solid line = simulation; dashed line = anechoic-chamber measurement."
        ),
        anchor="start"
    )
).configure_axis(
    labelFontSize=12,
    titleFontSize=14,
    gridColor="#D9D9D9"
).configure_legend(
    orient="top",
    labelFontSize=12,
    titleFontSize=12
).interactive()

st.altair_chart(chart_2, use_container_width=True)

st.markdown(
    """
    **Encoding justification.** This chart still uses position for the two
    quantitative variables, so frequency and \(S_{11}\) remain precisely readable.
    Instead of hue, it encodes the data source using line texture:
    solid for simulation and dashed for measurement. It is useful when the figure
    may be printed in grayscale or viewed by someone who has difficulty
    distinguishing colors.

    However, line style is generally less immediate than strongly separated hue
    when the two curves overlap or vary rapidly. Therefore, it is a practical,
    accessible alternative, but not as visually fast as Chart 1 for dense data.

    **Gestalt/preattentive principle.** **Similarity** is again used, but through
    texture rather than color. All dashed segments group as the measured response,
    while solid segments group as the simulated response.
    """
)

# ============================================================
# CHART 3: SMALL MULTIPLES WITH MATPLOTLIB
# ============================================================
st.subheader("Chart 3 — Small Multiples: Separate Panels by Data Source")

fig, axes = plt.subplots(
    nrows=1,
    ncols=2,
    figsize=(13, 4.8),
    sharex=True,
    sharey=True
)

source_order = [
    "Simulation",
    "Anechoic-chamber measurement"
]

panel_colors = {
    "Simulation": "#2166AC",
    "Anechoic-chamber measurement": "#D6604D"
}

band_colors = {
    "Band 1": "#B8E0D2",
    "Band 2": "#C9D8F0",
    "Band 3": "#F8D6A3"
}

for ax, source in zip(axes, source_order):

    source_data = filtered_df[
        filtered_df["source"] == source
    ].sort_values("frequency_ghz")

    # Light target-band background regions
    for _, band in bands.iterrows():
        ax.axvspan(
            band["start_ghz"],
            band["end_ghz"],
            color=band_colors[band["band"]],
            alpha=0.45
        )

        ax.text(
            x=(band["start_ghz"] + band["end_ghz"]) / 2,
            y=y_max - 1,
            s=band["band"],
            ha="center",
            va="top",
            fontsize=10,
            fontweight="bold",
            color="#333333"
        )

    # The source-specific S11 curve
    ax.plot(
        source_data["frequency_ghz"],
        source_data["s11_db"],
        color=panel_colors[source],
        linewidth=2.5
    )

    # Requirement line
    ax.axhline(
        y=-15,
        color="#4D4D4D",
        linestyle="--",
        linewidth=1.5
    )

    ax.set_title(source, fontsize=14, fontweight="bold")
    ax.set_xlabel("Frequency (GHz)", fontsize=12)
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)
    ax.grid(True, color="#D9D9D9", linewidth=0.8)

axes[0].set_ylabel("S11 (dB)", fontsize=12)

fig.suptitle(
    "S11 Small Multiples: Simulation and Anechoic-Chamber Measurement",
    fontsize=16,
    fontweight="bold",
    y=1.03
)

fig.tight_layout()

st.pyplot(fig)

st.markdown(
    """
    **Encoding justification.** This chart uses spatial separation into two
    aligned panels rather than overlaying the simulation and measurement curves.
    Frequency and \(S_{11}\) remain encoded by position, so values can still be
    compared accurately. The shared axis limits are essential: they ensure that
    visual differences reflect the data rather than different scales.

    **Gestalt/preattentive principle.** This design uses **common region** and
    **proximity**. Each response is enclosed in its own panel, making the source
    grouping immediately clear and reducing visual interference from overlapping
    curves.

    **Trade-off.** Separate panels reduce overlap and simplify inspection of each
    response, but direct point-by-point comparison requires looking between panels.
    """
)

# ------------------------------------------------------------
# SUMMARY / INTERPRETATION
# ------------------------------------------------------------
st.header("Comparison and conclusion")

st.markdown(
    """
    **Recommended chart for the paper or presentation: Chart 1.** It combines
    the most perceptually accurate channel for the numerical variables—position on
    common axes—with distinct color for source identity and shaded regions for
    target-band extent. It enables a reader to assess the \(-15\) dB requirement,
    locate resonances, and compare simulation with measurement in one view.

    **Accessibility note.** The app does not rely on color alone. Chart 2 offers a
    solid-versus-dashed alternative for grayscale printing or color-vision
    accessibility, while Chart 3 separates the two sources into labeled panels.
    All charts have explicit axis labels, units in GHz and dB, descriptive titles,
    a visible \(-15\) dB threshold, and interactive hover tooltips.
    """
)


# ------------------------------------------------------------
# OPTIONAL: NUMERICAL SUMMARY IN EACH BAND
# ------------------------------------------------------------
st.header("Band-by-band numerical summary")

summary_rows = []

for _, band in bands.iterrows():
    for source in ["Simulation", "Anechoic-chamber measurement"]:
        subset = s11_df[
            (s11_df["source"] == source)
            & (s11_df["frequency_ghz"] >= band["start_ghz"])
            & (s11_df["frequency_ghz"] <= band["end_ghz"])
        ]

        if not subset.empty:
            minimum_row = subset.loc[subset["s11_db"].idxmin()]

            summary_rows.append({
                "Band": band["band"],
                "Range (GHz)": band["frequency_range"],
                "Source": source,
                "Minimum S11 (dB)": round(minimum_row["s11_db"], 2),
                "Frequency at minimum (GHz)": round(
                    minimum_row["frequency_ghz"], 4
                ),
                "Minimum meets −15 dB?": (
                    "Yes" if minimum_row["s11_db"] <= -15 else "No"
                )
            })

summary_df = pd.DataFrame(summary_rows)

st.dataframe(
    summary_df,
    use_container_width=True,
    hide_index=True
)

st.caption(
    "The table identifies the deepest S11 minimum in each specified band. "
    "For full-band compliance, inspect the curves in the charts, because a band "
    "can contain a minimum below −15 dB while other frequencies within the same "
    "interval remain above the requirement."
)