import os
from collections import OrderedDict
from market_analysis import ai_analysis
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from momentum_analysis_gemini import gemini_momentum_analysis
from adjusted_price_data import get_adjusted_price_of_all_companies, indices_data

print("SCRIPT STARTED")

def prepare_pivot(df, column_name="Ticker"):
    df = df.copy()
    df[["Open", "High", "Low", "Close", "Volume"]] = (
        df[["Open", "High", "Low", "Close", "Volume"]]
        .apply(pd.to_numeric, errors="coerce")
        .astype(float)
    )
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    return df.pivot_table(index="Date", columns=column_name, values="Close", aggfunc="first")


def plot_momentum_charts(price_df, output_dir, title_prefix, top_n=None):
    periods = OrderedDict([
        ("1-W", 5),
        ("2-W", 10),
        ("3-W", 15),
        ("1-M", 21),
        ("2-M", 42),
        ("3-M", 63),
        ("6-M", 126),
        ("1-Y", 252),
        ("2-Y", 504),
        ("3-Y", 756),
        ("5-Y", 1260),
    ])

    os.makedirs(output_dir, exist_ok=True)

    price_df = price_df.sort_index().dropna(how="all")

    for i, (label, n) in enumerate(periods.items(), start=1):
        window = price_df.tail(n).copy()
        if len(window) < 2:
            continue

        window = window.loc[:, window.iloc[0].notna()]
        window = window.ffill()

        min_obs = max(2, int(len(window) * 0.8))
        window = window.loc[:, window.notna().sum() >= min_obs]
        if window.empty:
            continue

        time_series = window.div(window.iloc[0]).sub(1)
        end_vals = time_series.iloc[-1].sort_values(ascending=False)

        if top_n is not None:
            end_vals = end_vals.head(top_n)

        time_series = time_series[end_vals.index]

        mode = "lines+markers" if n <= 63 else "lines"
        line_width = 1 if n <= 252 else 0.7

        fig = make_subplots(specs=[[{"secondary_y": False}]])

        for ticker in time_series.columns:
            fig.add_trace(go.Scatter(
                x=time_series.index,
                y=time_series[ticker],
                mode=mode,
                name=ticker,
                line=dict(width=line_width),
                marker=dict(size=3) if n <= 63 else None
            ))

            fig.add_annotation(
                x=1.01,
                xref="paper",
                y=time_series[ticker].iloc[-1],
                yref="y",
                text=f"{time_series[ticker].iloc[-1]:.1%} {ticker}",
                showarrow=False,
                font=dict(size=10),
                xanchor="left",
                yanchor="middle",
                align="left"
            )

        fig.update_layout(
            title=f"{title_prefix} Momentum Over the Last {label}",
            xaxis_title="Date",
            yaxis_title="Cumulative Return",
            autosize=False,
            showlegend=False,
            template="plotly_dark",
            margin=dict(l=80, r=160, t=100, b=80),
            xaxis=dict(
                tickformat="%b %d",
                tickangle=45,
                nticks=10,
                showgrid=True,
                showline=True
            ),
            yaxis=dict(
                tickformat=".0%",
                showgrid=True,
                showline=True
            )
        )
        print("Files in folder:", os.listdir("sectorwise_momentum"))
        print("Files in folder:", os.listdir("stockwise_momentum"))
        filename = f"{i:02d}_{label.replace('-', '_')}.png"
        fig.write_image(os.path.join(output_dir, filename), scale=2)
        print("Saved:", filepath, "Exists?", os.path.exists(filepath))


adjusted_data = get_adjusted_price_of_all_companies()
adjusted_pivot_df = prepare_pivot(adjusted_data, column_name="Ticker")


indices_df = indices_data()
indices_pivot_df = prepare_pivot(indices_df, column_name="Ticker")

print("Adjusted data shape:", adjusted_data.shape)
print("Indices data shape:", indices_df.shape)

plot_momentum_charts(
    price_df=indices_pivot_df,
    output_dir="sectorwise_momentum",
    title_prefix="Sectorwise",
    top_n=None
)

plot_momentum_charts(
    price_df=adjusted_pivot_df,
    output_dir="stockwise_momentum",
    title_prefix="Stockwise",
    top_n=20
)


from post_to_facebook import post_multiple_images_single_post


post_multiple_images_single_post("sectorwise_momentum", ai_analysis(indices_df))
post_multiple_images_single_post("stockwise_momentum", gemini_momentum_analysis(adjusted_data))
print('sector wise accumulation charts posted to facebook successfully!')