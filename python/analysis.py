# ============================================================
# COOKIE CATS A/B TEST ANALYSIS
# Gate 30 vs Gate 40
# ============================================================

import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt
import statsmodels.formula.api as smf


# ============================================================
# 1. LOAD CLEAN DATA
# ============================================================

df = pd.read_excel("Clean_Data_Final.xlsx")

print("=" * 70)
print("1. DATA VALIDATION")
print("=" * 70)

print("\nDataset Shape:")
print(df.shape)

print("\nFirst 5 Rows:")
print(df.head())

print("\nData Types:")
print(df.dtypes)

print("\nMissing Values:")
print(df.isna().sum())

print("\nDuplicate Rows:")
print(df.duplicated().sum())

print("\nDuplicate User IDs:")
print(df["userid"].duplicated().sum())

print("\nExperiment Groups:")
print(df["version"].value_counts())


# ============================================================
# 2. RETENTION COUNTS
# ============================================================

print("\n" + "=" * 70)
print("2. RETENTION COUNTS")
print("=" * 70)

retention_counts = (
    df.groupby("version")[["retention_1", "retention_7"]]
      .sum()
)

print(retention_counts)


# ============================================================
# 3. RETENTION RATES
# ============================================================

print("\n" + "=" * 70)
print("3. RETENTION RATES")
print("=" * 70)

retention_rates = (
    df.groupby("version")[["retention_1", "retention_7"]]
      .mean()
)

print(retention_rates)

day1_gate30 = retention_rates.loc["gate_30", "retention_1"]
day1_gate40 = retention_rates.loc["gate_40", "retention_1"]

day7_gate30 = retention_rates.loc["gate_30", "retention_7"]
day7_gate40 = retention_rates.loc["gate_40", "retention_7"]

day1_difference = day1_gate30 - day1_gate40
day7_difference = day7_gate30 - day7_gate40

print("\nDay-1 Retention Difference:")
print(f"{day1_difference:.4%}")

print("\nDay-7 Retention Difference:")
print(f"{day7_difference:.4%}")


# ============================================================
# 4. OVERALL DAY-7 A/B TEST
# ============================================================

print("\n" + "=" * 70)
print("4. TWO-PROPORTION TEST — DAY-7 RETENTION")
print("=" * 70)

# Sample sizes
overall_n30 = (df["version"] == "gate_30").sum()
overall_n40 = (df["version"] == "gate_40").sum()

# Retained players
overall_x30 = df.loc[
    df["version"] == "gate_30",
    "retention_7"
].sum()

overall_x40 = df.loc[
    df["version"] == "gate_40",
    "retention_7"
].sum()

# Retention proportions
overall_p30 = overall_x30 / overall_n30
overall_p40 = overall_x40 / overall_n40

# Pooled proportion for hypothesis test
pooled_p = (
    overall_x30 + overall_x40
) / (
    overall_n30 + overall_n40
)

# Standard error
overall_se_test = math.sqrt(
    pooled_p * (1 - pooled_p) *
    (1 / overall_n30 + 1 / overall_n40)
)

# Difference
overall_difference = overall_p30 - overall_p40

# Z statistic
z_statistic = overall_difference / overall_se_test

# Two-sided p-value
overall_p_value = math.erfc(
    abs(z_statistic) / math.sqrt(2)
)

print("\nGate 30:")
print("Players:", overall_n30)
print("Day-7 retained:", overall_x30)
print("Day-7 retention:", overall_p30)

print("\nGate 40:")
print("Players:", overall_n40)
print("Day-7 retained:", overall_x40)
print("Day-7 retention:", overall_p40)

print("\nPooled proportion:", pooled_p)
print("Standard Error:", overall_se_test)
print("Observed Difference:", overall_difference)
print("Z-statistic:", z_statistic)
print("P-value:", overall_p_value)


# ============================================================
# 5. 95% CONFIDENCE INTERVAL
# ============================================================

