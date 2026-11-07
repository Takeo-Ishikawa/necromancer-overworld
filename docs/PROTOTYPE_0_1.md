# Necromancer Overworld 0.1 — plano e critérios

## Escopo

Protótipo separado de Necromancer 2D. Câmara segura 24 x 20 unidades, paredes 3D, mobiliário provisório, personagem cápsula, câmera ortográfica inclinada e joystick móvel.

## Como testar

1. Abrir `unity/` no Unity 2022.3.62f2.
2. Executar **Necromancer > Build Prototype Scene** no menu do editor.
3. Abrir `Assets/Scenes/OverworldPrototype.unity`.
4. Pressionar Play. No computador, usar WASD/setas; no celular, joystick no canto inferior esquerdo.
5. Verificar deslocamento relativo à câmera, colisões, obstruções, escala e orientação.
6. Compilar APK de desenvolvimento e medir FPS, memória e tamanho em dispositivo real.

## Critérios de aprovação

- A câmera não esconde o personagem atrás das paredes durante a navegação.
- A protagonista não atravessa obstáculos.
- O joystick responde corretamente a toque e arrasto.
- A sala oferece espaço confortável de movimentação.
- A cena mantém pelo menos 30 FPS no Android de referência.
- O protótipo permanece independente da versão 2D.

## Limitações conhecidas

- Arte 3D provisória feita com primitivas, sem modelos definitivos.
- Ainda não há combate, necromancia, transição de bioma, salvamento ou interface final.
- Ainda não foi configurada URP; usa renderização padrão para reduzir risco na primeira abertura.
- A cena é gerada pelo Editor e não está versionada inicialmente.
- A compilação automática de APK e os secrets de assinatura/licença ainda não estão configurados.
- Código enviado ao GitHub, mas ainda não compilado ou executado no Unity.
