# Necromancer Overworld — 0.9.5 Realistic Hero

## Decisão após os renders reais

A comparação oficial da base masculina do Blender Studio (workflow [42551358033](https://github.com/Takeo-Ishikawa/necromancer-overworld/actions/runs/42551358033)) confirmou que **Body Male – Realistic** tem feições adultas muito mais adequadas ao protagonista do que a malha **Body Male – Stylized** usada de 0.9.1 até 0.9.4.

**Medidas verificadas:** base estilizada 12.502 vértices / 12.500 faces; realista 10.582 vértices / 10.590 faces. A topologia e as ordens dos loops são diferentes, logo um morph direto da cabeça anterior não seria válido.

Por isso, a nova versão deixa de empilhar deformações agressivas no rosto estilizado. A malha realista original permanece intacta.

## Implementação do herói realista

- Script: `tools/blender/realistic_hero_095/assemble_realistic_hero_095.py`
- Workflow independente: `.github/workflows/realistic-character-preview-095.yml`
- Fonte: Blender Studio Human Base Meshes v1.4.1, **CC0**.
- Corpo adulto realista **sem alterações da topologia anatômica**.
- Calças e proteções nos antebraços extraídas de faces reais da malha importada e salvas como objetos próprios e editáveis.
- Cabelo cinza/lilás em camadas ancorado na superfície do crânio com underlay separado.
- Cinto, fivela, bolsas e detalhes de couro/metal separados.
- Peitoral e abdômen expostos; pés descalços.
- Íris e pupilas posicionadas sobre os dois olhos do asset original.
- Arquivos `.blend`, `.fbx`, seis renders e metadados de procedência exportados pelo GitHub Actions.

## Critérios de aprovação

Uma execução de CI bem-sucedida **não** garante fidelidade artística. Examinar os seis renders reais para detectar defeitos de roupas, cabelo, olhos, colisões de geometria e perspectiva; preservar o modelo jogável do Unity enquanto o rosto/cabelo não forem aprovados.

O rosto adulto realista tem identidade anatômica melhor, mas não pode ser declarado fiel à folha de referência anterior sem o arquivo visual original, que não foi versionado no repositório.

## Verificação

### Resultado final verificado

- [42552256078](https://github.com/Takeo-Ishikawa/necromancer-overworld/actions/runs/42552256078): primeiro personagem completo 0.9.5 gerado e validado; cabelo em mechas muito brilhantes, olhos artificiais, calças volumosas.
- [42552594345](https://github.com/Takeo-Ishikawa/necromancer-overworld/actions/runs/42552594345): segunda prévia bem-sucedida após diminuir íris e reduzir mechas, com melhor leitura do rosto. O render traseiro revelou insuficiência capilar na nuca.
- [42552953434](https://github.com/Takeo-Ishikawa/necromancer-overworld/actions/runs/42552953434): teste técnico bem-sucedido, mas **reprovado visualmente**, pois uma coordenada da seleção de mechas colocou cabelo sobre costas e tronco.
- [42553194669](https://github.com/Takeo-Ishikawa/necromancer-overworld/actions/runs/42553194669): execução final **bem-sucedida, com seis PNGs inspecionados**. Correção da origem dos fios da nuca removeu completamente as mechas espúrias no tronco.
- Artefato final: `necromancer-realistic-hero-0-9-5-cc0-preview`, ID **13646292679**, ZIP ~46,8 MB, contendo `.blend`, `.fbx`, seis vistas e metadados.
- Metadados: corpo realista original **10.582 vértices / 10.590 faces**, sem alterações; calças 1.086 faces da malha herdada; braçadeiras 860 faces combinadas; scalp 346 faces; **340 mechas / 2.040 quads de cabelo**, olhos CC0 preservados.
- `unity/` não modificado, sem rigging ou animações.

### Parecer artístico

**A anatomia do rosto adulto melhorou de maneira clara em relação à 0.9.4**, sem deformar os traços da malha CC0. O corpo tem proporções mais coerentes, peitoral/abdômen descobertos e pés descalços. A cobertura posterior do cabelo está corrigida.

**Não aprovado artisticamente:** cabelo ainda se parece com placas sobrepostas e carece de um groom ou escultura orientada por referência; calças são muito volumosas, com pregas e costuras incompletas; braçadeiras e bolsas são peças provisórias. A aparência atual tampouco garante fidelidade à folha conceitual original, ausente do repositório.

**Direção recomendada para a 0.9.6:** congelar anatomia facial realista, redesenhar cabelo como volumes coerentes com mechas agrupadas e criar calças com caimento de alfaiataria sobre a mesma topologia de origem. Evitar novo acúmulo de deformações faciais ou retorno ao gerador primitivo. Manter o PR em rascunho e o personagem jogável do Unity preservado.