print("\n" + "=" * 70)
print("5. 95% CONFIDENCE INTERVAL")
print("=" * 70)

ci_standard_error = math.sqrt(
    (
        overall_p30 * (1 - overall_p30)
        / overall_n30
    )
    +
    (
        overall_p40 * (1 - overall_p40)
        / overall_n40
    )
)

margin_of_error = 1.96 * ci_standard_error

overall_ci_lower = (
    overall_difference - margin_of_error
)

overall_ci_upper = (
    overall_difference + margin_of_error
)

print("Standard Error:", ci_standard_error)
print("Margin of Error:", margin_of_error)

print(
    f"95% CI: "
    f"{overall_ci_lower:.4%} "
    f"to "
    f"{overall_ci_upper:.4%}"
)


# ============================================================
# 6. PRACTICAL BUSINESS IMPACT
# ============================================================

print("\n" + "=" * 70)
print("6. PRACTICAL BUSINESS IMPACT")
print("=" * 70)

retained_player_difference = overall_x30 - overall_x40

relative_lift = (
    overall_difference / overall_p40
)

print(
    "Additional retained players observed:",
    retained_player_difference
)

print(
    "Absolute Day-7 retention lift:",
    f"{overall_difference:.4%}"
)

print(
    "Relative lift vs Gate 40:",
    f"{relative_lift:.2%}"
)

# Expected additional retained users if 100,000 players
additional_per_100k = overall_difference * 100000

print(
    "Additional Day-7 retained players per 100,000:",
    round(additional_per_100k)
)


# ============================================================
# 7. BOOTSTRAP ANALYSIS
# ============================================================

print("\n" + "=" * 70)
print("7. BOOTSTRAP ANALYSIS")
print("=" * 70)

# Fixed seed makes the analysis reproducible
np.random.seed(42)

gate_30 = df[df["version"] == "gate_30"]
gate_40 = df[df["version"] == "gate_40"]

bootstrap_differences = []

for i in range(5000):

    sample_30 = gate_30["retention_7"].sample(
        n=len(gate_30),
        replace=True,
        random_state=None
    )

    sample_40 = gate_40["retention_7"].sample(
        n=len(gate_40),
        replace=True,
        random_state=None
    )

    difference = (
        sample_30.mean()
        - sample_40.mean()
    )

    bootstrap_differences.append(difference)

bootstrap_differences = np.array(
    bootstrap_differences
)

bootstrap_mean = bootstrap_differences.mean()
bootstrap_std = bootstrap_differences.std()

bootstrap_lower = np.percentile(
    bootstrap_differences,
    2.5
)

bootstrap_upper = np.percentile(
    bootstrap_differences,
    97.5
)

print("Number of simulations:", len(bootstrap_differences))

print(
    "Bootstrap mean difference:",
    bootstrap_mean
)

print(
    "Bootstrap standard deviation:",
    bootstrap_std
)

print(
    "Bootstrap 95% CI:",
    bootstrap_lower,
    "to",
    bootstrap_upper
)


# ============================================================
# 8. BOOTSTRAP VISUALIZATION
# ============================================================

plt.figure(figsize=(10, 6))

plt.hist(
    bootstrap_differences,
    bins=50
)

plt.axvline(
    overall_difference,
    linestyle="--",
    linewidth=2,
    label="Observed Difference"
)

plt.axvline(
    bootstrap_lower,
    linestyle=":",
    linewidth=2,
    label="2.5% CI"
)

plt.axvline(
    bootstrap_upper,
    linestyle=":",
    linewidth=2,
    label="97.5% CI"
)

plt.xlabel(
    "Difference in Day-7 Retention "
    "(Gate 30 - Gate 40)"
)

plt.ylabel("Frequency")

plt.title(
    "Bootstrap Distribution of "
    "Day-7 Retention Difference"
)

plt.legend()

plt.tight_layout()

