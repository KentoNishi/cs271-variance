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

methods = ["baseline", "iso_time", "iso_conf"]

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

flip_a_b = [
    ["baseline", 0],
    ["iso_time", 0],
    ["iso_conf", 0],
    ["baseline", 1],
    ["iso_time", 1],
    ["iso_conf", 1],
    ["baseline", 2],
    ["iso_time", 2],
    ["iso_conf", 2],
    ["baseline", 4],
    ["iso_time", 4],
    ["iso_conf", 4],
    ["baseline", 5],
    ["iso_time", 5],
    ["iso_conf", 5],
    ["baseline", 8],
    ["iso_time", 8],
    ["iso_conf", 8],
    ["baseline", 9],
    ["iso_time", 9],
    ["iso_conf", 9],
    ["baseline", 11],
    ["iso_time", 11],
    ["iso_conf", 11],
    ["baseline", 13],
    ["iso_time", 13],
    ["iso_conf", 13],
]

def some(arr, func):
    for item in arr:
        if func(item):
            return True
    return False

def flip(letter, task, method):
    return ("A" if letter == "B" else "B") if some(flip_a_b, lambda x: x[0] == method and x[1] == tasks.index(task)) else letter

def num_letters_different(str1, str2):
    return sum([1 for i in range(len(str1)) if str1[i] != str2[i]])

table = []
for i_1 in range(14):
    num = 0
    # for j in range(0, len(methods)):
    #     A1 = results[i_1][methods[0]][flip("A", methods[j])]
    #     B1 = results[i_1][methods[0]][flip("B", methods[j])]
    #     A2 = results[i_1][methods[j]][flip("A", methods[j])]
    #     B2 = results[i_1][methods[j]][flip("B", methods[j])]
    #     try:
    #         # try chi squared test
    #         _, p, _, _ = chi2_contingency([[A1, B1], [A2, B2]])
    #     except ValueError:
    #         odds, p = fisher_exact([[A1, B1], [A2, B2]])
    #     table.append({
    #         "Task": tasks[i_1],
    #         "Method1": methods[j],
    #         "Method2": methods[j],
    #         # "OddsRatio": odds,
    #         "PValue": p
    #     })
    #     num += 1
    for j_1 in range(0, len(methods)):
        for j_2 in range(j_1 + 1, len(methods)):
            A1 = results[i_1][methods[j_1]][flip("A", tasks[i_1], methods[j_1])]
            B1 = results[i_1][methods[j_1]][flip("B", tasks[i_1], methods[j_1])]
            A2 = results[i_1][methods[j_2]][flip("A", tasks[i_1], methods[j_2])]
            B2 = results[i_1][methods[j_2]][flip("B", tasks[i_1], methods[j_2])]
            odds, p = fisher_exact([[A1, B1], [A2, B2]])
            table.append({
                "Task": tasks[i_1],
                "Method1": methods[j_1],
                "Method2": methods[j_2],
                # "OddsRatio": odds,
                "PValue": p
            })
            num += 1
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

table_df = pd.DataFrame([{
    **item,
    "Dist": item["Task"][0],
    "Mean": item["Task"][1],
    "Var": item["Task"][2],
    "Method1": item["Method1"].replace("_", "-"),
    "Method2": item["Method2"].replace("_", "-"),
    "M1A": results[get_index(item["Task"])][item["Method1"]][flip("A", item["Task"], item["Method1"])],
    "M1B": results[get_index(item["Task"])][item["Method1"]][flip("B", item["Task"], item["Method1"])],
    "M2A": results[get_index(item["Task"])][item["Method2"]][flip("A", item["Task"], item["Method1"])],
    "M2B": results[get_index(item["Task"])][item["Method2"]][flip("B", item["Task"], item["Method1"])],
} for item in table])

# table_df.to_latex("table.tex", encoding='utf-8', escape=False, index=False, columns=["Distance", "Mean", "Variance", "Method1", "Method2", "OddsRatio", "PValue"], float_format="%.3f")

# "Dist2", "Mean2", "Var2", 
table_tex = table_df.to_latex(index=False, columns=["Dist", "Mean", "Var", "Method1", "M1A", "M1B", "Method2", "M2A", "M2B", "PValue"], float_format="%.3f", escape=False)
# print(table_tex)

