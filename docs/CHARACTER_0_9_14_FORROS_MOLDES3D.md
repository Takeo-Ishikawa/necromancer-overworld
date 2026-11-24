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

### Execuções reais

- [GitHub Actions 45487187569](https://github.com/Takeo-Ishikawa/necromancer-overworld/actions/runs/45487187569): **sucesso técnico**, mas a vista dos moldes 3D mostrava as pontas dos painéis extremos cortadas por uma câmera estreita; a modelagem estava íntegra.
- A câmera exclusiva do protótipo de calça foi ampliada de escala ortográfica **1,36 para 1,95**, deslocando o centro horizontal para manter todos os cinco objetos visíveis.
- [GitHub Actions 45487895687](https://github.com/Takeo-Ishikawa/necromancer-overworld/actions/runs/45487895687): **sucesso técnico** e inspeção visual final. Artefato: `necromancer-realistic-0-9-14-leather-linings-and-patterns` ID **14963744000**, com `necromancer_realistic_0914.blend`, `necromancer_realistic_0914.fbx`, `source_metadata.json` e **nove PNGs**, sendo oito vistas do personagem e uma vista exclusiva dos moldes.
- Integridade da anatomia: **10.582 vértices, 10.590 faces**, hash SHA-256 do corpo antes/depois `38989292ed2dd123c31b8135f2adc18c3202399de1683b74f8bd8cddf9d85e4d`; dois olhos preservados.
- As duas linguetas internas reais possuem **198 vértices, 168 faces quad e 1 UV** cada. O recuo médio é **0,003 m (3 mm)**. A largura máxima da abertura original medida entre as bordas é de apenas **0,00698 m (6,98 mm)** — a preocupação estética era a pele exposta, não uma grande abertura dimensional.
- Os seis painéis externos e os 16 cadarços da versão 0.9.13 permanecem visíveis. A imagem posterior confirma a cobertura discreta por trás dos cadarços, sem placa saliente.
- A nova maquete de calça inclui **quatro superfícies curvas independentes, cada uma com 286 faces quadriláteras**, mais um cós curvo não unido às pernas. Todos os cinco objetos são ocultos no `.blend` padrão, não são exportados em FBX e são mostrados só na imagem de estudo.
- A calça vestida permanece **uma única malha conectada de 1.122 vértices e 1.086 faces**, com os mesmos cinco shape keys. Sem rigging, animações ou integração no Unity.

### Avaliação artística honesta

**Aprovado como estudo geométrico e de apresentação, não como figurino definitivo.** O forro escurece e fecha visualmente a abertura, conservando a amarração em X. As braçadeiras continuam relativamente rígidas e precisarão de textura menos uniforme e estudo mais cuidadoso de punhos anatômicos.

Os cinco moldes agora têm curvatura 3D, mas o preview evidencia que **ainda se parecem com quatro faixas de tecido e um cós avulso**, não com uma calça costurada; não há união de painéis no cavalo, costuras físicas, nem caimento simulado. A calça atual continua marcada na pelve. A próxima etapa deve modelar o **cavalo e a união real entre painéis**, sem exibir tubos desconectados como se fossem roupa final.

**Nada alterado no diretório `unity/`.** O PR #2 continua em rascunho e sem merge.
