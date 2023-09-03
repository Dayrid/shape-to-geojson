import json
import math
import os
import re
from typing import List

import geopandas as gpd


def proc_x(x: float) -> float:
    return x / (math.pi / 180.0) / 6378137.0


def proc_y(y: float) -> float:
    return (2 * math.atan(math.exp(y / 6378137)) - math.pi / 2) / (
            math.pi / 180)


def divide_coordinates(coordinates):
    if isinstance(coordinates[0], list):
        # Рекурсивно обрабатываем вложенные массивы координат
        return [divide_coordinates(coord) for coord in coordinates]
    else:
        # Деление координат
        return [proc_x(coordinates[0]), proc_y(coordinates[1])]


def shp_to_geojson(from_path: str, to_path: str) -> None:
    try:
        data = gpd.read_file(from_path)

        js_string = data.to_json()
        js_obj = json.loads(js_string)

        for feature in js_obj['features']:
            coordinates = feature['geometry']['coordinates']
            feature['geometry']['coordinates'] = divide_coordinates(coordinates)

        with open(to_path, "w", encoding="utf-8") as f:
            json.dump(js_obj, f, ensure_ascii=False, indent=4)

    except IOError:
        pass


def folder_to_geojson(from_path: str, to_path: str, filter):
    files = [os.path.join(from_path, x) for x in os.listdir(from_path) if
             not os.path.isdir(x) and x.endswith(".shp") and filter(x)]
    if not os.path.exists(to_path):
        os.mkdir(to_path)
    for file in files:
        print(file)
        shp_to_geojson(file, os.path.join(to_path, os.path.basename(file).replace(".shp", ".geojson")))



def group_files_by_corpus(file_names):
    corpus_files = {}
    pattern = r"\d+"

    for file_name in file_names:
        match = re.search(pattern, file_name)
        if match:
            corpus_number = int(match.group(0))
            if corpus_number in corpus_files:
                corpus_files[corpus_number].append(file_name)
            else:
                corpus_files[corpus_number] = [file_name]

    return corpus_files

# folder_to_geojson("files", "geojsons", lambda x: "преобраз" in x)

folder_path = "geojsons"
file_names = [os.path.join(folder_path, x) for x in os.listdir(folder_path)]

corpus_files = group_files_by_corpus(file_names)
for corpus in corpus_files.keys():
    path = "geojsons/" + str(corpus)
    os.mkdir(path)
    for file in corpus_files[corpus]:
        os.rename(file, os.path.join(path, os.path.basename(file)))