# \begin{tabular}{lllllrr}
# \toprule
# Distance &  Mean & Variance &               Method1 &                     Method2 &  OddsRatio &  PValue \\
# \midrule
#    $A=B$ & $A=B$ &    $A=B$ &              baseline &       isochrone-timecontrol &      1.121 &   1.000 \\
#    $A=B$ & $A=B$ &    $A=B$ &              baseline & isochrone-confidencecontrol &      1.000 &   1.000 \\
#    $A=B$ & $A=B$ &    $A=B$ & isochrone-timecontrol & isochrone-confidencecontrol &      0.892 &   1.000 \\
#    $A=B$ & $A=B$ &    $A<B$ &              baseline &       isochrone-timecontrol &      0.600 &   0.450 \\
#    $A=B$ & $A=B$ &    $A<B$ &              baseline & isochrone-confidencecontrol &      0.600 &   0.450 \\
#    $A=B$ & $A=B$ &    $A<B$ & isochrone-timecontrol & isochrone-confidencecontrol &      1.000 &   1.000 \\
#    $A=B$ & $A<B$ &    $A=B$ &              baseline &       isochrone-timecontrol &      6.526 &   0.003 \\
# ...

# every block of 3 lines has the same Distance, Mean, and Variance
# add a \midrule after every block of 3 lines
# also only keep the middle line for the leftmost 3 columns
table_lines = table_tex.split("\n")
# for i in range(4, len(table_lines) - num + 1, num):
#     # table_lines[i - 1] = table_lines[i - 1] + "\\vspace{0.1cm}"
#     # add \cellcolor{gray!20} to the 4th, 5th, and 6th columns of the ith line
#     # table_lines[i] = "&".join(table_lines[i].split("&")[:3]) + "&" + "&".join(["\\cellcolor{gray!20}" + x for x in table_lines[i].split("&")[3:6]]) + "&" + "&".join(table_lines[i].split("&")[6:])
#     # do the same for the next line
#     # table_lines[i + 1] = "&".join(table_lines[i + 1].split("&")[:3]) + "&" + "&".join(["\\cellcolor{gray!20}" + x for x in table_lines[i + 1].split("&")[3:6]]) + "&" + "&".join(table_lines[i + 1].split("&")[6:])
#     # color the 1st, 2nd, 3rd, 4th, 5th, and 6th columns of the next line
#     # table_lines[i + 2] = "&".join(["\\cellcolor{gray!20}" + x for x in table_lines[i].split("&")[0:6]]) + "&" + "&".join(table_lines[i].split("&")[6:])
#     # table_lines[i + 1] = table_lines[i + 1] + "\\hline"
#     table_lines[i + num - 6] = "% " + table_lines[i + num - 6]
#     table_lines[i + num - 5] = "% " + table_lines[i + num - 5]
#     table_lines[i + num - 4] = "% " + table_lines[i + num - 4] + "\\hdashline"
#     table_lines[i + num - 1] = table_lines[i + num - 1] + "\\hline"
#     # table_lines[i] = "   & & &" + "&".join(table_lines[i].split("&")[3:])
#     # table_lines[i + 2] = "   & & &" + "&".join(table_lines[i + 2].split("&")[3:])

# for statistically significant lines, add \rowcolor{gray!20}
for i in range(len(table_lines)):
    try:
        p = float(table_lines[i].split("&")[-1].split("\\")[0].strip())
        if p < 0.05:
            split_by_and = table_lines[i].split("&")
            table_lines[i] = "&".join(split_by_and[:-1] + [" \\textbf{" + split_by_and[-1] + "}"])
    except ValueError:
        pass

table_tex = "\n".join(table_lines)
table_tex = table_tex.replace("tabular", "longtable")
# table_tex = table_tex.replace("lllllllrrlrrr", "ccc|ccc||lcc|lcc||c")
table_tex = table_tex.replace("llllrrlrrr", "ccc||ccc|ccc||c")
table_tex = table_tex.replace("inf", "$\infty$")
table_tex = table_tex.replace("NaN", "$\infty$")
table_tex = table_tex.replace("M1A", "A")
table_tex = table_tex.replace("M1B", "B")
table_tex = table_tex.replace("M2A", "A")
table_tex = table_tex.replace("M2B", "B")
table_tex = table_tex.replace("Method1", "Method 1")
table_tex = table_tex.replace("Method2", "Method 2")
table_tex = table_tex.replace("Dist", "Distance")
table_tex = table_tex.replace("Mean", "Mean")
table_tex = table_tex.replace("Var", "Variance")
table_tex = table_tex.replace("} ", "}")
with open("table.tex", "w") as f:
    f.write(table_tex)
