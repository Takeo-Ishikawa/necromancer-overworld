# Necromancer Overworld — v0.9.13: braçadeiras segmentadas e moldes de calça

## Propósito

Superar a aparência tubular das braçadeiras v0.9.12 criando uma estrutura de **três painéis de couro por antebraço**, com fechamento posterior real, sem remodelar anatomia. Iniciar, em paralelo, a elaboração de moldes próprios de calça, mas sem sobrepor peças ao figurino visível.

## Implementação

- Reutilização da cena completa da v0.9.12 com `NECROMANCER_0912_BUILD_ONLY=1`; duas braçadeiras de formato tubular e suas quatro costuras antigas são preservadas no arquivo Blender, porém ocultas e fora do FBX.
- Cada proteção tem **uma frente e duas metades posteriores**, todos objetos separados, compostos de quad faces e camada UV individual. A geometria procede das seções anatômicas do modelo de teste v0.9.12 (derivado do Blender Studio Body Male – Realistic CC0).
- Uma abertura estreita na parte traseira recebe **oito cadarços cruzados por braço**, apoiados em extremidades reais dos painéis; costuras discretas percorrem as bordas. O rosto, as mãos, os pés e os braços originais não são alterados.
- Materiais foscos e acabamento escuro das bordas foram utilizados para permitir uma comparação com o couro tubular anterior, evitando volumes ornamentais.
- Para começar a produção de calças por moldes, foram criados **cinco objetos de malhas planas (2D)**, representando dois painéis dianteiros, dois traseiros e um cós. Estão na coleção oculta `0913 | five flat trouser cutting patterns HIDDEN STUDY - not stitched`, não são renderizados ou exportados. **Ainda não formam uma calça funcional**: demandam desenho de moldes, costuras/união topológica e caimento físico. A peça visível é a calça conectada validada da v0.9.12, preservada sem alterações.
- O projeto `unity/`, rigs, animações e protagonista jogável não são tocados. PR #2 continua rascunho, sem merge.

## Verificação

O workflow `.github/workflows/realistic-character-preview-0913.yml` executa Blender 4.5.15 LTS, verifica os hashes do corpo e dos olhos, topologia e UV dos seis painéis, cadarços curtos, moldes ocultos e exporta Blender/FBX/JSON com oito PNGs reais.

## Resultado

### Compilações verificadas (24/11/2026)

- [Execução 45473079128](https://github.com/Takeo-Ishikawa/necromancer-overworld/actions/runs/45473079128): **sucesso técnico**; oito renders gerados, porém a vista de detalhe da amarração estava enquadrada no centro das costas e não mostrava o antebraço. O erro era na câmera, não na malha.
- [Execução 45473743993](https://github.com/Takeo-Ishikawa/necromancer-overworld/actions/runs/45473743993): **sucesso técnico**, com o enquadramento corrigido; oito imagens genuínas inspecionadas.
- Artefato final: `necromancer-realistic-0-9-13-panelled-leather` (ID **14957673921**), contendo `necromancer_realistic_0913.blend`, `necromancer_realistic_0913.fbx`, `source_metadata.json` e oito vistas PNG.
- A anatomia adulta original preservou integralmente seu SHA-256 de coordenadas `38989292ed2dd123c31b8135f2adc18c3202399de1683b74f8bd8cddf9d85e4d` antes/depois. Dois olhos também preservados. Corpo: **10.582 vértices / 10.590 faces**.
- Cada antebraço apresenta **três painéis independentes**: um frontal de **378 quads** e dois posteriores de **210 quads** cada, com UV própria para todos os seis painéis. São **1.596 faces quadriláteras** de couro distribuídas entre ambos os antebraços.
- Existem **16 cordões cruzados** traseiros, todos com percurso inferior a **0,020 m**; oito guias finas de borda editáveis. As braçadeiras tubulares 0.9.12 e suas curvas antigas permanecem ocultas no Blender e fora do FBX.
- Foram guardadas **cinco peças planas de molde de calça** como estudo oculto e não exportado: dois painéis dianteiros, dois traseiros e um cós. A calça vestida permanece a peça conectada v0.9.12 de **1.122 vértices / 1.086 faces**, sem alteração.
- Nenhuma alteração em `unity/`, rigging, animações ou personagem jogável.

### Julgamento visual

**Progresso técnico e modelagem modular confirmados.** A vista frontal apresenta painéis de couro mais definidos e acabamento sem protuberâncias pontiagudas. A vista posterior corrigida revela a abertura traseira e a amarração em X ao longo do antebraço.

**Não é um figurino aprovado:** a abertura posterior parece excessivamente profunda e os cordões ainda ficam visualmente pouco destacados. O couro continua rígido e precisa de aba interna/gusset, fechamento e aderência mais verossímeis. A estrutura de 2D da calça não é ainda uma calça costurada ou simulada. A região pélvica do tecido atual continua excessivamente anatômica.

**Próxima prioridade:** experimentar uma tira interna de couro atrás dos cadarços, reduzir o destaque da abertura, revisar o fechamento na altura do punho e avançar de moldes planos para topologia independente de calça com volume e caimento adequados. O PR segue em rascunho; nenhum merge no `main`.
