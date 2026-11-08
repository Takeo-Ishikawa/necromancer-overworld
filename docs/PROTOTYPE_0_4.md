# Necromancer Overworld 0.4 — primeira sala e Grave Pups

## Entregue

O corredor da versão 0.3 agora se abre para uma sala de caverna de 22 × 22 unidades, delimitada por paredes e com acesso livre pela entrada central. A barreira provisória do corredor foi removida.

Três **Grave Pups** provisórios ocupam a sala. Cada um é formado por peças 3D separadas (corpo, cabeça, orelhas, olhos e patas) agrupadas em um GameObject próprio. O script `GravePupPatrol` faz cada criatura caminhar em uma área limitada ao redor de seu ponto inicial, com pausas entre deslocamentos.

A geometria da sala está no grupo `04 - First cave room (modular)`. O cenário e os Grave Pups permanecem editáveis separadamente.

## Limites desta versão

Os Grave Pups ainda são criaturas **não hostis**: não causam dano, não perseguem o jogador e não podem ser derrotados ou reanimados. A intenção desta etapa é validar escala, circulação, aparência e animação simples de deslocamento antes do sistema de combate.

## Testes para Windows e Android

1. Sair da câmara, percorrer o corredor e entrar na nova sala.
2. Verificar que não há barreira invisível na junção do corredor com a sala.
3. Observar os três Grave Pups patrulhando sem atravessar as paredes.
4. Retornar à câmara e avaliar se o enquadramento da câmera permanece legível.
5. Verificar desempenho em Android e Windows.

## Próxima etapa

Implementar vida, detecção de alvos e combate automático básico. Em seguida, adicionar cadáveres reanimáveis e invocações persistentes, mantendo as mecânicas alinhadas ao projeto 2D.

**Status:** código enviado ao GitHub; compilação e teste da versão 0.4 ainda não confirmados.
