import json
import customtkinter as ctk
from collections import Counter
import statistics as st
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


# plt.style.use("grayscale")  # Change style of plots


def LinearRegression(data):  # https://towardsdatascience.com/linear-regression-using-gradient-descent-97a6c8700931
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
    Y_pred = a*X + b
    return Y_pred, X, Y


class Plots:
    def __init__(self, data):
        self.data = data

        lst = sorted(data, key=lambda x: x["positive_ratings"], reverse=True)

        names = []
        keys = []
        for i in lst[:5]:
            names.append(i["name"])
            keys.append(i["positive_ratings"])

        window = ctk.CTk()
        window.grid_columnconfigure([0, 1], weight=1)
        window.grid_columnconfigure([0, 1], weight=1)

        Plots.figure1(window, names, keys)
        Plots.figure2(window, names, keys)
        # Plots.figure3(window, names, keys)
        Plots.figure4(self, window)
        Plots.figure5(self, window)

        window.mainloop()

    @staticmethod
    def figure1(window, x, y):
        fig, ax = plt.subplots()
        fig.autofmt_xdate()

        canvas = FigureCanvasTkAgg(fig, master=window)
        canvas.get_tk_widget().grid(row=0, column=0)

        ax.scatter(x, y)
        ax.plot(x, y)
        canvas.draw()

    @staticmethod
    def figure2(window, x, y):
        fig, ax = plt.subplots()
        fig.autofmt_xdate()

        canvas = FigureCanvasTkAgg(fig, master=window)
        canvas.get_tk_widget().grid(row=0, column=1)

        ax.bar(x, y)
        canvas.draw()

    @staticmethod
    def figure3(window, names, data):
        colors = plt.get_cmap('Blues')(np.linspace(0.2, 0.7, len(data)))

        fig, ax = plt.subplots()
        fig.autofmt_xdate()

        canvas = FigureCanvasTkAgg(fig, master=window)
        canvas.get_tk_widget().grid(row=1, column=0)

        ax.pie(data, colors=colors, labels=names,
               wedgeprops={"linewidth": 3, "edgecolor": "white"})
        canvas.draw()

    def figure4(self, window):
        data = self.data
        newData = []
        cols = ['price', 'average_playtime']

        newData.append([line['price'] and line['average_playtime'] for line in data])

        df = pd.DataFrame(data=data, columns=cols)

        Y_pred, X, Y = LinearRegression(df)

        # Convert to hours
        Y /= 60
        Y_pred /= 60

        fig, ax = plt.subplots()
        canvas = FigureCanvasTkAgg(fig, master=window)
        canvas.get_tk_widget().grid(row=1, column=1)

        ax.scatter(X, Y)
        ax.plot([min(X), max(X)], [min(Y_pred), max(Y_pred)], color='red')
        plt.xlabel("Price")
        plt.ylabel("Average playtime")
        plt.xlim(-1, 100)
        plt.ylim(-5, 500)
        canvas.draw()

    def figure5(self, window):
        data = self.data
        newData = [line['price'] for line in data]
        counted = Counter(newData)

        s = pd.Series(counted, name="count")
        s.index.name = "price"
        s = s.reset_index()

        price = s.iloc[:, 0]
        count = s.iloc[:, 1]

        fig, ax = plt.subplots()
        canvas = FigureCanvasTkAgg(fig, master=window)
        canvas.get_tk_widget().grid(row=1, column=0)

        ax.bar(price, count)
        plt.xlim(0, 30)
        plt.title("How many games have the same price?")
        plt.xlabel("Price")
        plt.ylabel("Count")
        canvas.draw()


def avg_price(loaded_json):
    avg = st.mean(list(i["price"] for i in loaded_json))
    return round(avg, 2)


def avg_playtime(loaded_json):
    avg = st.mean(list(i["average_playtime"] for i in loaded_json))
    return round(avg)


def min_to_hours(minutes):
    return round(minutes / 60)


def avg_positive(loaded_json):
    avg = st.mean(list(i["positive_ratings"] for i in loaded_json))
    return round(avg)


def most_expensive_game(loaded_json):
    game = max(loaded_json, key=lambda a: a["price"])
    return game["price"], game["name"]


def amountOfGames(loaded_json):
    return len(loaded_json)


def main(loaded_json):
    avg = avg_playtime(loaded_json)
    biggest, name = most_expensive_game(loaded_json)
    print(f"\x1b[32mAverage price: {avg_price(loaded_json)}")
    print(f"Average playtime: {avg} minutes")
    print(f"Average playtime: {min_to_hours(avg)} hours")
    print(f"Average positive reviews: {avg_positive(loaded_json)}")
    print(f"Most expensive game belongs to: \x1b[31m{name}\x1b[32m with a price of ${biggest}")
    print(f"There are {amountOfGames(loaded_json)} games on steam")


if __name__ == '__main__':
    with open("steam.json") as file_read:
        rjson = file_read.read()
        loaded_json = json.loads(rjson)

    main(loaded_json)
    Plots(loaded_json)



