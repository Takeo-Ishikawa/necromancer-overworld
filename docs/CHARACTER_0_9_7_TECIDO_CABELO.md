# Necromancer Overworld — 0.9.7 | Estudo de alfaiataria e cabelo superior

## Escopo da implementação

A versão 0.9.7 continua sobre a base masculina adulta `Body Male – Realistic` do Blender Studio Human Base Meshes v1.4.1, com licença CC0. O arquivo `tools/blender/realistic_hero_096/assemble_realistic_hero_096.py` agora expõe um modo de construção sem exportação `NECROMANCER_096_BUILD_ONLY=1`, para que `tools/blender/realistic_hero_097/assemble_realistic_hero_097.py` possa reutilizar os objetos finais da 0.9.6 sem duplicar processamento.

A anatomia do personagem e os dois olhos foram integralmente preservados: **10.582 vértices, 10.590 faces** no corpo e mesmo SHA-256 de todas as coordenadas do corpo antes/depois: `38989292ed2dd123c31b8135f2adc18c3202399de1683b74f8bd8cddf9d85e4d`. O workflow também valida os hashes dos dois olhos. Nenhuma alteração em `unity/`, sem rigging ou animações.

## Trabalho de tecido: experimento e decisão

Foram criadas, efetivamente, duas malhas independentes de pernas de calças, cada uma com **864 quads, 28 anéis e 32 vértices por anel**. A parte superior do tecido foi extraída dos polígonos originais da roupa (300 faces), com duas bainhas e costuras. O experimento completo está preservado como objetos editáveis no arquivo Blender.

A inspeção dos renders mostrou que a primeira versão formava uma **bermuda sobre leggings** por causa da emenda entre quadril e pernas. Criar superfícies de transição (96 quads) agravou o problema, introduzindo faixas/placas ao redor das coxas.

**Decisão técnica e artística:** não usar a nova alfaiataria como roupa visível ou exportá-la ao FBX. Manter esses componentes **ocultos no .blend para estudo e revisão**, com `hide_render=True`, e mostrar/exportar a calça contínua de 1.086 quads da 0.9.6 com novo material de tecido escuro com microtextura. Isso evita regredir a estética. A modelagem de alfaiataria realmente contínua ainda não está resolvida e não deve ser declarada entregue como definitiva.

## Trabalho no cabelo: mudança efetivamente visível

Foram preservados os **1.760 fios curtos** guiados sobre a superfície anatômica do couro cabeludo da 0.9.6.

A primeira proposta da 0.9.7 acrescentou 265 fios superiores, porém o render do rosto mostrou brilho excessivo e aparência de peruca. Reduzimos o volume, a espessura e o contraste para **180 novos fios suavemente orientados** (120 na coroa e 60 na franja), separados em dois objetos editáveis. As pontas são reaproximadas da superfície por projeção na malha do couro cabeludo.

O resultado final é uma mudança moderada na textura/silhueta do cabelo, e não um groom de qualidade final. A referência aprovada segue ausente do repositório.

## GitHub Actions e inspeção real

Workflow: `.github/workflows/realistic-character-preview-097.yml`, Blender 4.5.15 LTS.

| Execução | Resultado técnico | Parecer visual |
|---|---|---|
| [42562386387](https://github.com/Takeo-Ishikawa/necromancer-overworld/actions/runs/42562386387) | Sucesso | **Reprovado:** descontinuidade entre shorts/pelve e pernas |
| [42562858534](https://github.com/Takeo-Ishikawa/necromancer-overworld/actions/runs/42562858534) | Sucesso | **Reprovado:** bandas rígidas na transição da coxa |
| [42563255376](https://github.com/Takeo-Ishikawa/necromancer-overworld/actions/runs/42563255376) | Sucesso | Calça contínua restaurada; cabelo ainda brilhante/irregular |
| [42563591608](https://github.com/Takeo-Ishikawa/necromancer-overworld/actions/runs/42563591608) | **Sucesso** | Renders finais inspecionados: roupa sem emendas artificiais, cabelo moderadamente refinado |

O artefato da execução final, `necromancer-realistic-0-9-7-independent-tailoring`, ID **13650716173**, contém `necromancer_realistic_097.blend`, `necromancer_realistic_097.fbx`, JSON de procedência e oito renders PNG: frente, lado, costas, três-quartos, rosto frontal, rosto três-quartos, nuca e detalhe das calças.

### O que foi efetivamente aprovado na inspeção

- Importação e integridade da malha adulta realista, sem deformações inadvertidas;
- Geração de .blend, FBX e oito renders reais;
- Restauração da roupa contínua, evitando as bandas/placas das tentativas anteriores;
- Novos fios superiores em densidade mais discreta, sem pontas rígidas proeminentes.

### Pendências artísticas e próximos passos

**O personagem como um todo não está aprovado artisticamente.** As calças ainda reproduzem a anatomia e não têm caimento de alfaiataria de produção. A região pélvica é excessivamente marcada. O cabelo tem padrão procedural muito uniforme e ainda precisa de referência visual e groom artístico dedicado. Braçadeiras e bolsas permanecem rudimentares e não foram remodeladas nesta etapa.

Para a próxima versão, priorizar **uma única superfície de tecido contínua**, com topologia costurada entre pelvis e pernas, sem sobreposições separadas ou bordas sobrepostas; estudar desenho UV, posicionamento de costuras e tratamentos de folga antes de tentar novamente o loft. Refinar adicionalmente o cabelo em volumes coerentes com a referência conceitual. Não alterar o rosto original nem integrar ao Unity antes de aprovação explícita.

O PR deve permanecer em **rascunho**.