plt.savefig(
    "bootstrap_day7_retention.png",
    dpi=300
)

plt.show()


# ============================================================
# 9. ENGAGEMENT SEGMENTATION
# ============================================================

print("\n" + "=" * 70)
print("9. ENGAGEMENT SEGMENTATION")
print("=" * 70)

q33 = df["sum_gamerounds"].quantile(1 / 3)
q67 = df["sum_gamerounds"].quantile(2 / 3)

print("33rd percentile:", q33)
print("67th percentile:", q67)

# Based on observed quantiles:
# Low    = <= 8
# Medium = 9–35
# High   = >35

df["engagement"] = pd.cut(
    df["sum_gamerounds"],
    bins=[
        -1,
        8,
        35,
        float("inf")
    ],
    labels=[
        "Low",
        "Medium",
        "High"
    ]
)

print("\nEngagement Segment Counts:")

segment_counts = (
    df["engagement"]
    .value_counts()
    .sort_index()
)

print(segment_counts)


# ============================================================
# 10. SEGMENT RETENTION
# ============================================================

print("\n" + "=" * 70)
print("10. DAY-7 RETENTION BY ENGAGEMENT")
print("=" * 70)

segment_retention = (
    df.groupby(
        ["engagement", "version"],
        observed=True
    )["retention_7"]
    .agg(
        count="count",
        retained="sum",
        retention_rate="mean"
    )
)

print(segment_retention)


# ============================================================
# 11. SEGMENT EFFECTS + CONFIDENCE INTERVALS
# ============================================================

print("\n" + "=" * 70)
print("11. SEGMENT-LEVEL EFFECTS")
print("=" * 70)

segment_results = []

for segment in ["Low", "Medium", "High"]:

    group_30 = df[
        (df["engagement"] == segment)
        &
        (df["version"] == "gate_30")
    ]

    group_40 = df[
        (df["engagement"] == segment)
        &
        (df["version"] == "gate_40")
    ]

    n30 = len(group_30)
    n40 = len(group_40)

    x30 = group_30["retention_7"].sum()
    x40 = group_40["retention_7"].sum()

    p30 = x30 / n30
    p40 = x40 / n40

    difference = p30 - p40

    se = math.sqrt(
        (
            p30 * (1 - p30)
            / n30
        )
        +
        (
            p40 * (1 - p40)
            / n40
        )
    )

    margin = 1.96 * se

    lower = difference - margin
    upper = difference + margin

    segment_results.append({
        "Engagement": segment,
        "Gate_30_n": n30,
        "Gate_40_n": n40,
        "Gate_30_Retention": p30,
        "Gate_40_Retention": p40,
        "Difference": difference,
        "CI_Lower": lower,
        "CI_Upper": upper
    })

    print(f"\n{segment}")
    print("Gate 30 n:", n30)
    print("Gate 40 n:", n40)
    print(
        "Gate 30 retention:",
        f"{p30:.4%}"
    )
    print(
        "Gate 40 retention:",
        f"{p40:.4%}"
    )
    print(
        "Difference:",
        f"{difference:.4%}"
    )
    print(
        "95% CI:",
        f"{lower:.4%} to {upper:.4%}"
    )

segment_results_df = pd.DataFrame(
    segment_results
)


# ============================================================
# 12. INTERACTION ANALYSIS
# ============================================================

print("\n" + "=" * 70)
print("12. INTERACTION ANALYSIS")
print("=" * 70)

print(
    "\nIMPORTANT:"
    "\nEngagement is based on sum_gamerounds measured during"
    "\nthe experiment. Therefore this is exploratory/post-treatment"
    "\nsegmentation and should NOT be interpreted as clean causal"
    "\nheterogeneous treatment effects."
)

# Convert Boolean to numeric
df["retention_7_numeric"] = (
    df["retention_7"]
    .astype(int)
)

model = smf.logit(
    "retention_7_numeric ~ "
    "C(version) * C(engagement)",
    data=df
).fit()

