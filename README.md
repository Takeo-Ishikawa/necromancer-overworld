# Necromancer Overworld — protótipo 2.5D

Experimento independente do jogo **Necromancer: Rise of the Fallen**. Nenhum arquivo do projeto 2D é modificado.

## Protótipo 0.1

- Unity **2022.3.62f2 LTS**, projeto na pasta `unity/`.
- Câmara subterrânea 3D modular, câmera ortográfica inclinada e protagonista provisória.
- Movimento no plano XZ com teclado (WASD/setas) e joystick virtual para Android.
- Cena experimental construída pelo script de Editor `OverworldSceneBuilder`.
- Assets geométricos provisórios para avaliar perspectiva, colisões, navegação e desempenho antes de criar arte definitiva.

## Abrir e executar

1. Abra a pasta `unity/` no Unity Hub, usando Unity 2022.3.62f2.
2. Aguarde a importação. No menu **Necromancer > Build Prototype Scene**, gere a cena.
3. Abra `Assets/Scenes/OverworldPrototype.unity` e pressione Play.
4. No Android, selecione a plataforma Android em Build Settings e gere um APK de desenvolvimento.

O projeto foi criado como protótipo de baixo risco; **ainda não houve compilação Unity nem teste em aparelho**. O APK automatizado e a assinatura persistente serão configurados em etapa posterior.

## Próximos passos

Validar escala, controle, colisões e legibilidade. Depois introduzir modelos 3D próprios, decoração, fonte, altar e um Grave Pup experimental.
