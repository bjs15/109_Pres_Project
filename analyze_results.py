import csv
import math

# Load training data
X = []  # Training features
y = []  # Training outcomes

# Read training data
print("Loading training data from simulation_results.csv...")
reader = csv.reader(open('simulation_results.csv'))
header = next(reader)
for row in reader:
    # Add bias term and convert features
    for_x = [float(1)]  # Bias term
    for i in range(len(row) - 1):  # All columns except last
        for_x.append(float(row[i] == 'True'))
    X.append(for_x)
    y.append(int(row[-1]))  # Last column is player1_won

def sigmoid(z):
    return 1/(1+math.exp(-z))

# Set up parameters
L = len(X[0])  # Number of features including bias
steps = 1000   # Increased steps for more data
eta = 0.00001  # Decreased learning rate for stability with larger dataset

# Initialize weights
w = [0.0] * L

print("\nTraining model using gradient ascent...")
print(f"Training on {len(X)} examples...")

# Do gradient ascent steps times
for _ in range(steps):
    grad = [0.0 for _ in range(L)]
    for xi, yi in zip(X, y):
        z = sum(w[i]*xi[i] for i in range(L))
        p_i = sigmoid(z)
        err = yi - p_i
        for i in range(L):
            grad[i] += err * xi[i]

    # Update weights
    for i in range(L):
        w[i] += eta * grad[i]

print("Weights: ", w)

# Calculate training accuracy
correct = 0
total = len(X)
for xi, yi in zip(X, y):
    z = sum(w[i]*xi[i] for i in range(L))
    prediction = sigmoid(z)
    if (prediction > .5 and yi == 1) or (prediction < .5 and yi == 0):
        correct += 1

print(f"\nTraining accuracy: {correct/total:.3f}")

# Analyze effects of each mechanic
feature_names = ['Bias', 'Choose', 'Swap', 'Winner Starts']
print("\nEffect of each mechanic:")
for i in range(L):
    if i == 0:
        print(f"Bias term: {w[i]:.3f} (base win probability: {sigmoid(w[i]):.3f})")
    else:
        effect = "increases" if w[i] > 0 else "decreases"
        odds_ratio = math.exp(abs(w[i]))
        percent = (odds_ratio - 1) * 100
        print(f"{feature_names[i]}: {effect} winning chance by {percent:.1f}%")

# Calculate win probabilities for all combinations
print("\nPredicted win probabilities for all combinations:")
print("Choose  Swap    Winner_Starts  Win_Prob")
print("-" * 40)

for choose in [0, 1]:
    for swap in [0, 1]:
        for winner in [0, 1]:
            features = [1, choose, swap, winner]
            z = sum(w[i]*features[i] for i in range(L))
            pred_prob = sigmoid(z)
            print(f"{bool(choose):<7} {bool(swap):<7} {bool(winner):<13} {pred_prob:>8.3f}")

# Calculate actual win rates from training data
print("\nActual win rates in training data:")
for i in range(1, L):  # Skip bias term
    wins_enabled = 0
    total_enabled = 0
    wins_disabled = 0
    total_disabled = 0
    
    for xi, yi in zip(X, y):
        if xi[i] == 1:
            total_enabled += 1
            wins_enabled += yi
        else:
            total_disabled += 1
            wins_disabled += yi
            
    win_rate_enabled = wins_enabled/total_enabled if total_enabled > 0 else 0
    win_rate_disabled = wins_disabled/total_disabled if total_disabled > 0 else 0
    
    print(f"\n{feature_names[i]}:")
    print(f"  Enabled:  {win_rate_enabled:.3f} ({wins_enabled}/{total_enabled})")
    print(f"  Disabled: {win_rate_disabled:.3f} ({wins_disabled}/{total_disabled})")