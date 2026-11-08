# Necromancer Overworld 0.2 — polimento estrutural da câmara

## Implementado

O gerador de cena 0.1 continua sendo o ponto de entrada. A etapa `OverworldVisualPass.Apply()` acrescenta objetos editáveis separados e agrupados na Hierarchy:

- Lajes individuais no piso, sem colliders adicionais, para testar leitura de profundidade.
- Colunas com base e capitel nas bordas da câmara.
- Quatro braseiros arcanos com luzes locais sem sombras dinâmicas.
- Portas e puxadores do guarda-roupa, travesseiro, foco do altar e cristal da fonte.
- Silhueta provisória da protagonista (capuz, ombreiras, rosto e cajado).

A geometria é provisória e intencionalmente simples. Não substitui modelos e texturas finais.

## Teste

O APK é gerado pelo mesmo workflow `android-preview.yml`. Não há alterações nos secrets de Unity ou assinatura. A cena é recriada automaticamente durante cada build, incluindo os novos detalhes.

Avaliar: visualização do chão, espaço livre, contraste da personagem, obstrução das colunas, movimentação e taxa de quadros. Se o personagem ficar oculto por objetos altos, a próxima etapa será tratar a oclusão da câmera.

## Próximo marco

- Substituir a cápsula da protagonista por um modelo de personagem estilizado.
- Melhorar materiais e cores do cenário com uma direção artística consistente.
- Implementar a transição entre câmara e primeiro corredor de caverna.
- Comparar desempenho e APK com a versão 0.1.

**Status:** alterações enviadas ao repositório; a versão 0.2 ainda não foi compilada nem testada em dispositivo real.
