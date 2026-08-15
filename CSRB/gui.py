import customtkinter as ctk
from core import RocketMath
from data import DataManager

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")


class FastGraph(ctk.CTkCanvas):
    def __init__(self, master, color="#00ff00", title="", **kwargs):
        super().__init__(master, bg="#1e1e1e", highlightthickness=0, **kwargs)
        self.color = color
        self.title = title
        self.dataX = [0, 1, 2, 3, 4, 5]
        self.dataY = [0, 10, 20, 15, 5, 0]
        self.minY = 0
        self.maxY = 25
        self.bind("<Configure>", self.onResize)

    def onResize(self, event):
        self.draw()

    def setData(self, xData, yData):
        if xData and yData and len(xData) > 1:
            self.dataX = xData
            self.dataY = yData
            self.minY = min(yData) * 0.9
            self.maxY = max(yData) * 1.1
            if self.minY == self.maxY:
                self.maxY += 1
        self.draw()

    def draw(self):
        self.delete("all")
        w = self.winfo_width()
        h = self.winfo_height()

        if w < 50 or h < 50:
            self.after(100, self.draw)
            return

        self.create_rectangle(0, 0, w, h, fill="#1e1e1e", outline="")

        if len(self.dataX) < 2:
            self.create_line(50, h // 2, w - 50, h // 2, fill=self.color, width=5)
            self.create_text(w // 2, h // 2, text="НЕТ ДАННЫХ", fill="white")
            return

        self.create_text(w // 2, 15, text=self.title, fill="white", font=("Arial", 11, "bold"))

        marginL, marginR, marginT, marginB = 55, 20, 35, 45
        plotW = w - marginL - marginR
        plotH = h - marginT - marginB

        if plotW <= 0 or plotH <= 0:
            return

        for i in range(5):
            y = marginT + plotH * i / 4
            self.create_line(marginL, y, w - marginR, y, fill="#333333", width=1)
            val = self.maxY - (self.maxY - self.minY) * i / 4
            self.create_text(marginL - 5, y, text=f"{val:.1f}", fill="#888888", font=("Arial", 8), anchor="e")

        for i in range(5):
            x = marginL + plotW * i / 4
            self.create_line(x, h - marginB, x, h - marginB + 5, fill="#888888", width=1)
            t = self.dataX[-1] * i / 4 if self.dataX[-1] > 0 else 0
            self.create_text(x, h - marginB + 15, text=f"{t:.2f}", fill="#888888", font=("Arial", 8))

        points = []
        for i in range(len(self.dataX)):
            x = marginL + (self.dataX[i] / max(self.dataX)) * plotW if max(self.dataX) > 0 else marginL
            y = marginT + plotH - (self.dataY[i] - self.minY) / (self.maxY - self.minY) * plotH
            points.extend([x, y])
            self.create_oval(x - 2, y - 2, x + 2, y + 2, fill=self.color, outline="")

        if len(points) >= 4:
            self.create_line(points, fill=self.color, width=2)

        self.create_line(marginL, marginT, marginL, h - marginB, fill="white", width=1)
        self.create_line(marginL, h - marginB, w - marginR, h - marginB, fill="white", width=1)
        self.create_text(w // 2, h - 5, text="Время, с", fill="white", font=("Arial", 9))


class MainWindow:
    def __init__(self):
        self.window = ctk.CTk()
        self.window.title("SRBcalc")
        self.window.geometry("1200x680")
        self.window.minsize(1024, 600)

        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_rowconfigure(0, weight=0)
        self.window.grid_rowconfigure(1, weight=1)

        self.create_top_bar()

        self.tabContainer = ctk.CTkFrame(self.window)
        self.tabContainer.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        self.tabContainer.grid_columnconfigure(0, weight=1)
        self.tabContainer.grid_rowconfigure(0, weight=1)

        self.tabs = {}
        self.tab_loaded = {"main": False, "help": False, "materials": False, "graphs": False}
        self.calculationResult = None

        self.create_main_tab()
        self.show_tab("main")
        self.loadInitialData()

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

        for text, tab_name, color, hover in buttons:
            btn = ctk.CTkButton(
                self.topFrame, text=text,
                command=lambda t=tab_name: self.show_tab(t),
                width=140, height=35, fg_color=color, hover_color=hover, text_color="white"
            )
            btn.pack(side="left", padx=5, pady=5)

    def create_main_tab(self):
        if self.tab_loaded["main"]:
            return

        self.mainTab = ctk.CTkFrame(self.tabContainer)
        self.mainTab.grid_columnconfigure(0, weight=1)
        self.mainTab.grid_columnconfigure(1, weight=1)
        self.mainTab.grid_rowconfigure(0, weight=1)

        leftFrame = ctk.CTkFrame(self.mainTab)
        leftFrame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.entries = {}

        param_sections = [
            ("ПАРАМЕТРЫ ТОПЛИВА", 16, [
                ("Температура T0 (K):", "T0", "1720"),
                ("Газовая постоянная R (Дж/кг·K):", "R", "197.9"),
                ("Показатель адиабаты k:", "k", "1.133"),
                ("Коэф. скорости горения a:", "a", "2.5e-5"),
                ("Показатель степени n:", "n", "0.40"),
                ("Плотность ρ (кг/м³):", "rho", "1890"),
            ]),
            ("ДОП. ПАРАМЕТРЫ", 14, [
                ("КПД камеры:", "etaComb", "0.95"),
                ("КПД сопла:", "etaNozzle", "0.97"),
            ]),
            ("ГЕОМЕТРИЯ (метры)", 16, [
                ("Длина шашки L:", "L", "0.15"),
                ("Диаметр канала Dcore:", "Dcore", "0.018"),
                ("Наруж. диаметр Dout:", "Dout", "0.04"),
                ("Диаметр критики Dthroat:", "Dthroat", "0.007"),
                ("Диаметр среза Dexit:", "Dexit", "0.03"),
                ("Кол-во каналов:", "Ncores", "1"),
            ]),
            ("МАТЕРИАЛ КОРПУСА", 14, [
                ("Толщина стенки (мм):", "wallThick", "2.0"),
                ("Запас прочности:", "safetyFactor", "2.5"),
            ]),
        ]

        for section_title, font_size, params in param_sections:
            ctk.CTkLabel(leftFrame, text=section_title, font=("Arial", font_size, "bold")).pack(pady=(10, 5),
                                                                                                anchor="w", padx=10)
            for label, key, default in params:
                row = ctk.CTkFrame(leftFrame)
                row.pack(fill="x", padx=10, pady=2)
                ctk.CTkLabel(row, text=label, width=210, anchor="w").pack(side="left", padx=5)
                entry = ctk.CTkEntry(row, width=120)
                entry.pack(side="left", padx=5)
                entry.insert(0, default)
                self.entries[key] = entry

        btn_frame = ctk.CTkFrame(leftFrame)
        btn_frame.pack(fill="x", padx=10, pady=15)
        for text, cmd in [("Сохранить", self.saveToFile), ("Загрузить", self.loadFromFile),
                          ("Сброс", self.resetToDefaults)]:
            ctk.CTkButton(btn_frame, text=text, command=cmd, width=100, height=32).pack(side="left", padx=5)

        rightFrame = ctk.CTkFrame(self.mainTab)
        rightFrame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        ctk.CTkLabel(rightFrame, text="РЕЗУЛЬТАТЫ РАСЧЁТА", font=("Arial", 18, "bold")).pack(pady=10)

        self.resultText = ctk.CTkTextbox(rightFrame, wrap="word", font=("Consolas", 11))
        self.resultText.pack(fill="both", expand=True, padx=10, pady=5)

        ctk.CTkButton(rightFrame, text="РАССЧИТАТЬ", command=self.calculate, height=45,
                      font=("Arial", 16, "bold"), fg_color="#2e7d32", hover_color="#1e5a20").pack(pady=10)

        self.tabs["main"] = self.mainTab
        self.tab_loaded["main"] = True

    def create_help_tab(self):
        if self.tab_loaded["help"]:
            return
        self.helpTab = ctk.CTkFrame(self.tabContainer)
        text_widget = ctk.CTkTextbox(self.helpTab, wrap="word", font=("Consolas", 11))
        text_widget.pack(fill="both", expand=True, padx=15, pady=15)

        help_text = """
=== ТТРД КАЛЬКУЛЯТОР ===
Руководство пользователя

1. ВВОД ДАННЫХ
   - Заполните все поля на вкладке "Основной расчёт"
   - Параметры топлива: T0, R, k, a, n, rho
   - Геометрия: L, Dcore, Dout, Dthroat, Ncores
   - Все размеры в метрах

2. РАСЧЁТ
   - Нажмите кнопку "РАССЧИТАТЬ"
   - Результаты появятся справа
   - При ошибках ввода увидите сообщение

3. ОСНОВНЫЕ ФОРМУЛЫ
   Pc = (a * rho * Ab * C* / At)^(1/(1-n))
   r = a * Pc^n
   F = Pc * At
   Isp = F / (mdot * g0)

4. ЕДИНИЦЫ ИЗМЕРЕНИЯ
   - Давление: Па (результат в МПа)
   - Температура: K
   - Размеры: метры
   - Масса: кг
   - Время: секунды

5. ГРАФИКИ
   - Перейдите на вкладку "Графики"
   - Нажмите "Обновить" после расчёта
   - Отображаются: давление, тяга, масса

6. СОХРАНЕНИЕ
   - Кнопка "Сохранить" - запись параметров в config.txt
   - Кнопка "Загрузить" - чтение из config.txt
   - Кнопка "Сброс" - возврат к значениям по умолчанию

7. ТИПИЧНЫЕ ЗНАЧЕНИЯ
   HTPB-топливо:
   T0 = 1720 K, R = 197.6, k = 1.133
   a = 5.83e-6, n = 0.319, rho = 1892

   Для малых двигателей (до 1000 Н):
   Dthroat = 0.005-0.015 м
   Dcore = 0.015-0.030 м
   Dout = 0.030-0.060 м
   L = 0.10-0.30 м

8. ОГРАНИЧЕНИЯ
   - Dout > Dcore > 0
   - Dthroat > 0
   - Все параметры должны быть положительными
   - n обычно в диапазоне 0.1-0.8
"""
        text_widget.insert("0.0", help_text)
        text_widget.configure(state="disabled")
        self.tabs["help"] = self.helpTab
        self.tab_loaded["help"] = True

    def create_materials_tab(self):
        if self.tab_loaded["materials"]:
            return

        self.materialsTab = ctk.CTkFrame(self.tabContainer)
        self.materialsTab.grid_columnconfigure(0, weight=1)
        self.materialsTab.grid_rowconfigure(0, weight=0)
        self.materialsTab.grid_rowconfigure(1, weight=1)

        topFrame = ctk.CTkFrame(self.materialsTab)
        topFrame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        ctk.CTkLabel(topFrame, text="ВЫБОР МАТЕРИАЛА ТОПЛИВА", font=("Arial", 16, "bold")).pack(pady=5)

        materials_db = {
            "HTPB (стандартный)": {
                "T0": 1720, "R": 197.6, "k": 1.133,
                "a": 5.83e-6, "n": 0.319, "rho": 1892,
                "desc": "Полибутадиен с гидроксильными группами\nСтандартное связующее для ТТРД"
            },
            "HTPB (высокое содержание Al)": {
                "T0": 1850, "R": 175.0, "k": 1.15,
                "a": 4.2e-6, "n": 0.35, "rho": 1950,
                "desc": "18-20% алюминия\nПовышенная плотность и температура"
            },
            "HTPB (низкое содержание Al)": {
                "T0": 1650, "R": 205.0, "k": 1.12,
                "a": 6.1e-6, "n": 0.30, "rho": 1850,
                "desc": "5-10% алюминия\nМеньше температуры, выше газовой постоянной"
            },
            "PBAN": {
                "T0": 1680, "R": 200.0, "k": 1.14,
                "a": 5.5e-6, "n": 0.32, "rho": 1880,
                "desc": "Полибутадиен-акрилонитрил\nИспользуется в Solid Rocket Boosters"
            },
            "CТПВ (нитроцеллюлозный)": {
                "T0": 1750, "R": 195.0, "k": 1.13,
                "a": 6.5e-6, "n": 0.28, "rho": 1910,
                "desc": "Смесевое твёрдое топливо\nВысокая скорость горения"
            },
            "APCP (стандартный)": {
                "T0": 1700, "R": 198.0, "k": 1.13,
                "a": 5.0e-6, "n": 0.33, "rho": 1890,
                "desc": "Аммоний перхлорат композит\nНаиболее распространённый тип"
            }
        }

        self.selected_material = "HTPB (стандартный)"

        def on_material_select(choice):
            self.selected_material = choice
            if choice in materials_db:
                desc = materials_db[choice]["desc"]
                desc_text.configure(state="normal")  # Временно разблокируем
                desc_text.delete("0.0", "end")
                desc_text.insert("0.0", desc)
                desc_text.configure(state="disabled")  # Снова блокируем

        def apply_selected():
            props = materials_db.get(self.selected_material)
            if not props:
                self.showResult("Выберите материал из списка")
                return

            mappings = {
                'T0': 'T0',
                'R': 'R',
                'k': 'k',
                'a': 'a',
                'n': 'n',
                'rho': 'rho'
            }

            for prop_key, entry_key in mappings.items():
                if prop_key in props and entry_key in self.entries:
                    self.entries[entry_key].delete(0, "end")
                    value = props[prop_key]
                    if isinstance(value, float) and value < 0.001:
                        self.entries[entry_key].insert(0, f"{value:.2e}")
                    else:
                        self.entries[entry_key].insert(0, str(value))

            self.showResult(f"Загружены параметры: {self.selected_material}")

        material_menu = ctk.CTkOptionMenu(
            topFrame,
            values=list(materials_db.keys()),
            variable=ctk.StringVar(value="HTPB (стандартный)"),
            command=on_material_select,
            width=300
        )
        material_menu.pack(pady=5)

        desc_text = ctk.CTkTextbox(topFrame, height=80, wrap="word", font=("Arial", 11))
        desc_text.pack(fill="x", padx=10, pady=5)

        desc_text.insert("0.0", materials_db["HTPB (стандартный)"]["desc"])
        desc_text.configure(state="disabled")

        ctk.CTkButton(
            topFrame,
            text="Применить параметры",
            command=apply_selected,
            height=35,
            fg_color="#2e7d32",
            hover_color="#1e5a20"
        ).pack(pady=5)

        bottomFrame = ctk.CTkFrame(self.materialsTab)
        bottomFrame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        ctk.CTkLabel(bottomFrame, text="СВОЙСТВА МАТЕРИАЛОВ", font=("Arial", 14, "bold")).pack(pady=5)

        table_text = ctk.CTkTextbox(bottomFrame, wrap="none", font=("Consolas", 10))
        table_text.pack(fill="both", expand=True, padx=10, pady=5)

        table = "┌─────────────────────┬──────────┬──────────┬──────────┬────────────┬────────────┬──────────┐\n"
        table += "│ Материал            │ T0, K    │ R, Дж/кг │ k        │ a          │ n          │ ρ, кг/м³ │\n"
        table += "├─────────────────────┼──────────┼──────────┼──────────┼────────────┼────────────┼──────────┤\n"

        for name, props in materials_db.items():
            name_display = name[:20].ljust(20)
            table += f"│ {name_display}│ {props['T0']:>8} │ {props['R']:>8} │ {props['k']:>8} │ {props['a']:>10.2e} │ {props['n']:>10} │ {props['rho']:>8} │\n"

        table += "└─────────────────────┴──────────┴──────────┴──────────┴────────────┴────────────┴──────────┘"

        table_text.insert("0.0", table)
        table_text.configure(state="disabled")

        self.tabs["materials"] = self.materialsTab
        self.tab_loaded["materials"] = True

    def create_graphs_tab(self):
        if self.tab_loaded["graphs"]:
            return

        self.graphsTab = ctk.CTkFrame(self.tabContainer)
        self.graphsTab.grid_columnconfigure((0, 1, 2), weight=1)
        self.graphsTab.grid_rowconfigure(0, weight=0)
        self.graphsTab.grid_rowconfigure(1, weight=1)

        controlFrame = ctk.CTkFrame(self.graphsTab)
        controlFrame.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky="ew")

        ctk.CTkLabel(controlFrame, text="ГРАФИКИ ХАРАКТЕРИСТИК", font=("Arial", 18, "bold")).pack(side="left", padx=10)
        ctk.CTkButton(controlFrame, text="Обновить", command=self.updateGraphs, width=100).pack(side="right", padx=10)

        self.graph1 = FastGraph(self.graphsTab, color="#00ff00", title="ДАВЛЕНИЕ В КАМЕРЕ")
        self.graph1.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

        self.graph2 = FastGraph(self.graphsTab, color="#ff4444", title="ТЯГА")
        self.graph2.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")

        self.graph3 = FastGraph(self.graphsTab, color="#4488ff", title="МАССА ТОПЛИВА")
        self.graph3.grid(row=1, column=2, padx=5, pady=5, sticky="nsew")

        ctk.CTkLabel(self.graphsTab, text="Давление, МПа", font=("Arial", 10)).grid(row=2, column=0, pady=(0, 5))
        ctk.CTkLabel(self.graphsTab, text="Тяга, Н", font=("Arial", 10)).grid(row=2, column=1, pady=(0, 5))
        ctk.CTkLabel(self.graphsTab, text="Масса, кг", font=("Arial", 10)).grid(row=2, column=2, pady=(0, 5))

        self.tabs["graphs"] = self.graphsTab
        self.tab_loaded["graphs"] = True

        if self.calculationResult:
            self.updateGraphs()

    def updateGraphs(self):
        if not self.calculationResult:
            return

        timeEvo = self.calculationResult.get('timeEvolution')
        if not timeEvo:
            return

        times = timeEvo.get('times', [])
        if not times:
            return

        self.graph1.setData(times, timeEvo.get('pressuresMpa', []))
        self.graph2.setData(times, timeEvo.get('thrusts', []))
        self.graph3.setData(times, timeEvo.get('masses', []))

    def show_tab(self, tab_name):
        if tab_name == "help" and not self.tab_loaded["help"]:
            self.create_help_tab()
        elif tab_name == "materials" and not self.tab_loaded["materials"]:
            self.create_materials_tab()
        elif tab_name == "graphs" and not self.tab_loaded["graphs"]:
            self.create_graphs_tab()

        for tab in self.tabs.values():
            tab.grid_remove()
        if tab_name in self.tabs:
            self.tabs[tab_name].grid(row=0, column=0, sticky="nsew")

    def getParams(self):
        params = {}
        for key, entry in self.entries.items():
            try:
                val = entry.get().strip()
                if not val:
                    params[key] = 0
                    continue
                if '.' in val or 'e' in val.lower() or 'E' in val.lower():
                    params[key] = float(val)
                else:
                    params[key] = int(val)
            except ValueError:
                params[key] = 0
            except:
                params[key] = 0

        defaults = {
            'Ncores': 1,
            'etaComb': 0.95,
            'wallThick': 0.002,
            'safetyFactor': 2.5
        }
        for key, default in defaults.items():
            if key not in params or params[key] == 0:
                params[key] = default

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

        errors = []
        warnings = []

        required = {
            'Dthroat': 'Диаметр критики',
            'Dcore': 'Диаметр канала',
            'Dout': 'Наружный диаметр',
            'L': 'Длина шашки',
            'T0': 'Температура',
            'R': 'Газовая постоянная',
            'rho': 'Плотность'
        }

        for key, name in required.items():
            if params.get(key, 0) <= 0:
                errors.append(f"X {name} должен быть > 0")

        if params.get('Dout', 0) <= params.get('Dcore', 0):
            errors.append("X Наружный диаметр (Dout) должен быть больше диаметра канала (Dcore)")

        if params.get('Ncores', 1) < 1:
            errors.append("X Количество каналов (Ncores) должно быть >= 1")

        if params.get('Dthroat', 0) >= params.get('Dcore', 0):
            warnings.append("! Диаметр критики (Dthroat) >= диаметра канала (Dcore)")

        if params.get('T0', 0) > 4000:
            warnings.append("! Температура > 4000 K - проверьте ввод")

        if params.get('n', 0) < 0.1 or params.get('n', 0) > 0.8:
            warnings.append("! Показатель степени n вне диапазона 0.1-0.8")

        if errors:
            msg = "ОШИБКИ ВВОДА:\n\n" + "\n".join(errors)
            if warnings:
                msg += "\n\n" + "\n".join(warnings)
            self.showResult(msg)
            return

        if warnings:
            self.showResult("ПРЕДУПРЕЖДЕНИЯ:\n\n" + "\n".join(warnings) + "\n\nРасчёт продолжен...")

        self.calculationResult = RocketMath.fullCalculation(params)

        if self.calculationResult and self.calculationResult.get('success'):
            r = self.calculationResult
            output = f"""
РЕЗУЛЬТАТЫ РАСЧЁТА

ТЕРМОДИНАМИКА:
   C* = {r['Cstar']:.0f} м/с

ГЕОМЕТРИЯ:
   Ab = {r['Ab'] * 10000:.1f} см2
   A* = {r['Athroat'] * 1e6:.1f} мм2
   Kn = {r['Kn']:.0f}

КАМЕРА СГОРАНИЯ:
   Pc = {r['PcMPa']:.2f} МПа ({r['Pc'] / 101325:.1f} атм)
   r = {r['r'] * 1000:.2f} мм/с

ХАРАКТЕРИСТИКИ:
   Тяга F = {r['F']:.0f} Н
   Isp = {r['Isp']:.0f} с
   Расход = {r['mdot']:.3f} кг/с
   Масса топлива = {r['mass']:.3f} кг
   Время горения = {r['tBurn']:.2f} с

ПРОЧНОСТЬ:
   Напряжение = {r['stress'] / 1e6:.1f} МПа
"""
            self.showResult(output)
        else:
            error = self.calculationResult.get('error', 'Unknown') if self.calculationResult else 'No result'
            self.showResult(f"ОШИБКА РАСЧЁТА:\n{error}")

        if self.tab_loaded.get("graphs") and hasattr(self, 'graph1'):
            self.updateGraphs()

    def run(self):
        self.window.mainloop()