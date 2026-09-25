# PAC Digital MPRJ

Plataforma demonstrativa, open source e portátil para governança do Plano Anual de Contratações do MPRJ. Dados e perfis são estritamente fictícios.

## Executar

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
alembic upgrade head
python -m uvicorn app.main:app --reload
```

Em outro terminal:

```powershell
cd frontend
pnpm install
pnpm run build
```

Consulte `STATUS.md`, `docs/19-vertical-v0.6.md` e `docs/20-integracao-sei.md`.
