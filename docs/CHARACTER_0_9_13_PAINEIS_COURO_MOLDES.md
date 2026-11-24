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

Pendente de análise dos renders. A execução técnica não constitui aprovação artística.
