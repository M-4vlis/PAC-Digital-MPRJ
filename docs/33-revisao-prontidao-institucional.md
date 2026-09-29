# Revisão de prontidão institucional — v1.0.0-rc.2

Data da revisão: 29/09/2026.

## Objetivo

Conferir a implementação contra o propósito original do PAC Digital MPRJ e contra as inclusões posteriores, distinguindo claramente o que funciona, o que é demonstrativo e o que depende de homologação institucional.

## Achados tratados nesta versão

| Prioridade | Apontamento | Causa confirmada | Tratamento |
|---|---|---|---|
| Crítica | Cadastro concluía no servidor, exibia sucesso e erro `Cannot read properties of null (reading 'reset')`, e a carteira só atualizava após recarregar | O componente era desmontado antes de o código chamar `reset()` no formulário | O formulário permanece montado até criação, eventual upload e recarga; depois é limpo e fechado. Teste de integração cobre criação e leitura imediata |
| Alta | Valor estimado era digitado como número cru | Campo numérico sem máscara nem decomposição de quantidade e valor unitário | Entrada monetária em reais, com separação brasileira; quantidade × valor unitário calcula e envia o total, validado novamente pela API |
| Alta | Formulário não reunia os elementos mínimos do PAC/MPRJ | Modelo inicial reduzia a demanda a objeto, unidade, categoria, data e total | Incluídos justificativa, quantidade, unidade de medida, responsável, prioridade, período, correlação/dependência, renovação e dados opcionais de catálogo |
| Alta | Requisitante não corrigia nem retirava cadastro indevido | Não havia endpoints nem controles de interface | Edição cria nova versão; retirada é exclusão lógica com justificativa e auditoria. O requisitante só pode fazê-las enquanto a demanda está em rascunho e não iniciada |
| Alta | Não havia documento de DFD | Modelo não possuía armazenamento de anexos | Upload e download de PDF, DOC e DOCX, limite de 8 MiB, verificação mínima de assinatura do arquivo, metadados, hash técnico interno e volume persistente de produção |
| Alta | Seis prazos eram apresentados ao lado de 964 contratos sem explicação suficiente | População importada e amostra temporal apareciam como indicadores equivalentes | Interface agora mostra `6 de 964`, taxa de cobertura, denominador de cada percentil e bloqueio explícito de calibração abaixo de 30 casos por categoria |
| Média | P75 não era explicado | Rótulo estatístico sem definição de negócio | P50 e P75 são definidos na tela; P75 não é apresentado como prazo normativo nem meta |
| Média | Hash SHA-256 aparecia para o público | Evidência técnica de integridade foi levada à interface de negócio | Hash permanece no banco/API para auditoria, mas a tela exibe apenas versão, data e condição de publicação controlada |

## Resultado funcional atual

Funcionam no código e são testados: cadastro completo; máscara e cálculo monetário; histórico de versões; edição e retirada governadas; DFD; revisões aprovadas; adequação pós-LOA; transições de execução; retroplanejamento; riscos explicáveis; aprovações sequenciais; relatórios; exportações; snapshot público; importação pública PNCP; pré-validação local do PCA; vínculo local com número SEI; auditoria; backup e implantação conteinerizada.

Não estão ativados e não devem ser apresentados como concluídos: autenticação institucional, autorização confiável por perfil/unidade, chamadas ao SEI-MPRJ e transmissão ao PNCP. O código atual contém pontos de integração e validação local; as conexões reais exigem dados, credenciais, autorização e homologação do MPRJ.

## Riscos residuais para produção institucional

1. O perfil recebido em `X-Actor-Role` serve apenas à demonstração. Em produção ele deve vir de identidade institucional confiável e não do navegador.
2. O endereço atual em VPS é ambiente controlado de demonstração, não domínio institucional.
3. A base histórica PNCP possui 964 contratos importados, porém a amostra temporal produtiva observada antes desta correção tinha seis casos e não é representativa. O motor ignora essa referência enquanto cada categoria não atingir ao menos 30 observações válidas.
4. Os prazos do retroplanejamento são configuráveis e não normativos; a área competente deve homologá-los.
5. Arquivos DFD devem, na implantação institucional, usar armazenamento, antivírus, retenção e classificação de acesso definidos pela TI.

## Próxima decisão de homologação

Validar com Secretaria-Geral, área jurídica, contratação, TI, segurança e encarregado de dados: formulário, calendário, competências, fluxos, alçadas, perfis, classificação de documentos, parâmetros de risco e contratos de integração. Nenhum desses valores deve ser presumido pelo software.
