# Copyright (C) 2026 stepWRK
#
# This file is part of SRBcalculate.
#
# SRBcalculate is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

import math #  и тут математике!

class RocketMath:

    @staticmethod
    def throatArea(Dthroat):
        return math.pi * (Dthroat / 2) ** 2

    @staticmethod
    def burnArea(Dcore, L, Ncores=1):
        return math.pi * Dcore * L * Ncores

    @staticmethod
    def gammaFunction(k):
        return math.sqrt(k) * (2 / (k + 1)) ** ((k + 1) / (2 * (k - 1)))

    @staticmethod
    def characteristicVelocity(T0, R, k, etaComb=0.95):
        gamma = RocketMath.gammaFunction(k)
        return (1 / gamma) * math.sqrt(R * T0) * etaComb

    @staticmethod
    def chamberPressure(a, rho, Ab, Cstar, Athroat, n):
        if Athroat <= 0 or Ab <= 0:
            return 0
        return (a * rho * Ab * Cstar / Athroat) ** (1 / (1 - n))

    @staticmethod
    def burnRate(Pc, a, n):
        return a * (Pc ** n) if Pc > 0 else 0

    @staticmethod
    def massFlowRate(Athroat, Pc, Cstar):
        return Athroat * Pc / Cstar if Cstar > 0 else 0

    @staticmethod
    def propellantMass(rho, L, Dout, Dcore, Ncores=1):
        V_total = math.pi * (Dout / 2) ** 2 * L
        V_core = math.pi * (Dcore / 2) ** 2 * L * Ncores
        return rho * (V_total - V_core)

    @staticmethod
    def calculateTimeEvolution(params, numPoints=200):
        Dthroat = params.get("Dthroat", 0.007)
        Dcore   = params.get("Dcore", 0.018)
        L       = params.get("L", 0.200)
        Dout    = params.get("Dout", 0.040)
        Ncores  = params.get("Ncores", 1)
        etaComb = params.get("etaComb", 0.95)
        T0      = params.get("T0", 1720)
        R_gas   = params.get("R", 197.9)
        k       = params.get("k", 1.13)
        a       = params.get("a", 2.5e-5)  #реализме ( увеличено для него)
        n       = params.get("n", 0.40)
        rho     = params.get("rho", 1890)

        Athroat = RocketMath.throatArea(Dthroat)
        if Athroat <= 0:
            return {"success": False, "error": "Athroat must be > 0"}

        Cstar = RocketMath.characteristicVelocity(T0, R_gas, k, etaComb)

        web = (Dout - Dcore) / 2.0
        total_mass = RocketMath.propellantMass(rho, L, Dout, Dcore, Ncores)

        Ab0 = math.pi * Dcore * L * Ncores
        Pc0 = RocketMath.chamberPressure(a, rho, Ab0, Cstar, Athroat, n)
        F0  = Pc0 * Athroat
        r0  = RocketMath.burnRate(Pc0, a, n)

        t_max = web / r0 if r0 > 0 else 1.0
        dt = t_max / numPoints

        print(f"[LOG 1] Dcore={Dcore*1000:.1f}mm, Dout={Dout*1000:.1f}mm, Throat={Dthroat*1000:.1f}mm")
        print(f"[LOG 2] Pc0={Pc0/1e6:.2f}MPa, r0={r0*1000:.2f}mm/s, t_burn_est={t_max:.2f}s")

        times     = [0.0]
        pressures = [Pc0]
        thrusts   = [F0]
        masses    = [total_mass]

        current_web = web
        current_Dcore = Dcore
        remaining_mass = total_mass
        burn_index = numPoints

        for i in range(1, numPoints):
            t = i * dt

            if pressures[-1] > 0:
                mdot = RocketMath.massFlowRate(Athroat, pressures[-1], Cstar)
                remaining_mass -= mdot * dt
            if remaining_mass < 0:
                remaining_mass = 0

            Ab = math.pi * current_Dcore * L * Ncores
            Pc = RocketMath.chamberPressure(a, rho, Ab, Cstar, Athroat, n)

            if current_web <= 0 or remaining_mass <= 0 or Pc < 100000:
                if burn_index == numPoints:
                    burn_index = i
                for j in range(i, numPoints):
                    times.append(j * dt)
                    pressures.append(0.0)
                    thrusts.append(0.0)
                    masses.append(remaining_mass)
                break

            r = RocketMath.burnRate(Pc, a, n)
            F = Pc * Athroat

            times.append(t)
            pressures.append(Pc)
            thrusts.append(F)
            masses.append(remaining_mass)
            current_web -= r * dt
            if current_web < 0:
                current_web = 0
            current_Dcore = Dout - 2 * current_web

        end_idx = min(burn_index + 5, len(times))
        times     = times[:end_idx]
        pressures = pressures[:end_idx]
        thrusts   = thrusts[:end_idx]
        masses    = masses[:end_idx]

        print(f"[LOG 3] Mass: {masses[0]:.3f} -> {masses[-1]:.3f} kg, Pc_max={max(pressures)/1e6:.2f}MPa, F_max={max(thrusts):.0f}N")

        total_impulse = 0
        for i in range(len(times) - 1):
            dt_actual = times[i+1] - times[i]
            F_avg = (thrusts[i] + thrusts[i+1]) / 2
            total_impulse += F_avg * dt_actual

        return {
            "times": times,
            "pressures": pressures,
            "pressuresMpa": [p / 1e6 for p in pressures],
            "thrusts": thrusts,
            "masses": masses,
            "totalImpulse": total_impulse,
            "avgPressure": sum(pressures) / len(pressures) if pressures else 0,
            "maxPressure": max(pressures) if pressures else 0,
            "avgThrust": sum(thrusts) / len(thrusts) if thrusts else 0,
            "maxThrust": max(thrusts) if thrusts else 0,
            "burnTime": times[-1] if times else 0,
            "propellantMass": total_mass,
            "success": True
        }

    @staticmethod
    def fullCalculation(params):
        print(f"[LOG 4] fullCalculation started")
        try:
            Dthroat = params.get("Dthroat", 0.007)
            Dcore   = params.get("Dcore", 0.018)
            L       = params.get("L", 0.200)
            Dout    = params.get("Dout", 0.040)
            Ncores  = params.get("Ncores", 1)
            wallThick = params.get("wallThick", 0.003)
            etaComb = params.get("etaComb", 0.95)
            T0      = params.get("T0", 1720)
            R_gas   = params.get("R", 197.9)
            k       = params.get("k", 1.13)
            a       = params.get("a", 2.5e-5)
            n       = params.get("n", 0.40)
            rho     = params.get("rho", 1890)

            Athroat = RocketMath.throatArea(Dthroat)
            Ab = math.pi * Dcore * L * Ncores
            Cstar = RocketMath.characteristicVelocity(T0, R_gas, k, etaComb)
            Pc = RocketMath.chamberPressure(a, rho, Ab, Cstar, Athroat, n)

            F = Pc * Athroat
            mdot = RocketMath.massFlowRate(Athroat, Pc, Cstar)
            Isp = F / (mdot * 9.80665) if mdot > 0 else 0
            Kn = Ab / Athroat if Athroat > 0 else 0
            r = RocketMath.burnRate(Pc, a, n)
            mass = RocketMath.propellantMass(rho, L, Dout, Dcore, Ncores)
            web = (Dout - Dcore) / 2
            tBurn = web / r if r > 0 else 0
            stress = Pc * (Dout / 2) / wallThick if wallThick > 0 else 0

            timeEvolution = RocketMath.calculateTimeEvolution(params)

            print(f"[LOG 4] Done: Pc={Pc/1e6:.2f}MPa, F={F:.0f}N, Mass={mass:.3f}kg")

            return {
                "Cstar": Cstar,
                "Ab": Ab,
                "Athroat": Athroat,
                "Pc": Pc,
                "PcMPa": Pc / 1_000_000,
                "F": F,
                "mdot": mdot,
                "Isp": Isp,
                "Kn": Kn,
                "r": r,
                "mass": mass,
                "tBurn": tBurn,
                "stress": stress,
                "timeEvolution": timeEvolution,
                "success": True
            }
        except Exception as e:
            print(f"[LOG 4] ERROR: {e}")
            return {"success": False, "error": str(e)}