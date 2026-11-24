# Necromancer Overworld — 0.9.14 | Forro da amarração e estudo 3D de moldes

## Objetivo

Evoluir a 0.9.13 em duas frentes, sem deformar a anatomia original e sem modificar o jogo no Unity:

1. Criar uma **língua de couro interna** de proteção, atrás dos cadarços posteriores de cada braçadeira, para evitar que a pele apareça diretamente na abertura.
2. Evoluir os cinco moldes **planos** da calça para cinco protótipos de **superfície curva 3D**, estudando folga, painéis dianteiros/traseiros e cós, sem vestir nem substituir a calça validada.

## Implementação

- Importação do estágio 0.9.13 com `NECROMANCER_0913_BUILD_ONLY=1`; evita exportações e renders redundantes. A cena base mantém os seis painéis de couro e os 16 cadarços cruzados.
- **Dois forros de couro editáveis**, um por braço: malhas fechadas lateralmente por quads, 22 anéis, 9 pontos transversais, 198 vértices, 168 quads e UV própria. A geometria é uma faixa ligeiramente mais larga que a abertura, recuada **3 mm** na direção do centro das seções, com espessura e cores de couro discretas. Os modelos anteriores continuam arquivados.
- **Quatro protótipos de painéis de calça em 3D** com 27 seções de altura × 12 pontos transversais, materiais dianteiro/traseiro e UV por painel. Os cortes e as curvas são guiados por faixas da superfície real da calça existente. Há ainda um quinto objeto de cós curvo.
- Estes **cinco objetos novos não são costurados nem vestíveis**, ficam ocultos na coleção de estudos e não entram no FBX do personagem. O script gera uma imagem separada mostrando somente os moldes tridimensionais, com enquadramento afastado do protagonista.
- A **calça que aparece no personagem permanece a versão contínua v0.9.12** (1.122 vértices, 1.086 faces e cinco shape keys); nada é sobreposto na cintura ou nas pernas.
- A anatomia base `Body Male – Realistic` do Blender Studio CC0 v1.4.1 e ambos os olhos permanecem intocados, controlados por hashes de todos os vértices. Não se altera `unity/`, rig, animações ou protagonista jogável.

## Revisão exigida

O workflow da 0.9.14 verifica a topologia, os quads independentes, a profundidade da faixa interna, a separação dos moldes, o número de PNGs e a integridade da fonte anatômica. Um teste automatizado não equivale à aprovação visual. Examinar particularmente a abertura posterior das braçadeiras e o aspecto dos cinco moldes 3D — que ainda são apenas protótipos de construção.

## Resultado

Pendente de execução e avaliação real. PR #2 deve permanecer em rascunho, sem merge.
