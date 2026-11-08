# NECROMANCER OVERWORLD — ESTADO DO PROJETO E PRÓXIMOS PASSOS

Atualizado em 2026-11-07. Documento central de continuidade para próximas sessões.

## Objetivo e separação de projetos

Criar um protótipo Unity 3D com câmera ortográfica inclinada (2.5D), preservando integralmente o jogo 2D original em outro repositório. Este repositório é `Takeo-Ishikawa/necromancer-overworld`. O foco é testar exploração, combate automático, reanimação e servos antes de investir em modelos 3D definitivos.

## Implementações até a versão 0.7

- **0.1:** estrutura Unity 2022.3.62f2, geração de cena por editor, câmara segura, controle de personagem por teclado/joystick, câmera ortográfica inclinada e compilação Android.
- **0.2:** polimento geométrico modular: lajes, colunas, braseiros, detalhes da câmara e silhueta provisória do protagonista.
- **0.3:** corredor de caverna conectado à saída sul da câmara.
- **0.4:** primeira sala de caverna, três Grave Pups provisórios e patrulhamento.
- **0.5:** vida, ataques automáticos sem gasto de anima, perseguição inimiga, morte e respawn. O jogador reaparece no santuário e os inimigos reaparecem após 10 segundos.
- **0.6:** inimigos derrotados deixam restos reanimáveis por 20 segundos; o necromante inicia com 100 de anima, gasta 25 por reanimação, tem alcance de interação de 3,5 unidades e limite inicial de cinco servos. Reanimar com **E/R** no Windows ou com o botão **REANIMAR** na interface (também disponível no Android). Servos são aliados persistentes até morrerem, acompanham o jogador e atacam automaticamente inimigos próximos. HUD provisório exibe vida, anima e número de servos.

- **0.7 (atual, terceira entrega):** barras de vida, números flutuantes de dano, desvio local de obstáculos para servos e HUD Unity Canvas com vida, anima, servos e botão REANIMAR. Falta validar compilações e comportamento em dispositivos.

## Mecânicas atuais e restrições

- O ataque automático não consome anima. A anima é usada somente para reanimar.
- Grave Pups hostis e servos usam a mesma infraestrutura de vida e combate, com facções diferenciadas.
- Servos não são salvos entre sessões; persistem somente durante a partida.
- A anima **não regenera** nesta versão: é um recurso de teste com valor inicial de 100. A economia definitiva e as fontes de anima ainda precisam ser projetadas.
- Os cadáveres são representações temporárias simplificadas, não modelos artísticos finais.
- Os servos utilizam cápsulas coloridas provisórias, não o modelo completo do Grave Pup.
- A IA ainda é simples, sem NavMesh. A versão 0.7 tenta desviar de obstáculos por sondagem lateral e SphereCast, mas não calcula caminhos globais; pode ficar presa em corredores complexos.
- O HUD de atributos e o botão de reanimação agora usam Unity Canvas/uGUI com CanvasScaler. Barras de vida e números de dano ainda usam OnGUI sobreposto à cena, provisoriamente.
- O comportamento e balanceamento ainda não foram validados em dispositivo. Não considerar a versão 0.7 aprovada antes dos testes.

## Correção de compilação (2026-11-07)

A execução Windows [42438140243](https://github.com/Takeo-Ishikawa/necromancer-overworld/actions/runs/42438140243) falhou durante a geração da cena com `ArgumentException: Arial.ttf is no longer a valid built in font. Please use LegacyRuntime.ttf`. A causa era `Resources.GetBuiltinResource<Font>("Arial.ttf")` em `OverworldSceneBuilder.HudText()`, introduzida na migração para Canvas. A referência foi alterada para `LegacyRuntime.ttf`. **A correção foi enviada; aguarda nova compilação para validação.**

## Como compilar

Workflows GitHub Actions:
- `.github/workflows/android-preview.yml`: gera APK Android.
- `.github/workflows/windows-preview.yml`: gera artefato ZIP com EXE e pasta Data para Windows x64.

Ambos geram a cena usando `OverworldSceneBuilder.Build()`. Os secrets de licença Unity são compartilhados. O código foi enviado ao GitHub; verificar as execuções antes de declarar compilação bem-sucedida.

## Testes de aceitação 0.7

1. Abrir o jogo em Windows e Android; confirmar que a câmara e o corredor continuam funcionais.
2. Entrar na sala, aproximar-se de um Grave Pup e verificar o combate automático.
3. Após derrotá-lo, verificar a presença dos restos por até 20 segundos.
4. Aproximar-se a menos de 3,5 unidades e pressionar E/R ou REANIMAR.
5. Confirmar gasto de 25 de anima, aparecimento de um servo e atualização do HUD.
6. Verificar que o servo acompanha o jogador e ataca outros Grave Pups.
7. Confirmar que os inimigos reaparecem e que o número de servos respeita o limite.
8. Confirmar que não há consumo de anima por ataques automáticos.
9. Verificar posicionamento e tamanho do botão no Android, especialmente em telas menores.
10. Verificar barras de vida verdes para protagonista/servos e vermelhas para Grave Pups, atualizadas ao receber dano.
11. Testar se os servos deixam de atravessar paredes, observando que ainda não conseguem desviar de obstáculos.
12. Confirmar que cada ataque exibe o dano efetivamente causado e que o número desaparece em menos de um segundo.
13. Conferir o tamanho do botão REANIMAR em diferentes resoluções e orientações.
14. Verificar que o novo HUD Canvas mostra vida, anima e servos e que REANIMAR funciona por toque e mouse sem interferir no joystick.
15. Verificar se os servos contornam pequenos obstáculos e se ficam presos em cantos fechados.
16. Observar eventuais travamentos, ataques à distância indevidos e queda de desempenho.

## Próximos passos priorizados

**0.7 — estabilidade e feedback de combate (em validação)**
- Feito: barras de vida, números de dano, desvio local de obstáculos e HUD de atributos/botão de reanimação com Unity Canvas.
- Pendente: validar builds Windows/Android e responsividade em diferentes telas, corrigir problemas reportados e adicionar efeitos de impacto.
- Pendente: aprimorar navegação global dos servos e seleção de alvos; migrar barras de vida/números flutuantes de OnGUI para Canvas se necessário.

**0.8 — sistema de necromancia aprofundado**
- Transformar cadáveres e servos em versões visuais consistentes dos Grave Pups.
- Definir fontes e regeneração de anima, custo por espécie, limite de servos e balanceamento.
- Introduzir dispensa de servos e gerenciamento do exército.

**0.9 — direção artística e animação**
- Substituir cápsula do necromante por modelo estilizado e criar animações básicas de locomoção/ataque.
- Consolidar materiais, iluminação e silhuetas das criaturas.
- Revisar câmera, oclusão, colisões e desempenho mobile.

**1.0 — ciclo jogável mínimo**
- Integrar uma segunda espécie de inimigo, inicialmente Rotboar.
- Validar loop: explorar → derrotar → reanimar → ampliar exército → enfrentar inimigos mais fortes.
- Preparar testes de jogabilidade e estabilidade em Windows e Android.

## Princípios de continuidade

1. Manter o repositório 2D original intacto.
2. Preservar cenário e personagens como elementos modulares editáveis.
3. Priorizar o ciclo jogável antes de investir em arte final.
4. Documentar entregas e pendências neste arquivo após cada marco.
5. Distinguir sempre **código enviado**, **compilação concluída** e **teste em dispositivo aprovado**.
