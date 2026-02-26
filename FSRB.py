import math

prop = {#тплв KNSB
    "T0": 1720, "R": 197.9, "k": 1.133,
    "a": 5.83e-6, "n": 0.319, "rho": 1890,
}

def CStar(T,R,k):
    g = math.sqrt(k) * (2/(k+1))**((k+1)/(2*(k-1)))
    return (1/g) * math.sqrt(R * T)

def Pc(a,n,rho,Ab,Astar,cs):
    return (a * rho * Ab * cs / Astar) ** (1/(1-n))

def AbCyl(D,L):
    return math.pi * D * L

L, Dcore, Dthroat = 0.3, 0.015, 0.012  # м

Astar = math.pi * (Dthroat/2)**2
Ab = AbCyl(Dcore, L)
Kn = Ab / Astar

cs = CStar(prop["T0"], prop["R"], prop["k"])
P = Pc(prop["a"], prop["n"], prop["rho"], Ab, Astar, cs)
F = P * Astar * 1.5  # Cf=1.5

print(f"Kn={Kn:.0f} | C*={cs:.0f} м/с | P={P/1e6:.2f} МПа | F={F:.0f} Н")