# Melhorias Futuras

Lista de melhorias e próximas tarefas planejadas para o projeto.

## Itens priorizados

- Separar as configurações de Wi‑Fi do tocador em um arquivo de configuração
  parametrizável (ex.: `config.json` ou `config.yaml`) para facilitar a
  reconfiguração sem editar o código-fonte.
- Fazer com que o publisher (maestro) crie sua própria fila/namespace UMQTT
  para que os clientes se conectem dinamicamente a um canal dedicado e
  simplificar descoberta/assinaturas.
- Adicionar mais músicas ao repertório (`podio/repertorio/`) com exemplos
  de partituras em JSON e testes automatizados para validação de formato.

## Observações

Essas melhorias podem ser implementadas em etapas curtas e documentadas em
PRs separados; cada PR deve incluir testes e instruções de migração quando
relevante.
