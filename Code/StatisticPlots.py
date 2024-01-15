import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
import json

# READ ME: If you want these to run download pandas and matplotlib. Also you have to change the test.json to steam.json.


def plot1():
    # https://towardsdatascience.com/linear-regression-using-gradient-descent-97a6c8700931

    def LinearRegression(data):
        # Read csv data
        X = data.iloc[:, 0]
        Y = data.iloc[:, 1]

        # Building the model
        a = 0
        b = 0

        L = 0.0001  # The learning Rate
        iterations = 1000  # More iterations means more accurate

        n = len(X)  # Number of elements in X

        # Gradient Descent
        for i in range(iterations):
            Y_pred = a * X + b  # The current predicted value of Y
            D_a = (-2 / n) * sum(X * (Y - Y_pred))  # (-2 / n) * ∑(X * (Y - YPred))
            D_b = (-2 / n) * sum(Y - Y_pred)  # (-2 / n) * ∑(Y - YPred)
            a -= L * D_a  # Update a
            b -= L * D_b  # Update b

        # Making predictions
        Y_pred = a * X + b
        return Y_pred, X, Y

    import json
    cols = ['price', 'average_playtime']
    data = []

    with open("steam.json") as f:
        doc = json.load(f)
        for line in doc:
            lst = [line['price'], line['average_playtime'] / 60]
            data.append(lst)

    df = pd.DataFrame(data=data, columns=cols)

    Y_pred, X, Y = LinearRegression(df)

    plt.scatter(X, Y)
    plt.plot([min(X), max(X)], [min(Y_pred), max(Y_pred)], color='red')  # regression line
    plt.xlabel("Price")
    plt.ylabel("Average playtime")
    plt.xlim(-1, 100)
    plt.ylim(-5, 500)
    plt.show()


def plot2():
    cols = ['price', 'count']
    data = []

    with open("steam.json") as f:
        doc = json.load(f)
        for line in doc:
            data.append(line['price'])

    counted = Counter(data)
    s = pd.Series(counted, name="count")
    s.index.name = "price"
    s = s.reset_index()

    X = s.iloc[:, 0]
    Y = s.iloc[:, 1]

    plt.bar(X, Y)
    plt.xlim(0, 30)
    plt.title("How many games have the same price?")
    plt.xlabel("Price")
    plt.ylabel("Count")
    plt.show()


plot1()
plot2()
