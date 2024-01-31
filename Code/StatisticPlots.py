import json
import customtkinter as ctk
from collections import Counter
import statistics as st
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


# plt.style.use("grayscale")  # Change style of plots

def binary_search(lst, arg, key):
    minIndex = 0
    maxIndex = len(lst)
    while maxIndex - minIndex > 1:
        scooby = (maxIndex - minIndex) / 2
        searchIndex = scooby + minIndex
        if arg > lst[int(searchIndex)][key]:
            minIndex += scooby  # take 2nd half
        elif arg < lst[int(searchIndex)][key]:
            maxIndex -= scooby  # take 1st half
        else:
            return True, int(searchIndex)
    return False, -1


def LinearRegression(data):  # https://towardsdatascience.com/linear-regression-using-gradient-descent-97a6c8700931
    # Read data
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


class MergeSort:
    @staticmethod
    def divide_list(lst):
        # Divide the list in two sub-lists
        length = len(lst) // 2
        left_list = lst[:length]
        right_list = lst[length:]

        return left_list, right_list

    @staticmethod
    def merge_sort(lst, key):  # https://reintech.io/blog/solving-problems-with-merge-sort-in-python
        if len(lst) <= 1:  # Base case
            return lst

        left_list, right_list = MergeSort.divide_list(lst)  # Divide list

        left_list = MergeSort.merge_sort(left_list, key)
        right_list = MergeSort.merge_sort(right_list, key)

        return MergeSort.merge(left_list, right_list, key)

    @staticmethod
    def merge(left, right, key):
        merged = []
        left_index = 0
        right_index = 0

        while left_index < len(left) and right_index < len(right):
            if left[left_index][key] <= right[right_index][key]:
                merged.append(left[left_index])
                left_index += 1
            else:
                merged.append(right[right_index])
                right_index += 1

        merged += left[left_index:]
        merged += right[right_index:]

        return merged


class SortByJson:
    @staticmethod
    def bubble_sort(lst, key, descending=False):  # NOT USED ANYMORE (switched to mergesort)
        length_of_unsorted_list = len(lst) - 1
        while length_of_unsorted_list > 0:
            for i in range(length_of_unsorted_list):
                if lst[i][key] > lst[i + 1][key]:  # if the current element is larger than the next element, then swap them
                    temp = lst[i + 1][key]
                    lst[i + 1][key] = lst[i][key]
                    lst[i][key] = temp
            length_of_unsorted_list -= 1

        if descending:
            return lst[::-1]
        return lst

    @staticmethod
    def filter_list(loaded_json, key_input=None):
        # Get the keys
        keys = ["appid", "name", "release_date", "required_age", "achievements", "positive_ratings", "negative_ratings", "average_playtime", "owners", "price"]
        key_string = ""
        for key in keys:
            key_string += f"{key}, "

        # Check if input is correct
        correct_input = False
        input_key = ""
        while not correct_input:
            if key_input is None:
                key_input = input(f"\x1b[34mFilter by one of the following: {key_string}\nFilter by key: ")

            for key in keys:
                if key_input == key:
                    correct_input = True
                    input_key = key

        sorted_list = MergeSort.merge_sort(loaded_json, input_key)
        return sorted_list


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
        Plots.figure4(data, window)
        Plots.figure5(data, window)

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

    @staticmethod
    def figure4(data, window):
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

    @staticmethod
    def figure5(data, window):
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


class SteamData:
    @staticmethod
    def avg_price(loaded_json):
        avg = st.mean(list(i["price"] for i in loaded_json))
        return round(avg, 2)

    @staticmethod
    def avg_playtime(loaded_json):
        avg = st.mean(list(i["average_playtime"] for i in loaded_json))
        return round(avg)

    @staticmethod
    def min_to_hours(minutes):
        return round(minutes / 60)

    @staticmethod
    def avg_positive(loaded_json):
        avg = st.mean(list(i["positive_ratings"] for i in loaded_json))
        return round(avg)

    @staticmethod
    def most_expensive_game(loaded_json):
        game = max(loaded_json, key=lambda a: a["price"])
        return game["price"], game["name"]

    @staticmethod
    def amountOfGames(loaded_json):
        return len(loaded_json)


def main(loaded_json):
    avg = SteamData.avg_playtime(loaded_json)
    biggest, name = SteamData.most_expensive_game(loaded_json)
    print(f"\x1b[32m+-Average price: {SteamData.avg_price(loaded_json)}")
    print(f"Average playtime: {avg} minutes")
    print(f"Average playtime: {SteamData.min_to_hours(avg)} hours")
    print(f"Average positive reviews: {SteamData.avg_positive(loaded_json)}")
    print(f"Most expensive game belongs to: {name} with a price of ${biggest}")
    print(f"There are {SteamData.amountOfGames(loaded_json)} games on steam")


if __name__ == '__main__':
    with open("steam.json") as file_read:
        rjson = file_read.read()
        loaded_json = json.loads(rjson)

    SortByJson.filter_list(loaded_json)
    main(loaded_json)
    Plots(loaded_json)



