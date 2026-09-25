# Roteiro de demonstração executiva — 7 minutos

## 1. Problema e proposta — 45 segundos

O PAC deixa de ser uma planilha estática e passa a ser uma carteira governada: cada demanda tem responsável, valor, prazo, situação, risco, justificativas e histórico preservado.

## 2. Visão executiva — 90 segundos

Abra **Visão executiva**. Mostre planejado × executado, distribuição da carteira, alterações e demandas prioritárias. Reforce que o risco é explicável e que os dados são fictícios.

## 3. Da demanda ao detalhe — 2 minutos

Abra uma demanda de risco alto. Mostre valores, data desejada, motivos do risco, marcos de retroplanejamento, pendência de catálogo PNCP, vínculo SEI e histórico. Explique que os prazos são configuráveis e não normativos.

## 4. Integrações — 90 segundos

Abra **Integrações**. Demonstre que SEI!, PCA/PNCP e identidade institucional são adaptadores separados. Destaque que nenhuma transmissão está ativa antes de homologação e autorização.

## 5. Governança — 60 segundos

Abra **Governança**. Mostre a trilha de eventos, versionamento, justificativas e separação entre planejamento e execução.

## 6. Encerramento — 45 segundos

Mensagem final: a plataforma já demonstra o ciclo completo e é portátil; para produção, faltam conexões e decisões institucionais — identidade, credenciais SEI/PNCP, domínio/HTTPS e validação das áreas responsáveis — e não reconstrução do produto.

## Perguntas que devem ser antecipadas

- **Usa dados reais?** Não. A demonstração contém apenas dados fictícios.
- **Já publica no PNCP?** Não. Gera e valida o payload localmente; publicar exige homologação e credencial.
- **Integra com o SEI?** A arquitetura e o adaptador estão preparados para o Web Service oficial; ativação depende do cadastro e das permissões na instância MPRJ.
- **Depende de nuvem específica?** Não. Pode operar em VPS, datacenter ou infraestrutura institucional com contêineres e PostgreSQL.
- **Os prazos são normas?** Não. São parâmetros de gestão configuráveis e explicitamente não normativos.
