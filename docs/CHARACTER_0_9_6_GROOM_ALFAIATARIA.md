# Necromancer Overworld — 0.9.6 | Groom de fibras e calças ajustadas

## Decisão de continuidade

A base **Body Male – Realistic** do Blender Studio Human Base Meshes v1.4.1 (CC0) continua sendo a fonte anatômica aprovada tecnicamente. A anatomia adulta foi mantida integralmente: **10.582 vértices / 10.590 faces**.

O script `tools/blender/realistic_hero_095/assemble_realistic_hero_095.py` tem modo de importação `NECROMANCER_095_ASSEMBLY_ONLY=1`, preservando a montagem anterior e evitando geração duplicada. A versão nova está em `tools/blender/realistic_hero_096/assemble_realistic_hero_096.py`.

A **integridade das coordenadas do corpo e dos dois olhos é verificada** por SHA-256 das coordenadas em double float antes/depois do processo: o hash do corpo é exatamente igual (`38989292ed2dd123c31b8135f2adc18c3202399de1683b74f8bd8cddf9d85e4d`). Nenhuma deformação facial, rigging, animação ou alteração de `unity/`.

## Mudanças implementadas

### 1. Calças

- Preservada a casca de **1.086 quads** originalmente extraída da malha realista CC0 e mantida como objeto editável.
- **917 vértices da roupa** modificados com redução lateral conservadora, discreto alisamento de joelhos/panturrilhas e transição gradual até o quadril.
- Duas costuras de bainha em curvas Blender editáveis, convertidas somente no estágio de exportação FBX.
- Foi criada uma checagem geométrica para impedir que a região das coxas se expanda além da silhueta original, após um primeiro teste falhar artisticamente.

### 2. Cabelo

- A primeira tentativa de 0.9.6 criou 103 mechas volumétricas afiladas; embora tecnicamente correta, **ficou pior visualmente**: pareciam pontas pregadas sobre um capacete liso. Ela foi descartada na renderização final, mas permanece no histórico Git para comparação.
- Foi substituída por **1.760 fibras afiladas em curvas reais do Blender**, distribuídas em quatro grupos editáveis: coroa (820), franja (290), têmporas (310) e nuca (340).
- As raízes são amostradas diretamente dos triângulos temporários de polígonos do scalp extraído da cabeça oficial. Para cada ponto da fibra, o traçado é reprojetado à superfície real por `closest_point_on_mesh` e sofre um deslocamento mínimo para não atravessar a pele.
- A malha original do scalp, com **346 quads**, permanece editável. Seu material foi texturizado com linhas para reduzir a aparência lisa.
- A altura mínima das raízes é **1,76708 m**, impedindo mechas sobre o pescoço/costas.

## GitHub Actions e evidências reais

Workflow: `.github/workflows/realistic-character-preview-096.yml` — Blender 4.5.15 LTS.

| Execução | Resultado técnico | Inspeção artística |
|---|---|---|
| [42555378136](https://github.com/Takeo-Ishikawa/necromancer-overworld/actions/runs/42555378136) | Sucesso | **Reprovado:** coxas triangulares e mechas rígidas |
| [42555795396](https://github.com/Takeo-Ishikawa/necromancer-overworld/actions/runs/42555795396) | Sucesso | Coxas corrigidas; cabelo ainda como pregos/placas |
| [42556515204](https://github.com/Takeo-Ishikawa/necromancer-overworld/actions/runs/42556515204) | **Sucesso** | Nuca muito mais convincente com fibras, sem regressão visível das calças |

Artefato final: **`necromancer-realistic-0-9-6-cc0-groom-tailoring`**, ID **13646958724**, tamanho ZIP ~50,7 MB. Contém `necromancer_realistic_096.blend`, `necromancer_realistic_096.fbx`, oito renders PNG e `source_metadata.json`:

- Corpo inteiro: frente, lateral, costas e três-quartos;
- Rosto: frontal e três-quartos;
- Detalhes: cabelo na nuca e calças.

## Inspeção visual: o que melhorou e o que falta

A inspeção real confirmou que as calças não apresentam mais os volumes triangulares gerados no primeiro teste. A nova nuca deixou de parecer um capacete com espinhos e agora mostra fios curtos com direção coerente sobre a superfície da cabeça.

**Ainda não aprovada artisticamente:** o cabelo ficou curto e uniforme demais na região frontal (efeito de corte raspado), enquanto o conceito original pedia cabelo curto, mas em camadas. As calças estão menos infladas, porém ainda parecem uma roupa extremamente ajustada à anatomia, com marcação exagerada na região pélvica e poucas pregas. Braçadeiras e bolsas continuam blocadas/provisórias. Falta conferir a fidelidade exata contra a folha de referência original, não versionada no GitHub.

**Próxima prioridade (0.9.7):** construir volumes de cabelo superiores em mechas agrupadas **sem reintroduzir pontas rígidas**, criar calças com modelagem de tecido própria em vez de apenas adaptar a casca do corpo, e revisar as braçadeiras e bolsas. Não substituir o personagem atual de Unity até aprovação.
