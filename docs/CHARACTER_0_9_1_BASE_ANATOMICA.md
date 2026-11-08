# Necromancer — base anatômica real 0.9.1 (Blender Studio CC0)

## Origem e licença

- **Pacote:** Blender Studio Human Base Meshes v1.4.1
- **Fonte oficial:** https://www.blender.org/download/demo-files/
- **Download automatizado:** https://mirror.blender.org/demo/asset-bundles/human-base-meshes/human-base-meshes-bundle-v1.4.1.zip
- **Licença do pacote:** CC0-1.0, inclusive uso comercial, conforme página oficial.
- **Biblioteca carregada:** `human-base-meshes-bundle-v1.4.1/human_base_meshes_bundle.blend`
- **Datablock escolhido:** coleção `Body Male - Stylized` — NÃO a alternativa Primitive/Primitve.
- **Blender:** 4.5.15 LTS executado em GitHub Actions; sem instalação local.
- **Arquivo de código:** `tools/blender/anatomical/import_sculpt_091.py`
- **Workflow independente:** `.github/workflows/anatomical-character-preview.yml`.

O pacote externo é baixado em cada execução. Não é guardado no Git nem inclui modelos de procedência incerta. O workflow guarda em cache somente a instalação do Blender 4.5 LTS. O gerador antigo `character-model-preview.yml` permanece disponível e isolado para comparação/retorno seguro.

## Entrega verificada

GitHub Actions: execução [42523839634](https://github.com/Takeo-Ishikawa/necromancer-overworld/actions/runs/42523839634). O workflow importou, inspecionou, adaptou para 1,90 m, exportou .blend/.fbx e renderizou quatro vistas ortográficas genuínas em fundo de estúdio. O pacote `necromancer-anatomical-0-9-1-cc0-preview` inclui:

- `necromancer_anatomy_091.blend` — base anatômica com malha original preservada em coleção oculta e primeiro passe de escultura sobre malha copiada;
- `necromancer_anatomy_091.fbx` — modelo-base de verdade, sem voxel/remesh das versões antigas;
- `anatomy_front.png`, `anatomy_side.png`, `anatomy_back.png`, `anatomy_threequarter.png`;
- `source_metadata.json` e `asset_catalog.json` — rastreabilidade da licença, nome real do asset, parâmetros e inventário da biblioteca.

Malha corporal selecionada: **12.502 vértices / 12.500 faces**, altura de **1,90 m**. Uma subdivisão de prévia não destrutiva adiciona definição ao render, preservando o controle sobre os quads originais. O primeiro passe esculpe suavemente peitoral, abdômen e oblíquos via deslocamento dos vértices reais. A malha é uma base anatômica melhor para escultura, mas o passe realizado **não equivale a uma escultura artística de alta fidelidade**.

## Próximas etapas de produção

1. Reproporcionalizar a silhueta usando a folha de referência aprovada (ombros, cintura, pernas, rosto), sem perder o fluxo de topologia.
2. Esculpir feições, peito, costas e músculos com malha e níveis de subdivisão verdadeiros; avaliar frontal e perfil.
3. Criar cabelo curto grisalho/lilás e calças escuras bordadas como malhas próprias, adaptadas à base anatômica; incluir bolsas, braçadeiras e pés descalços.
4. Aprovar vista frontal/lateral/traseira, e só então estudar retopologia de deformação, materiais PBR, rigging, animações e LOD/mobile.
5. Substituir a cápsula provisória no Unity **apenas depois** da aprovação artística e técnica.

**Não confundir:** sucesso no GitHub Actions significa que os arquivos foram gerados; não significa aprovação da aparência, disponibilidade de animações nem integração ao jogo. O protagonista atual da cena Unity permanece intacto.
