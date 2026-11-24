# Necromancer Overworld — 0.9.10 | Costuras até a bainha e acessórios

## Escopo

Esta etapa evolui o protótipo 0.9.9 exclusivamente em **modelagem dos acessórios e das costuras da roupa**. A base anatômica continua sendo o Blender Studio **Human Base Meshes v1.4.1, Body Male – Realistic**, licença CC0, 10.582 vértices e 10.590 faces. O rosto, o corpo e os dois olhos oficiais não são deformados.

### Implementação

- Reutilização do estágio 0.9.9 com `NECROMANCER_099_BUILD_ONLY=1`, sem render/export redundante.
- Costuras antigas 0.9.9 ocultas. Duas curvas Bézier novas são calculadas por faixas reais da **superfície avaliada** da calça conectada, suavizadas e novamente projetadas à malha, com controle explícito da distância até a bainha. Acessíveis como curvas editáveis no `.blend`.
- Bolsas retangulares anteriores arquivadas e ocultas; novas bolsas com malhas de contorno arredondado, aba separada, fechos de bronze discreto, costura periférica e tirante próprio para fixação ao cinto.
- Material das duas braçadeiras revisado para couro preto-acinzentado com relevo discreto e linhas de costura projetadas à superfície real da proteção, sem alterações na malha original do braço.
- Novo conjunto de objetos agrupado em coleção editável `0910 | refined leather gear and garment seams`; rosto e pé descalço permanecem inalterados.
- Sem modificações em `unity/`, sem rigging, animações, nem troca do protagonista jogável.

### Verificações de integridade

A verificação automática valida: hashes coordenados antes/depois do corpo e olhos, calça conectada com 1.122 vértices / 1.086 quads, duas costuras com pontas a menos de 2,6 cm da borda inferior, duas novas bolsas arredondadas e proteções no antebraço. O sucesso técnico não substitui análise visual.

### Execuções

Pendente de resultado dos oito PNGs reais. O PR permanece em rascunho, sem merge.
