# Copyright (C) 2026 stepWRK
#
# This file is part of SRBcalculate.
#
# SRBcalculate is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

import customtkinter as ctk
from core import RocketMath
from data import DataManager

class MainWindow:
    def __init__(self):
        self.window = ctk.CTk()
        self.window.title("SRBcalc")
        self.window.geometry("1920x1080")
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_rowconfigure(1, weight=1)
        self.topFrame = ctk.CTkFrame(self.window)# верхняя панель с кнопками переключения
        self.topFrame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        self.btnMain = ctk.CTkButton(# кнопки для переключения вкладок
            self.topFrame,
            text="Основной расчёт",
            command=lambda: self.showTab("main"),
            width=150,
            height=40,
            fg_color="#2e7d32",
            hover_color="#1e5a20",      #цветь
            text_color="white"
        )
        self.btnMain.pack(side="left", padx=5, pady=5)

        self.btnHelp = ctk.CTkButton(
            self.topFrame,
            text="Справка",
            command=lambda: self.showTab("help"),
            width=150,
            height=40,
            fg_color="#1976d2",
            hover_color="#0d47a1",      #цветь
            text_color="white"
        )
        self.btnHelp.pack(side="left", padx=5, pady=5)

        self.btnMaterials = ctk.CTkButton(
            self.topFrame,
            text="Материалы",
            command=lambda: self.showTab("materials"),
            width=150,
            height=40,
            fg_color="#ed6c02",
            hover_color="#b74d00",      #цветь
            text_color="white"
        )
        self.btnMaterials.pack(side="left", padx=5, pady=5)

        self.btnGraphs = ctk.CTkButton(
            self.topFrame,
            text="Графики",
            command=lambda: self.showTab("graphs"),
            width=150,
            height=40,
            fg_color="#9c27b0",
            hover_color="#6a1b9a",      #цветь
            text_color="white"
        )
        self.btnGraphs.pack(side="left", padx=5, pady=5)
        self.btnGraphs.pack(side="left", padx=5, pady=5)
        self.tabContainer = ctk.CTkFrame(self.window)
        self.tabContainer.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        self.tabContainer.grid_columnconfigure(0, weight=1)
        self.tabContainer.grid_rowconfigure(0, weight=1)
        self.createMainTab()# создаём все вкладки
        self.createHelpTab()
        self.createMaterialsTab()
        self.createGraphsTab()
        self.showTab("main")
        self.loadInitialData()

    def createMainTab(self):
        self.mainTab = ctk.CTkFrame(self.tabContainer)
        self.mainTab.grid_columnconfigure(0, weight=1)
        self.mainTab.grid_columnconfigure(1, weight=1)
        self.mainTab.grid_rowconfigure(0, weight=1)

        leftFrame = ctk.CTkFrame(self.mainTab)# левая панель (ввод)
        leftFrame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.entries = {}# Словарь для полей ввода

        ctk.CTkLabel(# === ТОПЛИВО ===
            leftFrame,
            text="параметры топлива",
            font=("Arial", 16, "bold")
        ).pack(pady=5)

        fuelParams = [ # Базовые параметры топлива
            ("Температура T0 (K):", "T0", "1720", "Температура горения"),
            ("Газовая постоянная R (Дж/кг·K):", "R", "197.9", "Газовая постоянная"),
            ("Показатель адиабаты k:", "k", "1.133", "Показатель адиабаты"),
            ("Коэф. скорости горения a:", "a", "5.83e-6", "Коэф. скорости горения"),
            ("Показатель степени n:", "n", "0.319", "Степень в законе горения"),
            ("Плотность ρ (кг/м³):", "rho", "1890", "Плотность топлива")
        ]

        for label, key, default, hint in fuelParams:
            frame = ctk.CTkFrame(leftFrame)
            frame.pack(fill="x", padx=10, pady=2)

            ctk.CTkLabel(frame, text=label, width=180, anchor="w").pack(side="left", padx=5)
            entry = ctk.CTkEntry(frame, width=120)
            entry.pack(side="left", padx=5)
            entry.insert(0, default)

            ctk.CTkLabel(frame, text="ⓘ", width=20, text_color="gray").pack(side="left")# Подсказка при наведении

            self.entries[key] = entry

        ctk.CTkLabel(# === ДОПОЛНИТЕЛЬНЫЕ ПАРАМЕТРЫ ТОПЛИВА ===
            leftFrame,
            text="ДОП. ПАРАМЕТРЫ ТОПЛИВА",
            font=("Arial", 14, "bold")
        ).pack(pady=5)

        extraFuel = [
            ("Содержание Al (%):", "AlContent", "0", "Процент алюминия"),
            ("Соотношение O/F:", "OF", "2.5", "Соотношение окислитель/горючее"),
            ("КПД камеры:", "etaComb", "0.95", "КПД камеры"),
            ("КПД сопла:", "etaNozzle", "0.97", "КПД сопла")
        ]

        for label, key, default, hint in extraFuel:
            frame = ctk.CTkFrame(leftFrame)
            frame.pack(fill="x", padx=10, pady=2)

            ctk.CTkLabel(frame, text=label, width=180, anchor="w").pack(side="left", padx=5)
            entry = ctk.CTkEntry(frame, width=120)
            entry.pack(side="left", padx=5)
            entry.insert(0, default)
            self.entries[key] = entry

        ctk.CTkLabel(# === ГЕОМЕТРИЯ ===
            leftFrame,
            text="ГЕОМЕТРИЯ ШАШКИ (метры)",
            font=("Arial", 16, "bold")
        ).pack(pady=5)

        geomParams = [
            ("Длина шашки L:", "L", "0.3", "Длина шашки"),
            ("Диаметр канала Dcore:", "Dcore", "0.015", "Диаметр канала"),
            ("Наруж. диаметр Dout:", "Dout", "0.05", "Наружный диаметр"),
            ("Диаметр критики Dthroat:", "Dthroat", "0.012", "Диаметр критики"),
            ("Диаметр среза Dexit:", "Dexit", "0.03", "Диаметр среза сопла"),
            ("Кол-во каналов:", "Ncores", "1", "Количество каналов")
        ]

        for label, key, default, hint in geomParams:
            frame = ctk.CTkFrame(leftFrame)
            frame.pack(fill="x", padx=10, pady=2)

            ctk.CTkLabel(frame, text=label, width=180, anchor="w").pack(side="left", padx=5)
            entry = ctk.CTkEntry(frame, width=120)
            entry.pack(side="left", padx=5)
            entry.insert(0, default)
            self.entries[key] = entry

        ctk.CTkLabel(# === МАТЕРИАЛЫ КОРПУСА ===
            leftFrame,
            text="МАТЕРИАЛ КОРПУСА",
            font=("Arial", 14, "bold")
        ).pack(pady=5)

        caseParams = [
            ("Материал корпуса:", "caseMat", "Aluminum", "Материал корпуса"),
            ("Толщина стенки (мм):", "wallThick", "2.0", "Толщина стенки"),
            ("Запас прочности:", "safetyFactor", "2.5", "Запас прочности")
        ]

        for label, key, default, hint in caseParams:
            frame = ctk.CTkFrame(leftFrame)
            frame.pack(fill="x", padx=10, pady=2)

            ctk.CTkLabel(frame, text=label, width=180, anchor="w").pack(side="left", padx=5)
            entry = ctk.CTkEntry(frame, width=120)
            entry.pack(side="left", padx=5)
            entry.insert(0, default)
            self.entries[key] = entry

        btnFrame = ctk.CTkFrame(leftFrame)# Кнопки
        btnFrame.pack(fill="x", padx=10, pady=10)

        ctk.CTkButton(
            btnFrame,
            text="Сохранить",
            command=self.saveToFile,
            height=35,
            width=120
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            btnFrame,
            text="Загрузить",
            command=self.loadFromFile,
            height=35,
            width=120
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            btnFrame,
            text="Сброс",
            command=self.resetToDefaults,
            height=35,
            width=120
        ).pack(side="left", padx=5)

        rightFrame = ctk.CTkFrame(self.mainTab)# правая панель (результаты)
        rightFrame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        ctk.CTkLabel(
            rightFrame,
            text="РЕЗУЛЬТАТЫ РАСЧЁТА",
            font=("Arial", 18, "bold")
        ).pack(pady=10)

        self.resultText = ctk.CTkTextbox(
            rightFrame,
            wrap="word",
            font=("Consolas", 12),
            height=400
        )
        self.resultText.pack(fill="both", expand=True, padx=10, pady=5)

        ctk.CTkButton(# кнопка расчёта
            rightFrame,
            text="РАССЧИТАТЬ",
            command=self.calculate,
            height=50,
            font=("Arial", 19, "bold"),
            fg_color="#2e7d32",
            hover_color="#1e5a20"
        ).pack(pady=10)

    def createHelpTab(self):
        self.helpTab = ctk.CTkFrame(self.tabContainer)

        helpText = ctk.CTkTextbox(self.helpTab, wrap="word", font=("Arial", 12))
        helpText.pack(fill="both", expand=True, padx=20, pady=20)

        helpContent = """
        Руководство по расчёту
        ===========================

        осн формулы:
        
        1) Характеристическая скорость C* = (1/Γ) * √(R * T0)
           Γ = √(k) * (2/(k+1))^((k+1)/(2(k-1)))

        2) Давление в камере Pc = [a * ρ * Ab * C* / A*] ^ (1/(1-n))

        3) Тяга F = Pc * A* * Cf

        4) Скорость горения r = a * Pc^n


        ОПИСАНИЕ ПАРАМЕТРОВ:
        --------------------
        T0  - Температура горения (K)
        R   - Удельная газовая постоянная (Дж/кг·K)
        k   - Показатель адиабаты (Cp/Cv)
        a   - Коэффициент скорости горения
        n   - Показатель степени в законе горения (0 < n < 1)
        ρ   - Плотность топлива (кг/м³)

        L      - Длина шашки (м)
        Dcore  - Начальный диаметр канала (м)
        Dout   - Наружный диаметр шашки (м)
        Dthroat- Диаметр критического сечения (м)
        Dexit  - Диаметр среза сопла (м)

        безопсность:
        ------------------
        - Всегда используйте запас прочности > 2 для стенок корпуса
        - Не превышайте предел текучести материала
        - Проверяйте коэффициент Kn (обычно 200-400 для KNSB)
        - Макс. давление должно быть < давления разрушения корпуса

        основные топлива:
        -------------------------
        KNSB  (KNO3 + Сорбит)    : T0≈1720K, n≈0.32
        KNSU  (KNO3 + Сахар)      : T0≈1700K, n≈0.33
        KNDX  (KNO3 + Декстроза)  : T0≈1680K, n≈0.326
        APCP  (Перхлорат аммония) : T0≈2500K, n≈0.3-0.5

        типичн. значения Kn:
        ---------------------
        KNSB:  Kn=200-250 → Pc≈3-5 МПа
        KNSU:  Kn=250-300 → Pc≈4-6 МПа
        APCP:  Kn=300-400 → Pc≈5-8 МПа
        """

        helpText.insert("0.0", helpContent)
        helpText.configure(state="disabled")

    def createMaterialsTab(self):
        self.materialsTab = ctk.CTkFrame(self.tabContainer)

        materials = [# таблица материалов
            ["Материал", "Плотность кг/м³", "Текучесть МПа", "Прочность МПа", "Макс. T K"],
            ["Алюминий 6061-T6", "2700", "275", "310", "500"],
            ["Алюминий 7075-T6", "2810", "505", "570", "480"],
            ["Сталь 4130", "7850", "435", "670", "800"],
            ["Нерж. сталь 304", "8000", "215", "505", "900"],
            ["Титан Ti-6Al-4V", "4430", "880", "950", "700"],
            ["Углепластик", "1600", "400", "600", "450"],
            ["Стеклопластик", "1850", "150", "250", "400"],
            ["ПВХ", "1400", "45", "55", "350"],
            ["Поликарбонат", "1200", "65", "70", "400"]
        ]

        textWidget = ctk.CTkTextbox(self.materialsTab, wrap="none", font=("Consolas", 12))
        textWidget.pack(fill="both", expand=True, padx=20, pady=20)

        output = "Б.Д материялов\n"# формируем таблицу
        output += "=" * 80 + "\n"

        for row in materials:
            output += f"{row[0]:<20} {row[1]:>12} {row[2]:>12} {row[3]:>12} {row[4]:>12}\n"

        output += "\n" + "=" * 80 + "\n"
        output += "Используйте эти значения для расчёта прочности корпуса\n"
        output += "Всегда применяйте запас прочности 2-3x\n"

        textWidget.insert("0.0", output)
        textWidget.configure(state="disabled")

    def createGraphsTab(self):
        self.graphsTab = ctk.CTkFrame(self.tabContainer)

        ctk.CTkLabel(
            self.graphsTab,
            text="Здесь будут отображаться графики",
            font=("Arial", 16)
        ).pack(pady=50)

        ctk.CTkLabel(
            self.graphsTab,
            text="(Скоро появятся: зависимость давления от времени, кривые тяги, скорость горения)",
            font=("Arial", 9)
        ).pack()

    def showTab(self, tabName): #ёкарный бабай, вкладки!
        self.mainTab.grid_remove()
        self.helpTab.grid_remove()
        self.materialsTab.grid_remove()
        self.graphsTab.grid_remove()

        if tabName == "main":
            self.mainTab.grid(row=0, column=0, sticky="nsew")
        elif tabName == "help":
            self.helpTab.grid(row=0, column=0, sticky="nsew")
        elif tabName == "materials":
            self.materialsTab.grid(row=0, column=0, sticky="nsew")
        elif tabName == "graphs":
            self.graphsTab.grid(row=0, column=0, sticky="nsew")

    def getParams(self): #отдай значения, мои
        params = {}
        for key, entry in self.entries.items():
            try:
                val = entry.get().strip()
                if 'e' in val or 'E' in val:
                    params[key] = float(val)
                elif '.' in val:
                    params[key] = float(val)
                else:
                    params[key] = int(val)
            except:
                params[key] = 0
                print(f"Ошибка чтения {key}: {val}")
        return params

    def setParams(self, params): #знач в полях ввода
        for key, value in params.items():
            if key in self.entries:
                self.entries[key].delete(0, "end")
                self.entries[key].insert(0, str(value))

    def loadInitialData(self): #загрузка нач данных
        success, msg, params = DataManager.loadFromFile()
        if success:
            self.setParams(params)
            print("Загружено:", msg)
        else:
            params = DataManager.getDefaultParams()
            self.setParams(params)
            print("Значения по умолчанию")

    def saveToFile(self):
        params = self.getParams()
        success, msg = DataManager.saveToFile(params)
        self.showResult(msg)
        print("Сохранено:", msg)

    def loadFromFile(self):
        success, msg, params = DataManager.loadFromFile()
        if success:
            self.setParams(params)
            self.showResult(msg)
        else:
            self.showResult(f"Ошибка: {msg}")
        print("Загружено:", msg)

    def resetToDefaults(self):
        params = DataManager.getDefaultParams()
        self.setParams(params)
        self.showResult("сброс значений по умолчанию")

    def showResult(self, text):
        self.resultText.delete("0.0", "end")
        self.resultText.insert("0.0", text)

    def calculate(self):
        params = self.getParams()
        print("Расчёт с помощью:", params)

        result = RocketMath.fullCalculation(params)

        if result.get('success', False):
            output = f""" результаты полного расчёта
{'=' * 60}

термодинафиг:
C* = {result['Cstar']:.0f} м/с
C* (теоретич.) = {result['Cstar'] / 0.95:.0f} м/с (с учётом потерь)

геометрия:
Ab = {result['Ab'] * 10000:.2f} см²
A* = {result['Athroat'] * 1e6:.2f} мм²
Kn = {result['Kn']:.0f}
Степень расширения = {params.get('Dexit', 0) / params.get('Dthroat', 1):.2f}

пари камеры сгор:
Pc = {result['PcMPa']:.2f} МПа
Pc = {result['Pc'] / 101325:.2f} атм
Скорость горения = {result['r'] * 1000:.2f} мм/с
Скорость горения = {result['r'] * 1000 / 25.4:.2f} дюйм/с

характеристики:
Тяга (ур. моря) = {result['F']:.0f} Н
Тяга = {result['F'] / 4.448:.0f} фунт-сил
Уд. импульс (оц.) = {result['Cstar'] * 1.5 / 9.81:.0f} с

пареверке в безоопаснасте:
Макс. давление = {result['PcMPa']:.2f} МПа
Напряжение стенки (2мм Al) = {result['PcMPa'] * params.get('Dout', 0.05) / (2 * 0.002):.0f} МПа
Запас прочности = {275 / (result['PcMPa'] * params.get('Dout', 0.05) / (2 * 0.002)):.1f}x

входные данные:
T0={params['T0']}K, n={params['n']:.3f}
L={params['L'] * 1000:.0f}мм, Dcore={params['Dcore'] * 1000:.1f}мм
Al={params.get('AlContent', 0)}%, O/F={params.get('OF', 2.5)}
"""
        else:
            output = f"ОШИБКА: {result['ошибка']}"

        self.showResult(output)
        print("Расчёт завершён")

    def run(self):
        self.window.mainloop()