print(model.summary())


# ============================================================
# 13. EXTRACT INTERACTION RESULTS
# ============================================================

interaction_results = []

for term in [
    "C(version)[T.gate_40]:C(engagement)[T.Medium]",
    "C(version)[T.gate_40]:C(engagement)[T.High]"
]:

    if term in model.params.index:

        interaction_results.append({
            "Interaction": term,
            "Coefficient": model.params[term],
            "P_Value": model.pvalues[term],
            "CI_Lower": model.conf_int().loc[term, 0],
            "CI_Upper": model.conf_int().loc[term, 1]
        })

interaction_results_df = pd.DataFrame(
    interaction_results
)

print("\nInteraction Terms:")

print(interaction_results_df)


# ============================================================
# 14. OUTLIER SENSITIVITY ANALYSIS
# ============================================================

print("\n" + "=" * 70)
print("14. OUTLIER SENSITIVITY ANALYSIS")
print("=" * 70)

print(
    "\nThe cleaned analysis excludes userid 6390605,"
    "\nwhich had 49,854 gamerounds."
)

print(
    "\nWe now check whether including this observation"
    "\nchanges the Day-7 retention conclusion."
)

try:

    raw_df = pd.read_csv("cookie_cats.csv")

    raw_n30 = (
        raw_df["version"] == "gate_30"
    ).sum()

    raw_n40 = (
        raw_df["version"] == "gate_40"
    ).sum()

    raw_x30 = raw_df.loc[
        raw_df["version"] == "gate_30",
        "retention_7"
    ].sum()

    raw_x40 = raw_df.loc[
        raw_df["version"] == "gate_40",
        "retention_7"
    ].sum()

    raw_p30 = raw_x30 / raw_n30
    raw_p40 = raw_x40 / raw_n40

    raw_difference = raw_p30 - raw_p40

    raw_pooled = (
        raw_x30 + raw_x40
    ) / (
        raw_n30 + raw_n40
    )

    raw_se = math.sqrt(
        raw_pooled
        * (1 - raw_pooled)
        * (
            1 / raw_n30
            + 1 / raw_n40
        )
    )

    raw_z = raw_difference / raw_se

    raw_p_value = math.erfc(
        abs(raw_z) / math.sqrt(2)
    )

    print("\nINCLUDING OUTLIER:")
    print("Gate 30 retention:", f"{raw_p30:.4%}")
    print("Gate 40 retention:", f"{raw_p40:.4%}")
    print("Difference:", f"{raw_difference:.4%}")
    print("Z-statistic:", raw_z)
    print("P-value:", raw_p_value)

    print("\nEXCLUDING OUTLIER:")
    print(
        "Gate 30 retention:",
        f"{overall_p30:.4%}"
    )
    print(
        "Gate 40 retention:",
        f"{overall_p40:.4%}"
    )
    print(
        "Difference:",
        f"{overall_difference:.4%}"
    )
    print(
        "P-value:",
        overall_p_value
    )

    sensitivity_results = pd.DataFrame({
        "Scenario": [
            "Including outlier",
            "Excluding outlier"
        ],
        "Gate_30_Retention": [
            raw_p30,
            overall_p30
        ],
        "Gate_40_Retention": [
            raw_p40,
            overall_p40
        ],
        "Difference": [
            raw_difference,
            overall_difference
        ],
        "P_Value": [
            raw_p_value,
            overall_p_value
        ]
    })

except FileNotFoundError:

    print(
        "\nRaw cookie_cats.csv not found."
        "\nSensitivity analysis skipped."
    )

    sensitivity_results = pd.DataFrame()


# ============================================================
# 15. FINAL RESULTS TABLE
# ============================================================

print("\n" + "=" * 70)
print("15. FINAL RESULTS")
print("=" * 70)

