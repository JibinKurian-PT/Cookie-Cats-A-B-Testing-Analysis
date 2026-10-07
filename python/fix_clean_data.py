import pandas as pd

# Load the current cleaned workbook
df = pd.read_excel("Cleaned_Data.xlsx")

print("Before cleaning:", df.shape)

# Remove the identified extreme observation
df = df[df["userid"] != 6390605].copy()

# Save the definitive cleaned dataset
df.to_excel("Clean_Data_Final.xlsx", index=False)

print("After cleaning:", df.shape)
print("Maximum gamerounds:", df["sum_gamerounds"].max())
print("Outlier records remaining:", (df["userid"] == 6390605).sum())
print("\nExperiment groups:")
print(df["version"].value_counts())
