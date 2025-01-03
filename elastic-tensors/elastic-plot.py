import plotly.graph_objects as go
import pandas as pd

# Load data from elastic-results.json
df1 = pd.read_json("elastic-results.json")

# Load data from elastic-gnn-results.json
df2 = pd.read_json("elastic-gnn-results.json")

# Expand derived_properties column into separate columns
df1_expanded = pd.json_normalize(df1["derived_properties"])
df2_expanded = pd.json_normalize(df2["derived_properties"])

# Add the "ordering" column to the expanded dataframes
df1_expanded["ordering"] = df1["ordering"]
df2_expanded["ordering"] = df2["ordering"]

# Remove rows with blank string as ordering
df1_expanded = df1_expanded[df1_expanded["ordering"] != ""]
df2_expanded = df2_expanded[df2_expanded["ordering"] != ""]


# Merge the two dataframes based on the column "ordering"
merged_df = pd.merge(df1_expanded, df2_expanded, on="ordering")

# Clean up unphysical values
merged_df = merged_df[abs(merged_df["k_voigt_x"]) <= 1000]
merged_df = merged_df[abs(merged_df["k_voigt_y"]) <= 1000]
merged_df = merged_df[abs(merged_df["g_voigt_x"]) <= 1000]
merged_df = merged_df[abs(merged_df["g_voigt_y"]) <= 1000]


# Get the column names excluding "ordering"
columns = merged_df.columns.tolist()

# Generate scatter plots for each column
for column in columns:
    if column.endswith("_x"):
        column_y = column.replace("_x", "_y")
        if column_y in columns:
            fig = go.Figure(
                data=go.Scatter(
                    x=merged_df[column], y=merged_df[column_y], mode="markers"
                )
            )

            # add a parity line from min to max
            try:
                min_val = min(min(merged_df[column]), min(merged_df[column_y]))
                max_val = max(max(merged_df[column]), max(merged_df[column_y]))
                fig.add_trace(
                    go.Scatter(
                        x=[min_val, max_val],
                        y=[min_val, max_val],
                        mode="lines",
                        line=dict(color="black", width=1),
                    )
                )
            except:
                pass

            fig.update_layout(
                title=f"{column_y} vs {column}",
                xaxis_title=column,
                yaxis_title=column_y,
                width=600,
                height=600,
                template="simple_white",
                showlegend=False,
            )
            fig.update_xaxes(mirror=True)
            fig.update_yaxes(mirror=True)

            fig.write_image(f"{column.replace('_x', '')}.png", scale=3)
            # fig.show()
