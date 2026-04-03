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
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

class MainWindow:
    def __init__(self):
        self.window = ctk.CTk()
        self.window.title("SRBcalc")
        self.window.geometry("1200x680")
        self.window.minsize(1024, 600)


        self.window.GridСolumnconfigure(0, weight=1) # осн сетка
        self.window.GridRowconfigure(0, weight=0)
        self.window.GridRowconfigure(1, weight=1)

        self.create_top_bar() # верхняя панель с кнопками

        self.tabContainer = ctk.CTkFrame(self.window) # контейнер для вкладок
        self.tabContainer.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        self.tabContainer.GridСolumnconfigure(0, weight=1)
        self.tabContainer.GridRowconfigure(0, weight=1)

        self.tabs = {}
        self.TabLoaded = {"main": False, "help": False, "materials": False, "graphs": False}

        self.CreateMainTab()
        self.ShowTab("main")

        self.loadInitialData()

        self.window.update_idletasks()

    def create_top_bar(self):
        self.topFrame = ctk.CTkFrame(self.window, height=50)
        self.topFrame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.topFrame.grid_propagate(False)

        buttons = [
            ("Основной расчёт", "main", "#2e7d32", "#1e5a20"),
            ("Справка", "help", "#1976d2", "#0d47a1"),
            ("Материалы", "materials", "#ed6c02", "#b74d00"),
            ("Графики", "graphs", "#9c27b0", "#6a1b9a"),
        ]

        for text, TabName, color, hover in buttons:
            btn = ctk.CTkButton(
                self.topFrame,
                text=text,
                command=lambda t=TabName: self.ShowTab(t),
                width=140,
                height=35,
                fg_color=color,
                hover_color=hover,
                text_color="white"
            )
            btn.pack(side="left", padx=5, pady=5)

    def CreateMainTab(self):
        if self.TabLoaded["main"]:
            return

        self.mainTab = ctk.CTkFrame(self.tabContainer)
        self.mainTab.GridСolumnconfigure(0, weight=1)
        self.mainTab.GridСolumnconfigure(1, weight=1)
        self.mainTab.GridRowconfigure(0, weight=1)

        leftFrame = ctk.CTkFrame(self.mainTab)
        leftFrame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.entries = {}

        ParamSections = [
            ("ПАРАМЕТРЫ ТОПЛИВА", 16, [
                ("Температура T0 (K):", "T0", "1720"),
                ("Газовая постоянная R (Дж/кг·K):", "R", "197.9"),
                ("Показатель адиабаты k:", "k", "1.133"),
                ("Коэф. скорости горения a:", "a", "5.83e-6"),
                ("Показатель степени n:", "n", "0.319"),
                ("Плотность ρ (кг/м³):", "rho", "1890"),
            ]),
            ("ДОП. ПАРАМЕТРЫ", 14, [
                ("Содержание Al (%):", "AlContent", "0"),
                ("Соотношение O/F:", "OF", "2.5"),
                ("КПД камеры:", "etaComb", "0.95"),
                ("КПД сопла:", "etaNozzle", "0.97"),
            ]),
            ("ГЕОМЕТРИЯ (метры)", 16, [
                ("Длина шашки L:", "L", "0.3"),
                ("Диаметр канала Dcore:", "Dcore", "0.015"),
                ("Наруж. диаметр Dout:", "Dout", "0.05"),
                ("Диаметр критики Dthroat:", "Dthroat", "0.012"),
                ("Диаметр среза Dexit:", "Dexit", "0.03"),
                ("Кол-во каналов:", "Ncores", "1"),
            ]),
            ("МАТЕРИАЛ КОРПУСА", 14, [
                ("Материал:", "caseMat", "Aluminum"),
                ("Толщина стенки (мм):", "wallThick", "2.0"),
                ("Запас прочности:", "safetyFactor", "2.5"),
            ]),
        ]

        for SectionTitle, FontSize, params in ParamSections:
            ctk.CTkLabel(
                leftFrame,
                text=SectionTitle,
                font=("Arial", FontSize, "bold")
            ).pack(pady=(10, 5), anchor="w", padx=10)

            for label, key, default in params:
                row = ctk.CTkFrame(leftFrame)
                row.pack(fill="x", padx=10, pady=2)

                ctk.CTkLabel(row, text=label, width=210, anchor="w").pack(side="left", padx=5)
                entry = ctk.CTkEntry(row, width=120)
                entry.pack(side="left", padx=5)
                entry.insert(0, default)
                self.entries[key] = entry

        BtnFrame = ctk.CTkFrame(leftFrame)
        BtnFrame.pack(fill="x", padx=10, pady=15)

        for text, cmd in [("Сохранить", self.saveToFile), ("Загрузить", self.loadFromFile),
                          ("Сброс", self.resetToDefaults)]:
            ctk.CTkButton(BtnFrame, text=text, command=cmd, width=100, height=32).pack(side="left", padx=5)

        rightFrame = ctk.CTkFrame(self.mainTab)
        rightFrame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        ctk.CTkLabel(
            rightFrame,
            text="РЕЗУЛЬТАТЫ РАСЧЁТА",
            font=("Arial", 18, "bold")
        ).pack(pady=10)

        self.resultText = ctk.CTkTextbox(rightFrame, wrap="word", font=("Consolas", 11))
        self.resultText.pack(fill="both", expand=True, padx=10, pady=5)

        ctk.CTkButton(
            rightFrame,
            text="РАССЧИТАТЬ",
            command=self.calculate,
            height=45,
            font=("Arial", 16, "bold"),
            fg_color="#2e7d32",
            hover_color="#1e5a20"
        ).pack(pady=10)

        self.tabs["main"] = self.mainTab
        self.TabLoaded["main"] = True

    def create_help_tab(self):
        if self.TabLoaded["help"]:
            return

        self.helpTab = ctk.CTkFrame(self.tabContainer)
        TextWidget = ctk.CTkTextbox(self.helpTab, wrap="word", font=("Arial", 12))
        TextWidget.pack(fill="both", expand=True, padx=15, pady=15)

        HelpMe = """
РУКОВОДСТВО ПО РАСЧЁТУ
—————————————————

ОСНОВНЫЕ ФОРМУЛЫ:
—————————————————
C* = (1/Γ) * √(R * T0)  - характеристическая скорость
Γ = √(k) * (2/(k+1))^((k+1)/(2(k-1)))
Pc = [a * ρ * Ab * C* / A*] ^ (1/(1-n))  - давление в камере
F = Pc * A* * Cf  - тяга
r = a * Pc^n  - скорость горения

ПАРАМЕТРЫ:
—————————————————
T0    - Температура горения (K)
R     - Газовая постоянная (Дж/кг·K)
k     - Показатель адиабаты
a, n  - Коэффициенты скорости горения
ρ     - Плотность топлива (кг/м³)
L     - Длина шашки (м)
Dcore - Диаметр канала (м)
Dout  - Наружный диаметр (м)
Dthroat - Диаметр критики (м)
Dexit - Диаметр среза сопла (м)

ТИПИЧНЫЕ ТОПЛИВА:
—————————————————
KNSB (KNO3+Сорбит) : T0≈1720K, n≈0.32
KNSU (KNO3+Сахар)  : T0≈1700K, n≈0.33
APCP               : T0≈2500K, n≈0.3-0.5

БЕЗОПАСНОСТЬ:
—————————————————
- Запас прочности корпуса > 2
- Kn = 200-400 для любительских топлив
- Не превышайте предел текучести материала
"""
        TextWidget.insert("0.0", HelpMe)
        TextWidget.configure(state="disabled")

        self.tabs["help"] = self.helpTab
        self.TabLoaded["help"] = True

    def create_materials_tab(self):
        if self.TabLoaded["materials"]:
            return

        self.materialsTab = ctk.CTkFrame(self.tabContainer)
        TextWidget = ctk.CTkTextbox(self.materialsTab, wrap="none", font=("Consolas", 11))
        TextWidget.pack(fill="both", expand=True, padx=15, pady=15)

        materials = [
            ["Материал", "Плотность", "Текучесть", "Прочность", "Макс.T"],
            ["", "кг/м³", "МПа", "МПа", "K"],
            ["-" * 12, "-" * 8, "-" * 8, "-" * 8, "-" * 6],
            ["Алюминий 6061-T6", "2700", "275", "310", "500"],
            ["Алюминий 7075-T6", "2810", "505", "570", "480"],
            ["Сталь 4130", "7850", "435", "670", "800"],
            ["Нерж. сталь 304", "8000", "215", "505", "900"],
            ["Титан Ti-6Al-4V", "4430", "880", "950", "700"],
            ["Углепластик", "1600", "400", "600", "450"],
            ["Стеклопластик", "1850", "150", "250", "400"],
        ]

        output = "База данных материялов\n" + "—" * 55 + "\n"
        for row in materials:
            output += f"{row[0]:<18} {row[1]:>8} {row[2]:>8} {row[3]:>8} {row[4]:>6}\n"

        output += "\n" + "—" * 55 + "\n"
        output += "Запас прочности: 2-3x от расчётного напряжения"

        TextWidget.insert("0.0", output)
        TextWidget.configure(state="disabled")

        self.tabs["materials"] = self.materialsTab
        self.TabLoaded["materials"] = True

    def createGraphsTab(self):
        if self.TabLoaded["graphs"]:
            return

        self.graphsTab = ctk.CTkFrame(self.tabContainer)

        frame = ctk.CTkFrame(self.graphsTab)
        frame.pack(expand=True)

        ctk.CTkLabel(frame, text="Гафики", font=("Arial", 20, "bold")).pack(pady=20)
        ctk.CTkLabel(frame, text="В разработке", font=("Arial", 14)).pack()
        ctk.CTkLabel(frame, text="(P(t), F(t), r(t))", font=("Arial", 11), text_color="gray").pack()

        self.tabs["graphs"] = self.graphsTab
        self.TabLoaded["graphs"] = True

    def ShowTab(self, TabName):
        if TabName == "help" and not self.TabLoaded["help"]:
            self.create_help_tab()
        elif TabName == "materials" and not self.TabLoaded["materials"]:
            self.create_materials_tab()
        elif TabName == "graphs" and not self.TabLoaded["graphs"]:
            self.createGraphsTab()

        for tab in self.tabs.values():
            tab.GridRemove()

        if TabName in self.tabs:
            self.tabs[TabName].grid(row=0, column=0, sticky="nsew")

    def getParams(self):
        params = {}
        for key, entry in self.entries.items():
            try:
                val = entry.get().strip()
                if 'e' in val.lower():
                    params[key] = float(val)
                elif '.' in val:
                    params[key] = float(val)
                else:
                    params[key] = int(val)
            except:
                params[key] = 0
        return params

    def setParams(self, params):
        for key, value in params.items():
            if key in self.entries:
                self.entries[key].delete(0, "end")
                self.entries[key].insert(0, str(value))

    def loadInitialData(self):
        success, msg, params = DataManager.loadFromFile()
        if success:
            self.setParams(params)
        else:
            self.setParams(DataManager.getDefaultParams())

    def saveToFile(self):
        success, msg = DataManager.saveToFile(self.getParams())
        self.showResult(msg)

    def loadFromFile(self):
        success, msg, params = DataManager.loadFromFile()
        if success:
            self.setParams(params)
        self.showResult(msg)

    def resetToDefaults(self):
        self.setParams(DataManager.getDefaultParams())
        self.showResult("Сброшено к значениям по умолчанию")

    def showResult(self, text):
        self.resultText.delete("0.0", "end")
        self.resultText.insert("0.0", text)

    def calculate(self):
        params = self.getParams()
        result = RocketMath.fullCalculation(params)

        if result.get('success', False):
            output = f"""
╔══════════════════════════════════════════════════════════════╗
║                    РЕЗУЛЬТАТЫ РАСЧЁТА                        ║
╚══════════════════════════════════════════════════════════════╝

ТЕРМОДИНАМИКА:
   C* = {result['Cstar']:.0f} м/с

ГЕОМЕТРИЯ:
   Ab = {result['Ab'] * 10000:.1f} см²
   A* = {result['Athroat'] * 1e6:.1f} мм²
   Kn = {result['Kn']:.0f}

КАМЕРА СГОРАНИЯ:
   Pc = {result['PcMPa']:.2f} МПа ({result['Pc'] / 101325:.1f} атм)
   r = {result['r'] * 1000:.2f} мм/с

ХАРАКТЕРИСТИКИ:
   Тяга F = {result['F']:.0f} Н ({result['F'] / 4.448:.0f} lbf)
   Cf = {result.get('Cf', 0):.3f}
   Isp = {result.get('Isp', 0):.0f} с
   Расход = {result.get('mdot', 0):.3f} кг/с

ПРОЧНОСТЬ:
   Напряжение = {result['stress'] / 1e6:.1f} МПа
"""
        else:
            output = f"ОШИБКА: {result.get('error', 'Неизвестная ошибка')}"

        self.showResult(output)

    def run(self):
        self.window.mainloop()