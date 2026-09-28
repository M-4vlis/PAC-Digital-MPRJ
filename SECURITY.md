# Segurança

## Estado da versão

A v0.13 é uma candidata de demonstração: a carteira contém dados fictícios e a inteligência histórica contém apenas dados abertos do PNCP. O ambiente atual usa HTTPS e autenticação de demonstração; dados internos reais exigem identidade institucional, monitoração, política de backup e homologação.

## Controles técnicos

- corpo de requisição limitado a 1 MiB;
- CSP, proteção contra enquadramento, restrição de permissões e `no-store` nas APIs;
- identificador de correlação em cada resposta;
- busca de padrões de segredos no CI;
- transmissões SEI/PNCP bloqueadas por desenho.

## Segredos

Nunca versione senhas, tokens, chaves SEI/PNCP ou arquivos `.env`. Use variáveis de ambiente ou o cofre de segredos aprovado pelo MPRJ.

## Integrações

As integrações externas são inativas por desenho. Qualquer ativação exige homologação, credenciais institucionais, trilha de auditoria, controle de repetição e revisão de segurança.

## Relato de vulnerabilidade

Durante a fase de projeto, registre o achado em canal restrito da equipe responsável. Não inclua credenciais, dados pessoais ou informações institucionais sensíveis em issues públicas.
