import os

from definitions import ROOT_DIR
import json
import xmltodict


def generate_absolute_path(source):
    path = os.path.join(ROOT_DIR, source)
    return path


def write_lines(source, data):
    with open(source, "w") as file:
        for i in range(0, len(data)):
            if i == len(data) - 1:
                file.write(f"{data[i]}")
            else:
                file.write(f"{data[i]}\n")


def write_as_is(source, data):
    with open(source, "w") as file:
        file.write(data)


def xml_to_json(file, exit_name):
    with open(file) as xml_file:
        data_dict = xmltodict.parse(xml_file.read())

        json_data = json.dumps(data_dict, indent=4)
        with open(
            generate_absolute_path(f"resources/{exit_name}.json"), "w"
        ) as json_file:
            json_file.write(json_data)


def read(source):
    with open(source, "rb") as file:
        data = file.read()
    return data
