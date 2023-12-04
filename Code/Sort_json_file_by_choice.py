import json

# NOTE!!!! Werkt nu niet omdat ik niet het json goede bestand in open() heb gedaan! Het is beter om dit the testen met een kleiner json bestand


def filter_list():
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
        while not correct_input:
            key_input = input(f"\x1b[34mFilter by one of the following: {key_string}\nFilter by: ")

            for key in keys:
                if key_input == key:
                    correct_input = True
                    input_key = key

        print(f"\x1b[31m{loaded_json}")
        sorted_list = sorted(loaded_json, key=lambda x: x[input_key], reverse=True)  # lambda function gets the values of dict
        print(f"\x1b[32m{sorted_list}")


filter_list()
