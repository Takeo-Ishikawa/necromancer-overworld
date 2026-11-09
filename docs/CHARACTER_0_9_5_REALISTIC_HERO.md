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

Registrar somente após executar e inspecionar o workflow e imagens reais.
