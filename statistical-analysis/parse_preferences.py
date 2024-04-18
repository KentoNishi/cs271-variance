import pandas as pd

# read in baseline.csv
baseline = pd.read_csv("baseline.csv")
# for columns indexed 2 through -1, the first character is either A or B (case insensitive)
# tally up the number of As and Bs for each column
# store the results in an array of dictionaries

results = []
for i in range(2, len(baseline.columns)):
    column = baseline.iloc[:, i]
    A = 0
    B = 0
    for value in column:
        if value[0].upper() == "A":
            A += 1
        elif value[0].upper() == "B":
            B += 1
    results.append({
        "A": A,
        "B": B
    })

print(results)
