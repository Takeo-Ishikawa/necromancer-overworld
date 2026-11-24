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
