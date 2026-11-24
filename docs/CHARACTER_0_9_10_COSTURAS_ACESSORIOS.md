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

### Resultado e inspeção verificados (24/11/2026)

Foram executados dois ciclos principais do Blender 4.5.15 LTS, além da execução intermediária em que o código estava atualizado, mas o workflow ainda não tinha sua checagem de comprimento dos fios:

- [45420105804](https://github.com/Takeo-Ishikawa/necromancer-overworld/actions/runs/45420105804): **sucesso técnico**, porém **reprovado visualmente** no acabamento das braçadeiras. As primeiras linhas decorativas criaram traços soltos que ultrapassavam os pulsos e alcançavam a região das coxas.
- [45421028322](https://github.com/Takeo-Ishikawa/necromancer-overworld/actions/runs/45421028322): **sucesso técnico e revisão visual concluída**. As linhas longas foram substituídas por traços curtos apoiados em arestas reais do modelo original, com teste explícito para impedir comprimentos exagerados. O defeito das linhas soltas foi eliminado no render frontal e nos detalhes dos antebraços.

Artefato final: `necromancer-realistic-0-9-10-garment-accessories`, ID **14934880825**, contendo `necromancer_realistic_0910.blend`, `necromancer_realistic_0910.fbx`, `source_metadata.json` e **oito vistas reais**: frente, costas, lateral, três-quartos, quadril frontal, bolsas, costura lateral e braçadeiras.

**Dados medidos nos metadados finais:**

- Fonte CC0 realista oficial preservada com **10.582 vértices e 10.590 faces**. Hash de coordenadas do corpo antes/depois: `38989292ed2dd123c31b8135f2adc18c3202399de1683b74f8bd8cddf9d85e4d`. Os dois olhos mantiveram seus hashes originais.
- Calça: **1.122 vértices / 1.086 faces**, uma única componente conectada.
- **Duas costuras Bézier completas**, cada uma com 16 pontos de controle; maior salto entre pontos de controle: 0,05838 m. As extremidades ficam **0,00934 m e 0,00965 m** (menos de 1 cm) acima da borda inferior da malha de tecido.
- Seis peças das bolsas antigas arquivadas e ocultas; duas novas bolsas arredondadas, dez subpeças de equipamento editáveis (malhas de corpo/aba/fechos, costuras e fixações).
- Duas braçadeiras existentes preservadas como objetos de origem, agora com couro procedural acinzentado. **16 pequenos pontos de costura** projetados em arestas reais; comprimento máximo **0,01989 m**, sem fios longos pendentes.
- Nenhum arquivo de `unity/` foi modificado; sem rigging, animação ou substituição do protagonista jogável.

### Avaliação artística

O resultado melhorou concretamente em relação à 0.9.9: as costuras laterais chegam à bainha com um percurso mais suave, as bolsas têm volumes orgânicos em vez de blocos simples, e a revisão final removeu a falha evidente dos traços soltos nas braçadeiras.

**Ainda não aprovado como personagem definitivo:** o couro e os detalhes ainda são simplificações procedurais; os pontos nas braçadeiras têm distribuição pouco natural, o contorno inferior das proteções é irregular, a calça continua ajustada demais à pelve, e o corte de cabelo é pouco expressivo. A referência conceitual original não está presente na árvore do repositório para uma comparação de fidelidade.

**Próxima prioridade:** modelar uma borda de braçadeira coerente, uniformizar o padrão das costuras e melhorar o acabamento do cinto e da região pélvica. O PR segue em **rascunho**, sem merge no `main`.
