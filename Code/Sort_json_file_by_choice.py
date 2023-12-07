import json


def bubble_sort(lst, key, descending=False):
    length_of_unsorted_list = len(lst) - 1
    while length_of_unsorted_list > 0:
        for i in range(length_of_unsorted_list):
            if lst[i][key] > lst[i + 1][key]:  # if the current element is larger than the next element, then swap them
                temp = lst[i + 1][key]
                lst[i + 1][key] = lst[i][key]
                lst[i][key] = temp
        length_of_unsorted_list -= 1

    if descending:
        return list(reversed(lst))

    return lst


def filter_list_all_keys():
    with open("test.json") as file_read:
        rjson = file_read.read()
        loaded_json = json.loads(rjson)

        # Get the keys
        keys = loaded_json[0].keys()
        key_string = ""
        for key in keys:
            key_string += f"{key}, "

        # Check if input is correct
        correct_input = False
        input_key = ""
        rev = True
        while not correct_input:
            key_input = input(
                f"\x1b[34mFilter by one of the following: {key_string}\nFilter by (key, desc (optional)): ")

            for key in keys:
                if key_input == key:
                    correct_input = True
                    input_key = key
                elif key_input == key + ", desc":
                    correct_input = True
                    input_key = key
                    rev = False

        print(f"\x1b[31m{loaded_json}")
        sorted_list = sorted(loaded_json, key=lambda x: x[input_key], reverse=rev)  # lambda function gets the values of dict
        print(f"\x1b[32m{sorted_list}")


def filter_list():
    with open("test.json") as file_read:
        rjson = file_read.read()
        loaded_json = json.loads(rjson)

        # Get the keys
        keys = ["name", "release_date", "required_age", "achievements", "positive_ratings", "negative_ratings", "average_playtime", "owners", "price"]
        key_string = ""
        for key in keys:
            key_string += f"{key}, "

        # Check if input is correct
        correct_input = False
        input_key = ""
        rev = True
        while not correct_input:
            key_input = input(f"\x1b[34mFilter by one of the following: {key_string}\nFilter by (key, asc (optional)): ")

            for key in keys:
                if key_input == key:
                    correct_input = True
                    input_key = key
                elif key_input == key + ", asc":
                    correct_input = True
                    input_key = key
                    rev = False

        print(f"\x1b[31m{loaded_json}")
        sorted_list = bubble_sort(loaded_json, input_key, rev)
        print(f"\x1b[32m{sorted_list}")


# filter_list_all_keys()
filter_list()
