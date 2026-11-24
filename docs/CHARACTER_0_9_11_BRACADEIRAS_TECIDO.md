# Necromancer Overworld — versão 0.9.11

## Objetivo e limites

Aprimorar bordas e acabamentos das duas braçadeiras e suavizar o caimento frontal da calça, preservando o personagem masculino adulto da base oficial Blender Studio Human Base Meshes v1.4.1, **Body Male – Realistic, CC0**. Não alterar anatomia, olhos, Unity, rigging ou animações.

## O que foi implementado

- `NECROMANCER_0910_BUILD_ONLY=1` permite reutilizar o conjunto anterior em outro script, sem exportações/renders redundantes.
- Sobre a malha REAL das braçadeiras, o Blender identifica arestas abertas de topo e punho, gerando pequenas tiras planas (6 mm de largura), com revestimento de couro preto-acinzentado. As tiras são objetos editáveis e não remodelam os braços. Pequenos pontos de costura de 4 mm substituem os detalhes irregulares da 0.9.10, agora ocultos para comparação.
- Dois passadores de couro discretos para o cinto, em objetos independentes.
- A calça permanece **uma malha conectada**, agora com quatro shape keys; a 0.9.11 acrescenta uma suavização conservadora e reversível do tecido pélvico na direção longitudinal, sem alterações na base anatômica.
- O novo workflow `.github/workflows/realistic-character-preview-0911.yml` exporta `.blend`, `.fbx`, JSON e oito renders reais, além de validar topologia, SHA-256 do corpo, olhos, peças de acabamento e arquivos.

## Critérios de revisão visual

Conferir se as tiras permanecem sobre o couro dos antebraços sem formar asas ou placas isoladas; se os pontos de costura não aparecem como fios soltos; e se o caimento frontal das calças não cria volumes artificiais.

O resultado estético não deve ser declarado aprovado apenas com a passagem no GitHub Actions. O PR #2 permanece em rascunho até avaliação.


## Execuções e decisão após análise visual

- [GitHub Actions 45446394037](https://github.com/Takeo-Ishikawa/necromancer-overworld/actions/runs/45446394037): **sucesso técnico**, mas **reprovado visualmente**. As 4 tiras de couro e 32 pequenos pontos sobre as bordas realmente existiam, porém acompanharam os recortes irregulares das malhas e criaram pontas salientes nas regiões dos pulsos.
- [GitHub Actions 45447248687](https://github.com/Takeo-Ishikawa/necromancer-overworld/actions/runs/45447248687): **sucesso técnico**, oito renders efetivamente inspecionados. Os acabamentos salientes foram ocultados; no lugar deles, foram aplicadas **faixas de material diretamente em 176 faces das braçadeiras** (88 por lado), sem gerar abas geométricas.
- Artefato final: `necromancer-realistic-0-9-11-bracer-trim`, ID **14944789872**. Contém `necromancer_realistic_0911.blend`, `necromancer_realistic_0911.fbx`, metadados JSON e oito PNGs de avaliação.
- Todos os **10.582 vértices e 10.590 faces** do corpo adulto CC0 foram mantidos sem mudanças no hash SHA-256 das coordenadas (`38989292ed2dd123c31b8135f2adc18c3202399de1683b74f8bd8cddf9d85e4d`). Os dois olhos também mantêm suas coordenadas.
- A calça permanece uma única malha de **1.122 vértices / 1.086 quads** e agora contém **quatro shape keys**, incluindo o ajuste pélvico adicional, aplicado a **74 vértices**. Foram incluídos dois passadores discretos de couro no cinto. As duas bolsas arredondadas da 0.9.10 continuam disponíveis.
- As antigas linhas de costura das braçadeiras permanecem ocultas e a nova tentativa de tiras salientes foi conservada, também oculta, no arquivo Blender.

### Avaliação artística final da etapa

As pontas artificiais criadas na primeira renderização desapareceram. A nova borda escurecida tem acabamento discreto, mas ainda segue recortes irregulares da malha original. O punho próximo à mão continua com uma silhueta recortada, e a região pélvica das calças continua excessivamente justa; a melhoria do drape foi discreta, não uma solução completa.

**Aprovação artística do personagem: pendente.** O arquivo continua sem rigging ou animações, o personagem jogável do Unity não foi substituído e o PR #2 continua em rascunho.

### Próxima direção

Considerar reconstruir as braçadeiras a partir de moldes de couro com uma linha de punho controlada, mantendo as proteções atuais como referência; avaliar modelagem real de tecido na pelve, em vez de continuar deformando a casca corporal. Não alterar a anatomia adulta ou integrar ao Unity sem aprovação.
