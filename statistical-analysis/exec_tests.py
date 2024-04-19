import pandas as pd

results = [{} for _ in range(14)]

tasks = [
    ["$A=B$", "$A=B$", "$A=B$"],
    ["$A=B$", "$A=B$", "$A<B$"],
    ["$A=B$", "$A<B$", "$A=B$"],
    ["$A=B$", "$A<B$", "$A>B$"],
    ["$A=B$", "$A<B$", "$A<B$"],
    ["$A<B$", "$A=B$", "$A=B$"],
    ["$A<B$", "$A=B$", "$A>B$"],
    ["$A<B$", "$A=B$", "$A<B$"],
    ["$A<B$", "$A>B$", "$A=B$"],
    ["$A<B$", "$A>B$", "$A>B$"],
    ["$A<B$", "$A>B$", "$A<B$"],
    ["$A<B$", "$A<B$", "$A=B$"],
    ["$A<B$", "$A<B$", "$A>B$"],
    ["$A<B$", "$A<B$", "$A<B$"],
]

flip_a_b = ["baseline", "isochrone_timecontrol", "isochrone_confidencecontrol"]
methods = ["baseline", "isochrone_timecontrol", "isochrone_confidencecontrol"]

for task in methods:
    baseline = pd.read_csv(f"{task}.csv")
    # for columns indexed 2 through -1, the first character is either A or B (case insensitive)
    # tally up the number of As and Bs for each column
    # store the results in an array of dictionaries

    for i in range(2, len(baseline.columns)):
        column = baseline.iloc[:, i]
        A = 0
        B = 0
        for value in column:
            if value[0].upper() == "A":
                A += 1
            elif value[0].upper() == "B":
                B += 1
        results[i - 2][task] = {
            "A": A,
            "B": B
        }

# print(results)

from scipy.stats import fisher_exact, chi2_contingency

table = []
for i in range(14):
    for j in range(len(methods) - 1):
        for k in range(j + 1, len(methods)):
            A1 = results[i][methods[j]]["A"]
            B1 = results[i][methods[j]]["B"]
            A2 = results[i][methods[k]]["A"]
            B2 = results[i][methods[k]]["B"]
            # don't use chi2_contingency since there can be 0 values
            # instead, use fisher's exact test
            # chi2, p, dof, expected = chi2_contingency([[A1, B1], [A2, B2]])
            odds, p = fisher_exact([[A1, B1], [A2, B2]])
            table.append({
                "Task": tasks[i],
                "Method1": methods[j],
                "Method2": methods[k],
                "OddsRatio": odds,
                "PValue": p
            })

# print(table)
# print statistically significant results
# for i, row in enumerate(table):
#     if row["PValue"] < 0.05:
#         print(f"Task {row['Task']}, {row['Method1']} vs {row['Method2']} P-Value: {row['PValue']}")


# build a latex table with the columns being:
# Task, Method1, Method2, Method1_A, Method1_B, Method2_A, Method2_B, OddsRatio, PValue
# for each row in the table. the first 3 columns are >, =, <
# print the latex table
# also, split the Task column into 3 separate columns, 1 for each part of the task. use <, =, > as the column values

def get_index(task):
    return tasks.index(task)

def flip(letter, method):
    return ("A" if letter == "B" else "B") if method in flip_a_b else letter

table_df = pd.DataFrame([{
    **item,
    "Distance": item["Task"][0],
    "Mean": item["Task"][1],
    "Variance": item["Task"][2],
    "Method1": item["Method1"].replace("_", "-"),
    "Method2": item["Method2"].replace("_", "-"),
    "M1A": results[get_index(item["Task"])][item["Method1"]][flip("A", item["Method1"])],
    "M1B": results[get_index(item["Task"])][item["Method1"]][flip("B", item["Method1"])],
    "M2A": results[get_index(item["Task"])][item["Method2"]][flip("A", item["Method1"])],
    "M2B": results[get_index(item["Task"])][item["Method2"]][flip("B", item["Method1"])],
} for item in table])

# table_df.to_latex("table.tex", encoding='utf-8', escape=False, index=False, columns=["Distance", "Mean", "Variance", "Method1", "Method2", "OddsRatio", "PValue"], float_format="%.3f")

table_tex = table_df.to_latex(index=False, columns=["Distance", "Mean", "Variance", "Method1", "Method2", "M1A", "M1B", "M2A", "M2B", "OddsRatio", "PValue"], float_format="%.3f", escape=False)
# print(table_tex)

table_lines = table_tex.split("\n")
# for statistically significant lines, add \rowcolor{lightgray}
for i, row in enumerate(table):
    if row["PValue"] < 0.05:
        table_lines[i + 4] = "\\rowcolor{lightgray} " + table_lines[i + 4]

table_tex = "\n".join(table_lines)
print(table_tex)

