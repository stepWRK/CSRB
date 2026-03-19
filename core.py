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
    def thrustCoefficient(k, Pc, Pa=101325, expansionRatio=1):
        return 1.5   # просто вариант, напомните автору доделать, если автор не забыл, а автор забыл

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
    def fullCalculation(params):
        try:
            Dthroat = params.get("Dthroat", 0.012)# основ параметры
            Dcore = params.get("Dcore", 0.015)
            L = params.get("L", 0.3)
            Dout = params.get("Dout", 0.05)
            Ncores = params.get("Ncores", 1)
            wallThick = params.get("wallThick", 0.002)
            etaComb = params.get("etaComb", 0.95)

            Athroat = RocketMath.throatArea(Dthroat)# площади
            Ab = RocketMath.burnArea(Dcore, L, Ncores)

            Cstar = RocketMath.characteristicVelocity(# я забыл что это, позже вспомню, завтра, если сейчас завтра то перечитай
                params["T0"], params["R"], params["k"], etaComb
            )

            Pc = RocketMath.chamberPressure(# давление
                params["a"], params["rho"], Ab, Cstar, Athroat, params["n"]
            )

            Cf = RocketMath.thrustCoefficient(params["k"], Pc)
            F = RocketMath.thrust(Pc, Athroat, Cf)# тяга

            Kn = RocketMath.Kn(Ab, Athroat)# Kn

            r = RocketMath.burnRate(Pc, params["a"], params["n"])# скорость горения

            mass = RocketMath.propellantMass(params["rho"], L, Dout, Dcore, Ncores)# масса топлива

            web = (Dout - Dcore) / 2# время горения (толщина СВОда)
            t_burn = RocketMath.burnTime(web, params["a"], Pc, params["n"])

            stress = RocketMath.caseStress(Pc, Dout, wallThick)# напряжение в корпусе

            return {
                "Cstar": Cstar,
                "Ab": Ab,
                "Athroat": Athroat,
                "Pc": Pc,
                "PcMPa": Pc / 1_000_000,
                "F": F,
                "Kn": Kn,
                "r": r,
                "mass": mass,
                "t_burn": t_burn,
                "stress": stress,
                "success": True
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }