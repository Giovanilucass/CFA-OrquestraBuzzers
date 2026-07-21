# 7. Desenvolvimento e histórico do projeto

Orientações para desenvolvimento contínuo e registro de progresso.

## Fluxo de trabalho sugerido

- Branching: `main` para releases, `feature/*` para mudanças.
- Commits: mensagens claras; cada PR deve referenciar uma issue.

## Registro de progresso

- Utilizar `CHANGELOG.md` para registrar versões e mudanças importantes.
- Manter notas de investigação e decisões em `docs/` quando relevantes.

## Testes e verificação

- Executar testes unitários com `python -m unittest` no diretório raiz.
- Ao modificar `orquestra/*`, testar em um dispositivo real ou em simulação.

## Desenvolvimento de novos dispositivos

- Seguir o template de documentação (Seções 1–7) para cada novo nó/projeto.
