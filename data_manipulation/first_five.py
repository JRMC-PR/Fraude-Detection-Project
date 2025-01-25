#!/usr/bin/env python3
import csv

with open("../Data/generated_logs.csv", "r") as f:
    reader = csv.reader(f)


    header = next(reader)
    print("Column names in the fake data\n:")

    for i in range(len(header)):
        print(f"{header[i]}")


    print("\nFirst five rows of the fake data\n:")
    for l , row in enumerate(reader):
        print(f"Row{i}")
        print("---------------------------------------------------------------------------------------")
        print(row)
        print("---------------------------------------------------------------------------------------")
        if l == 5:
            break
