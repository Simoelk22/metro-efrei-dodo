"""
Calcul d'impact environnemental : métro vs voiture.
Sources : ADEME 2023
"""

CO2_METRO_G_PER_KM = 4.1      # gCO2eq / passager.km — métro parisien
CO2_VOITURE_G_PER_KM = 120.0  # gCO2eq / km — voiture moyenne France
VITESSE_METRO_KMH = 25.0       # km/h — vitesse commerciale moyenne métro parisien


def estimer_distance_km(duree_secondes: int) -> float:
    """Estime la distance en km d'après la durée du trajet."""
    return (duree_secondes / 3600) * VITESSE_METRO_KMH


def calculer_co2(distance_km: float) -> dict:
    """
    Calcule les émissions CO2 pour le trajet.

    Retourne un dict :
      distance_km, co2_metro_g, co2_voiture_g, economie_g, ratio
    """
    co2_metro = distance_km * CO2_METRO_G_PER_KM
    co2_voiture = distance_km * CO2_VOITURE_G_PER_KM
    ratio = round(co2_voiture / co2_metro, 1) if co2_metro > 0 else 0
    return {
        "distance_km": round(distance_km, 1),
        "co2_metro_g": round(co2_metro, 1),
        "co2_voiture_g": round(co2_voiture, 1),
        "economie_g": round(co2_voiture - co2_metro, 1),
        "ratio": ratio,
    }
