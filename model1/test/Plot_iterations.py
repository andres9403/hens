import matplotlib.pyplot as plt
import csv

# Read results_53.csv (Pyomo 5.3)
iterations_53 = []
tac_53 = []
with open('results_53.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        iterations_53.append(int(row['iteration']))
        tac_53.append(float(row[' tac'] if ' tac' in row else row['tac']))

# Read results.csv (Pyomo last version)
iterations_last = []
tac_last = []
with open('results.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        iterations_last.append(int(row['iteration']))
        tac_last.append(float(row[' tac'] if ' tac' in row else row['tac']))

plt.figure(figsize=(10, 6))
plt.plot(iterations_53, tac_53, marker='o', label='Pyomo 5.3 (results_53.csv) - TAC')
plt.plot(iterations_last, tac_last, marker='s', label='Pyomo latest (results.csv) - TAC')
plt.xlabel('Iteration')
plt.ylabel('TAC')
plt.title('TAC per Iteration: Pyomo 5.3 vs Pyomo Latest')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# Plot total_time vs iteration
# Read total_time from both files

total_time_53 = []
with open('results_53.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        total_time_53.append(float(row[' total_time'] if ' total_time' in row else row['total_time']))

total_time_last = []
with open('results.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        total_time_last.append(float(row[' total_time'] if ' total_time' in row else row['total_time']))

plt.figure(figsize=(10, 6))
plt.plot(iterations_53, total_time_53, marker='o', label='Pyomo 5.3 (results_53.csv) - Total Time')
plt.plot(iterations_last, total_time_last, marker='s', label='Pyomo latest (results.csv) - Total Time')
plt.xlabel('Iteration')
plt.ylabel('Total Time (s)')
plt.title('Total Time per Iteration: Pyomo 5.3 vs Pyomo Latest')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

