# Copyright (C) 2026 stepWRK
#
# This file is part of SRBcalculate.
#
# SRBcalculate is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

import math

class RocketMath:

    @staticmethod
    def throatArea(Dthroat): #площадь крит гОрения
        return math.pi * (Dthroat / 2) ** 2

    @staticmethod
    def exitArea(Dexit):
        return math.pi * (Dexit / 2) ** 2

    @staticmethod
    def burnArea(Dcore, L, Ncores=1):# площадь горен
        return math.pi * Dcore * L * Ncores

    @staticmethod
    def gammaFunction(k):
        return math.sqrt(k) * (2 / (k + 1)) ** ((k + 1) / (2 * (k - 1)))

    @staticmethod
    def characteristicVelocity(T0, R, k, etaComb=0.95):# характ скор с уч С
        gamma = RocketMath.gammaFunction(k)
        Cstar_ideal = (1 / gamma) * math.sqrt(R * T0)
        return Cstar_ideal * etaComb

    @staticmethod
    def chamberPressure(a, rho, Ab, Cstar, Athroat, n):
        if Athroat <= 0:
            raise ValueError("Athroat must be > 0")
        return (a * rho * Ab * Cstar / Athroat) ** (1 / (1 - n))

    @staticmethod
    def ThrustCoefficient(k, Pc, Pa, Pe, Ae, Athroat):

        # полн расчёт коэффициента тяги Cf
        # k показатель адиабаты
        # Pc давление в камере Па
        # Pa атмосферное давление Па
        # Pe давление на срезе сопла Па
        # Ae площадь среза сопла м2
        # Athroat площадь критики м2
        # коэффициент расшир сопла
        expansionRatio = Ae / Athroat

        # давлению на срезе сопла (формула из газовой динамики)
        if expansionRatio <= 1:
            Pe = Pc
        else:
            # уровнение для Pe
            # (Ae/A*)² = (1/M²) * [(2/(k+1))*(1 + (k-1)M²/2)]^((k+1)/(k-1))
            # Mach на срезе
            M = RocketMath.machFromAreaRatio(expansionRatio, k)
            Pe = Pc * (1 + (k - 1) / 2 * M ** 2) ** (-k / (k - 1))

        # коэфициент тяги от расширения
        CfThrust = math.sqrt(
            2 * k ** 2 / (k - 1) * (2 / (k + 1)) ** ((k + 1) / (k - 1)) * (1 - (Pe / Pc) ** ((k - 1) / k)))

        # компонент от недог/перерасширения
        CfPressure = (Pe - Pa) / Pc * expansionRatio
        return CfThrust + CfPressure

    @staticmethod
    def machFromAreaRatio(A_ratio, k, M_guess=1.5, tolerance=1e-6):
        M = M_guess
        for _ in range(50):  # максимум 50 итераций
            # функц: f(M) = (A/A*)² - (1/M²) * [(2/(k+1))*(1 + (k-1)M²/2)]^((k+1)/(k-1))
            term1 = (2 / (k + 1)) * (1 + (k - 1) / 2 * M ** 2)
            term2 = term1 ** ((k + 1) / (k - 1))
            A_ratio_calc = (1 / M) * math.sqrt(term2)

            f = A_ratio_calc - A_ratio
            if abs(f) < tolerance:
                return M

            # производная
            df_dM = -1 / M ** 2 * math.sqrt(term2) + (1 / M) * (1 / (2 * math.sqrt(term2))) * \
                    ((k + 1) / (k - 1)) * term1 ** ((k + 1) / (k - 1) - 1) * ((k - 1) / 2) * 2 * M
            M -= f / df_dM

        return M

    @staticmethod
    def thrust(Pc, Athroat, Cf=1.5):
        return Pc * Athroat * Cf

    @staticmethod
    def Kn(Ab, Athroat):
        return Ab / Athroat

    @staticmethod
    def burnRate(Pc, a, n):
        return a * (Pc ** n)

    @staticmethod
    def caseStress(Pc, Dout, wallThick):
        R = Dout / 2
        return Pc * R / wallThick

    @staticmethod
    def propellantMass(rho, L, Dout, Dcore, Ncores=1):# масс топлива
        V_total = math.pi * (Dout / 2) ** 2 * L
        V_core = math.pi * (Dcore / 2) ** 2 * L * Ncores
        return rho * (V_total - V_core)

    @staticmethod
    def burnTime(web, a, Pc, n):# BURN RATE!
        r = RocketMath.burnRate(Pc, a, n)
        return web / r

    @staticmethod
    def specificImpulse(F, mass_flow_rate): # УД в сек
        return F / (mass_flow_rate * 9.80665)

    @staticmethod
    def massFlowRate(Athroat, Pc, Cstar):# массовый расход
        return Athroat * Pc / Cstar

    @staticmethod
    def thrustCoefficientWithLosses(CfIdeal, EtaNozzle=0.97): # физика, мы как бы теряем из-за сопла тягу и тд..
        return CfIdeal * EtaNozzle

    @staticmethod
    def fullCalculation(params):
        try:
            Dthroat = params.get("Dthroat", 0.012)
            Dcore = params.get("Dcore", 0.015)
            Dexit = params.get("Dexit", Dthroat * 3)
            L = params.get("L", 0.3)
            Dout = params.get("Dout", 0.05)
            Ncores = params.get("Ncores", 1)
            wallThick = params.get("wallThick", 0.002)
            etaComb = params.get("etaComb", 0.95)

            Athroat = RocketMath.throatArea(Dthroat)# расчёт площадей
            Aexit = RocketMath.exitArea(Dexit)
            Ab = RocketMath.burnArea(Dcore, L, Ncores)

            Cstar = RocketMath.characteristicVelocity(#термодинафиг
                params["T0"], params["R"], params["k"], etaComb
            )

            Pc = RocketMath.chamberPressure(# давить в камере
                params["a"], params["rho"], Ab, Cstar, Athroat, params["n"]
            )

            Pa = params.get("Pa", 101325)#коэффиц тяги
            Cf = RocketMath.ThrustCoefficient(
                params["k"], Pc, Pa, None, Aexit, Athroat
            )

            etaNozzle = params.get("etaNozzle", 0.97) # юлин сопло потери делает...
            Cf = RocketMath.thrustCoefficientWithLosses(Cf, etaNozzle)

            F = RocketMath.thrust(Pc, Athroat, Cf) # тяга и масс расХод
            mdot = RocketMath.massFlowRate(Athroat, Pc, Cstar)
            Isp = RocketMath.specificImpulse(F, mdot)

            Kn = RocketMath.Kn(Ab, Athroat) # остальная дрибидень
            r = RocketMath.burnRate(Pc, params["a"], params["n"])
            mass = RocketMath.propellantMass(params["rho"], L, Dout, Dcore, Ncores)
            web = (Dout - Dcore) / 2
            tBurn = RocketMath.burnTime(web, params["a"], Pc, params["n"])
            stress = RocketMath.caseStress(Pc, Dout, wallThick)

            return {
                "Cstar": Cstar,
                "Ab": Ab,
                "Athroat": Athroat,
                "Aexit": Aexit,
                "Pc": Pc,
                "PcMPa": Pc / 1_000_000,
                "F": F,
                "Cf": Cf,
                "mdot": mdot,
                "Isp": Isp,
                "Kn": Kn,
                "r": r,
                "mass": mass,
                "tBurn": tBurn,
                "stress": stress,
                "success": True
            }
        except Exception as e:
            return {"success": False, "error": str(e)}