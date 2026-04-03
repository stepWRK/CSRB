# Copyright (C) 2026 stepWRK
#
# This file is part of SRBcalculate.
#
# SRBcalculate is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

import os

class DataManager:
    @staticmethod
    def saveToFile(params, filename="config.txt"):
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write("# Propellant\n")
                f.write(f"T0 = {params['T0']}\n")
                f.write(f"R = {params['R']}\n")
                f.write(f"k = {params['k']}\n")
                f.write(f"a = {params['a']}\n")
                f.write(f"n = {params['n']}\n")
                f.write(f"rho = {params['rho']}\n")
                f.write("\n# Геометрия (метры)\n")
                f.write(f"L = {params['L']}\n")
                f.write(f"Dcore = {params['Dcore']}\n")
                f.write(f"Dout = {params['Dout']}\n")
                f.write(f"Dthroat = {params['Dthroat']}\n")
            return True, "Успешно сохранено!"
        except Exception as e:
            return False, str(e)

    @staticmethod
    def loadFromFile(filename="config.txt"):# загрузка файла
        params = {}
        if not os.path.exists(filename):
            return False, "Файл где-то завалялся на линии кармена", params
        try:
            with open(filename, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue

                    name, value = line.split("=", 1)
                    name = name.strip()
                    value = value.split("#")[0].strip()

                    try:
                        if 'e' in value or 'E' in value:
                            params[name] = float(value)
                        elif '.' in value:
                            params[name] = float(value)
                        else:
                            params[name] = int(value)
                    except:
                        params[name] = value
            return True, "О, файл найден, на высоте!", params
        except Exception as e:
            return False, str(e), params

    @staticmethod
    def getDefaultParams():# парам по умолчанию
        return {
            'T0': 1720,
            'R': 197.9,
            'k': 1.133,
            'a': 5.83e-6,
            'n': 0.319,
            'rho': 1890,
            'L': 0.3,
            'Dcore': 0.015,
            'Dout': 0.05,
            'Dthroat': 0.012
        }