final_results = pd.DataFrame({
    "Metric": [
        "Gate 30 Players",
        "Gate 40 Players",
        "Gate 30 Day-7 Retention",
        "Gate 40 Day-7 Retention",
        "Day-7 Retention Difference",
        "Z-statistic",
        "P-value",
        "95% CI Lower",
        "95% CI Upper",
        "Bootstrap Mean Difference",
        "Bootstrap 95% CI Lower",
        "Bootstrap 95% CI Upper",
        "Observed Retained Player Difference"
    ],

    "Value": [
        overall_n30,
        overall_n40,
        overall_p30,
        overall_p40,
        overall_difference,
        z_statistic,
        overall_p_value,
        overall_ci_lower,
        overall_ci_upper,
        bootstrap_mean,
        bootstrap_lower,
        bootstrap_upper,
        retained_player_difference
    ]
})

print(final_results)


# ============================================================
# 16. FINAL STATISTICAL INTERPRETATION
# ============================================================

print("\n" + "=" * 70)
print("16. STATISTICAL INTERPRETATION")
print("=" * 70)

alpha = 0.05

if overall_p_value < alpha:

    print(
        "\nResult:"
        "\nThere is statistically significant evidence"
        "\nof a difference in Day-7 retention between"
        "\nGate 30 and Gate 40."
    )

else:

    print(
        "\nResult:"
        "\nThere is not sufficient statistical evidence"
        "\nof a difference in Day-7 retention between"
        "\nGate 30 and Gate 40."
    )

print(
    "\nObserved difference:",
    f"{overall_difference:.2%}"
)

print(
    "\n95% confidence interval:",
    f"{overall_ci_lower:.2%}",
    "to",
    f"{overall_ci_upper:.2%}"
)

print(
    "\nBootstrap 95% confidence interval:",
    f"{bootstrap_lower:.2%}",
    "to",
    f"{bootstrap_upper:.2%}"
)


# ============================================================
# 17. BUSINESS INTERPRETATION
# ============================================================

print("\n" + "=" * 70)
print("17. BUSINESS INTERPRETATION")
print("=" * 70)

print(
    "\nThe Gate 30 group had higher observed Day-7 retention"
    "\nthan the Gate 40 group."
)

print(
    "\nThe absolute difference was",
    f"{overall_difference:.2%}",
    "or",
    f"{overall_difference * 100:.2f}",
    "percentage points."
)

print(
    "\nFor every 100,000 players exposed to the same"
    "\nretention rates, this difference corresponds to"
    f"approximately {round(additional_per_100k):,}"
    "\nadditional Day-7 retained players."
)

print(
    "\nHowever, the engagement segmentation should be"
    "\nconsidered exploratory because gamerounds was"
    "\nmeasured after players experienced the experiment."
)

print(
    "\nThe interaction model did not provide sufficient"
    "\nevidence that the Gate 30 vs Gate 40 treatment"
    "\neffect differed significantly by engagement segment."
)


# ============================================================
# 18. EXPORT RESULTS TO EXCEL
# ============================================================

print("\n" + "=" * 70)
print("18. EXPORTING RESULTS")
print("=" * 70)

with pd.ExcelWriter(
    "Final_Analysis_Results.xlsx",
    engine="openpyxl"
) as writer:

    final_results.to_excel(
        writer,
        sheet_name="Overall Results",
        index=False
    )

    retention_rates.to_excel(
        writer,
        sheet_name="Retention Rates"
    )

    segment_results_df.to_excel(
        writer,
        sheet_name="Segment Results",
        index=False
    )

    interaction_results_df.to_excel(
        writer,
        sheet_name="Interaction",
        index=False
    )

    if not sensitivity_results.empty:

        sensitivity_results.to_excel(
            writer,
            sheet_name="Sensitivity",
            index=False
        )

print(
    "\nResults exported to:"
    "\nFinal_Analysis_Results.xlsx"
)

print("\n" + "=" * 70)
print("ANALYSIS COMPLETE")
print("=" * 70)