# Necromancer Overworld 0.5 — combate automático inicial

## Implementação

A versão 0.5 adiciona os componentes reutilizáveis `OverworldHealth`, `OverworldAutoCombat` e `OverworldCombatLifecycle`. A protagonista possui 100 pontos de vida, ataque corpo a corpo automático sem consumo de anima, alcance de 2,3 unidades e dano de 20 por golpe. Os três Grave Pups possuem 45 pontos de vida, causam 6 de dano por golpe e perseguem a protagonista dentro da primeira sala.

O ataque é disparado automaticamente quando um alvo hostil está no alcance, sem botão adicional. A busca de alvos utiliza componentes de saúde e facção (`isPlayer`), evitando dano entre Grave Pups.

Ao chegar a zero de vida, o Grave Pup desaparece temporariamente e reaparece em sua posição original após 10 segundos. A protagonista retorna à câmara segura após 2 segundos. Os inimigos não perseguem o jogador além da primeira sala, preservando a câmara como refúgio.

## Escopo e limitações

Esta é a **primeira implementação funcional**, ainda sem efeitos de golpe, HUD de vida, cadáveres reanimáveis, invocações ou sistema de anima. A lógica de perseguição e ataque é simples, adequada apenas ao protótipo; a detecção de alvos ainda não foi otimizada para muitos inimigos. A personagem não possui animação de ataque.

## Testes recomendados

1. Compilar Windows e Android pelo GitHub Actions.
2. Entrar na primeira sala e aproximar-se de um Grave Pup: ele deve perseguir e atacar.
3. Permanecer perto dele e verificar a troca de dano e o desaparecimento ao morrer.
4. Esperar 10 segundos e verificar o reaparecimento do Grave Pup.
5. Retornar à câmara e verificar que os inimigos não seguem o jogador.
6. Se a protagonista morrer, verificar retorno à posição inicial após 2 segundos.

**Status:** código enviado ao repositório; compilação e testes em dispositivo ainda não confirmados.
