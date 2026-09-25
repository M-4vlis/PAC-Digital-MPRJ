# Integração com o SEI — análise e preparação

## Conclusão

O SEI possui integração oficial para sistemas externos por Web Services descritos em WSDL. O administrador cadastra o sistema consumidor, cria um serviço e libera operações, unidades, tipos de processo e tipos de documento. A autenticação pode utilizar chave de acesso ou restrição por endereço/IP.

Fontes oficiais:

- Administração de sistemas externos e serviços: https://manuais.processoeletronico.gov.br/pt-br/latest/SEIADM/Administracao_sei/Man_Adm_SEI_04-Administra%C3%A7%C3%A3o_SEI-11_Sistemas.html
- Documentação técnica SEI/PEN: https://wiki.processoeletronico.gov.br/pt-br/latest/Sistema_Eletronico_de_Informa%C3%A7%C3%A3o_SEI/Documentacao_de_Apoio.html
- Exemplo oficial de integração com SPE/SEI: https://manuais.processoeletronico.gov.br/pt-br/latest/PROTOCOLO.GOV.BR/MANUAL_TECNICO_OPERACIONAL/CONFIGURACAO_DA_INTEGRACAO_NO_PROTOCOLO.html
- Portal SEI do MPRJ: https://portalsei.mprj.mp.br/

## Situação específica do MPRJ

O portal institucional confirma o uso do SEI pelo MPRJ e registra a adoção da versão 4.0. Não foi localizada documentação pública do WSDL da instância nem uma autorização pública para consumo por sistemas externos. Isso é esperado: o acesso deve ser tratado com a STIC e com a administração do SEI-MPRJ.

## Dados necessários para homologação

1. URL interna do WSDL da instância MPRJ e versão exata do SEI.
2. Cadastro do `PAC Digital MPRJ` em **Administração > Sistemas**.
3. Identificação do serviço e chave de acesso, ou liberação do IP do servidor.
4. Operações autorizadas: no mínimo consultar/gerar procedimento e incluir documento.
5. Unidades, tipos de processo e tipos de documento permitidos.
6. Ambiente de homologação, regras de sigilo, limites e política de auditoria.

## Estratégia adotada

O PAC Digital possui um adaptador desacoplado. Na v0.7 ele somente:

- vincula manualmente uma demanda a um número de processo;
- informa se WSDL e segredo foram configurados;
- prepara o plano de operação;
- mantém `will_transmit = false`.

Nenhum segredo é armazenado no banco ou no repositório. A chamada SOAP real só deverá ser habilitada após homologação institucional.
