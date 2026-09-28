# ADR 0012 — fluxos de aprovação configuráveis

**Status:** aceita na v0.9.

## Decisão

Representar o processo de aprovação em quatro entidades independentes: template do fluxo, etapas ordenadas, instância por demanda e decisões imutáveis. A etapa informa o perfil necessário; a API impede decisão por perfil divergente e exige justificativa na rejeição.

## Motivo

As autoridades, alçadas e grupos institucionais ainda dependem de homologação. A configuração em dados permite ajustar essas regras sem reescrever o domínio do PAC.

## Consequências

- autenticação institucional futura deverá fornecer perfis confiáveis, substituindo o perfil demonstrativo enviado na requisição;
- alterações de template não devem reescrever decisões históricas;
- fluxos demonstrativos não constituem norma ou delegação de competência do MPRJ.
