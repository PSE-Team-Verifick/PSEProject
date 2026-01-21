from typing import Dict

from utils.result import Result, Failure, Success
from utils.singleton import SingletonMeta

from model.data.neural_network import NeuralNetwork
from model.data.input_bounds import InputBounds

import csv


class InputBoundsLoader(metaclass=SingletonMeta):
    def load_input_bounds(self, file_path: str, network: NeuralNetwork) -> Result[InputBounds]:
        ending = file_path.split('.')[-1]
        is_csv = (ending == 'csv')
        is_vnnlib = (ending == 'vnnlib')

        if not (is_csv or is_vnnlib):
            return Failure(ValueError(ending + ' is not supported. Please use a .csv or a .vnnlib file.'))

        input_count = self.__get_input_count(network)

        if is_csv:
            try:
                return self.__parse_csv(file_path, input_count)
            except BaseException as e:
                return Failure(e)

    def __get_input_count(self, network: NeuralNetwork) -> int:
        return 0

    def __parse_csv(self, file_path: str, input_count: int) -> Result[InputBounds]:
        rows = []
        try:
            with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)

                try:
                    header = next(reader)
                except StopIteration:
                    return Failure(ValueError(f"{file_path} is empty."))
                for row in reader:
                    rows.append([cell.strip() for cell in row])
        except OSError as e:
            return Failure(e)

        field_count = len(header)

        # checking whether the field count is valid and matches the format of the rows
        if field_count not in (2, 3):
            return Failure(ValueError(file_path + 'needs to be consistently organized in two or three columns.'))

        if any([len(row) != field_count for row in rows]):
            return Failure(ValueError(file_path + "must have {field_count} columns in every row."))

        if len(rows) != input_count:
            return Failure(ValueError(
                f"{file_path} has {str(len(rows))} rows. It needs the same number of inputs as the network ({input_count})"))

        indices = []
        # allow custom ordering of bounds
        if field_count == 3:
            for row in rows:
                indices.append(int(row[0]))
                del row[0]

            # check that all indices are covered exactly once
            if not sorted(indices) == list(range(len(rows))):
                return Failure(ValueError("Every index in the csv file has to appear exactly once."))
        else:
            indices = list(range(len(rows)))

        bounds = {
            i: (float(rows[i][0]), float(rows[i][1])) for i in indices
        }
        input_bounds = InputBounds(bounds)

        return Success(input_bounds)
