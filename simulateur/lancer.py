"""Point d'entrée en ligne de commande du robot virtuel.

Exemples :
    python lancer.py
    python lancer.py --scenario sol_sec
    python lancer.py --scenario obstacle --vitesse 4
    python lancer.py --une-seule --quiet
"""
import argparse
import sys

from robot_virtuel import RobotVirtuel
from scenarios import SCENARIOS


def main():
    parser = argparse.ArgumentParser(
        description="Lance le robot virtuel RoboAgri-Kin.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Scénarios disponibles : " + ", ".join(SCENARIOS.keys()),
    )
    parser.add_argument(
        "--scenario", default="nominal", choices=list(SCENARIOS.keys()),
        help="scénario de panne à simuler (défaut : nominal)",
    )
    parser.add_argument(
        "--vitesse", type=float, default=1.0,
        help="facteur de vitesse (2 = deux fois plus rapide, défaut 1)",
    )
    parser.add_argument(
        "--une-seule", action="store_true",
        help="ne joue qu'une seule mission puis s'arrête",
    )
    parser.add_argument(
        "--quiet", action="store_true",
        help="affiche uniquement les OK/WARN/ERR (pas les INFO)",
    )
    args = parser.parse_args()

    print(f"Scénario : {args.scenario}")
    print(f"Description : {SCENARIOS[args.scenario]['description']}")
    print()

    robot = RobotVirtuel(
        scenario=args.scenario,
        vitesse=args.vitesse,
        une_seule=args.une_seule,
        verbose=not args.quiet,
    )

    try:
        robot.boucle()
    except KeyboardInterrupt:
        print("\nArrêt demandé.")
        sys.exit(0)


if __name__ == "__main__":
    main()