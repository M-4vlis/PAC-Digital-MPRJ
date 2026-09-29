import argparse
from datetime import datetime

from .database import SessionLocal
from .pncp_history import sync_history

def main():
    parser = argparse.ArgumentParser(description="Importa contratos públicos do PNCP restritos ao CNPJ do MPRJ.")
    parser.add_argument("--start-year", type=int, default=2022)
    parser.add_argument("--end-year", type=int, default=datetime.now().year)
    parser.add_argument("--enrich-limit", type=int, default=250)
    parser.add_argument("--request-delay", type=float, default=.75, help="Intervalo em segundos entre consultas de enriquecimento.")
    args = parser.parse_args()
    with SessionLocal() as db:
        print(sync_history(db, args.start_year, args.end_year, args.enrich_limit, request_delay=max(0, args.request_delay)))

if __name__ == "__main__": main()
