# Matriz de requisitos do cadastro da demanda

## Norma institucional adotada

A fonte normativa primária usada nesta revisão é a [Resolução GPGJ nº 2.326/2020](https://www.mprj.mp.br/documents/20184/2156686/consolidado_2326.pdf/6afeaac9-695c-50ea-6ac6-5e62cb830744?t=1633441582621), vigente e sem alterações indicadas na consolidação consultada em 29/09/2026.

| Exigência | Base | Campo/controle implementado | Validação |
|---|---|---|---|
| Descrição sucinta do objeto | art. 2º, I | `title` | 5 a 240 caracteres |
| Quantidades | art. 2º, I | `quantity` | maior que zero, até quatro casas decimais |
| Unidade de medida | art. 2º, I | `unit_measure` | obrigatória |
| Justificativa | art. 2º, II | `justification` | obrigatória, mínimo de 10 caracteres |
| Estimativa preliminar | art. 2º, III | `unit_value` e `original_value` | total deve corresponder a quantidade × valor unitário |
| Data ou período desejado | art. 2º, IV | `desired_start_date` e `desired_date` | fim obrigatório; início não pode ser posterior ao fim |
| Correlação com outra contratação | art. 2º, V | `dependency_description` | campo explícito, admite declaração de inexistência em branco |
| Contratação ou prorrogação | art. 2º, caput | `renewal_contract` | indicador booleano |
| Inclusão, exclusão ou redimensionamento com justificativa | arts. 4º e 6º | versão, revisão, retirada lógica e justificativas | histórico e auditoria preservados |
| Adequação posterior à LOA | art. 5º | valores original, revisado e ajustado; `loa_justification` | endpoint próprio e nova versão |
| Sigilo | art. 9º | item fora da publicação pública | a política e os perfis reais ainda dependem de homologação institucional |

## Campos complementares

Responsável, e-mail, prioridade e identificação das áreas são campos de governança úteis. Eles também aparecem como referência no art. 8º do [Decreto federal nº 10.947/2022](https://www.planalto.gov.br/ccivil_03/_ato2019-2022/2022/decreto/d10947.htm). Esse decreto é tratado apenas como benchmark de desenho do DFD; ele não é declarado pelo projeto como norma automaticamente aplicável ao MPRJ.

Os campos de catálogo PNCP são opcionais no registro inicial da unidade e podem ser complementados durante a governança. A pré-validação indica objetivamente o que falta e nunca transmite dados.

## Documento anexo

O DFD pode ser anexado em PDF, DOC ou DOCX enquanto a integração com o SEI não estiver homologada. Limite atual: 8 MiB. O arquivo recebe identificador opaco, metadados e hash técnico interno. A aplicação não expõe caminho físico nem hash na interface de negócio.

## Limite jurídico

Esta matriz demonstra aderência técnica à resolução consultada. A aprovação do formulário, das competências, da temporalidade, das hipóteses de sigilo e de normas complementares cabe às autoridades e áreas competentes do MPRJ.
