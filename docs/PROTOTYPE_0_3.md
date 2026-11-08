# Necromancer Overworld 0.3 — entrada da caverna

## Implementação

A câmara segura agora se conecta a um corredor de caverna 3D pela abertura central da parede sul (x entre -3 e +3, z=-10). O corredor se estende até z=-25, tem piso e paredes com colisão, arco de entrada, pedras e cristais com iluminação local.

O corredor é gerado por `OverworldCaveEntrance.Apply()`, invocado pelo `OverworldSceneBuilder.Build()`. Seus objetos estão organizados no grupo `03 - Cave entrance (modular)`, separados dos objetos da câmara e editáveis independentemente.

Há uma barreira provisória no final do corredor para impedir que o jogador caia fora da geometria. **Não há inimigos, transição de cena nem combate nesta etapa**; o objetivo é testar exploração, continuidade espacial e enquadramento da câmera.

## Validação sugerida

1. Abrir o APK 0.3 e mover o necromante em direção à abertura sul.
2. Verificar se o personagem atravessa a entrada sem travar nas colunas do arco.
3. Percorrer o corredor até a barreira e retornar à câmara.
4. Verificar se a câmera acompanha o personagem sem obstruções graves e se o desempenho é adequado.
5. Conferir se a iluminação dos cristais e braseiros não compromete a leitura do caminho.

## Próximo passo

Após o teste, preparar a primeira sala de combate e introduzir criaturas provisórias com IA simples. Antes disso, corrigir eventuais problemas de enquadramento e colisão reportados no celular.

**Status:** alterações no GitHub; compilação e teste da versão 0.3 ainda não confirmados.
