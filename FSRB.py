# внимание, поддержка этой части кода прекращена!
import os, math
if not os.path.exists("config.txt"):
    with open("config.txt", "w", encoding="utf-8") as f:
        f.write("""# Топливо
T0 = 1720    # Температура K
R = 197.9    # Газовая постоянная
k = 1.133    # Показатель адиабаты
a = 5.83e-6  # Коэф горения
n = 0.319    # Степень
rho = 1890   # Плотность кг/м³

# Геометрия (метры!)
L = 0.3        # Длина заряда
D_core = 0.015 # Диаметр канала
D_out = 0.05   # Наружный диаметр
D_throat = 0.012 # Диаметр критики
""")
    print("заполнить нада")
    exit()

print("шитается")
with open("config.txt", "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            name, value = line.split("=", 1)
            name = name.strip()
            value = value.split("#")[0].strip()
            try:
                if "." in value or "e" in value.lower():
                    globals()[name] = float(value)
                else:
                    globals()[name] = int(value)
                print(f"  {name} = {globals()[name]}")
            except:
                globals()[name] = value

print("""——————
расчёт:""")

A_core = math.pi * (D_core/2)**2
A_throat = math.pi * (D_throat/2)**2
Ab = math.pi * D_core * L
gamma = math.sqrt(k) * (2/(k+1))**((k+1)/(2*(k-1)))
C_star = (1/gamma) * math.sqrt(R * T0)
Pc = (a * rho * Ab * C_star / A_throat) ** (1/(1-n))
Pc_MPa = Pc / 1_000_000
Cf = 1.5
F = Pc * A_throat * Cf

print(f"C* = {C_star:.0f} м/с",
"Ab = {Ab*10000:.2f} см²",
"Kn = {Ab/A_throat:.0f}",
"Pc = {Pc_MPa:.2f} МПа",
f"Тяга = {F:.0f} Н")