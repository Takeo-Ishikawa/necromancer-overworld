# Necromancer Overworld — 0.9.4: escultura facial adulta

## Origem e continuidade

A versão 0.9.4 não importa um novo personagem genérico: executa a construção da 0.9.3 em modo `NECROMANCER_093_BUILD_ONLY` e altera os vértices da malha original **Blender Studio Human Base Meshes v1.4.1 — Body Male Stylized (CC0)**. Contagens anatômicas obrigatórias: **12.502 vértices e 12.500 faces**. O arquivo `sculpt_character_093.py` permanece funcional autonomamente e a nova versão está em `sculpt_character_094.py`. O projeto Unity não é alterado.

## Mudanças da 0.9.4

1. Rosto: redução localizada das maçãs arredondadas, mandíbula mais angulada, queixo definido e relevo de nariz, com deformações contínuas nos vértices originais, sem voxel/remesh ou cabeça de primitivas.
2. Olhos: redução adicional da abertura ocular e dimensionamento dos **dois olhos originais** do CC0. As quatro superfícies de íris/pupila foram reposicionadas sobre os olhos alterados para evitar elementos flutuando.
3. Orelhas: aproximação das orelhas ao crânio e ligeira redução da altura, com registro do número de vértices afetados.
4. Sobrancelhas: substituição das duas linhas finas da 0.9.3 por duas pequenas malhas de faixa progressivamente afilada, ancoradas por raycast à superfície da testa. Os traços das pálpebras continuam em curvas editáveis.
5. Materiais: pele com tonalidade pálida fria e cabelo menos brilhante, mantendo os objetos de cabelo e vestuário separados.

## Inspeção programada

O workflow `.github/workflows/anatomical-character-preview.yml` usa Blender 4.5.15 LTS no GitHub Actions. Exporta `necromancer_character_094.blend` e `necromancer_character_094.fbx`, JSON de contagens e **nove renders reais**: frente, perfil, costas, três-quartos, rosto frontal, rosto três-quartos, rosto perfil, detalhe dos olhos e detalhe da calça. O estágio de Blender permanece editável; curvas são convertidas em geometria somente para FBX.

Validações: mesmas 12.502/12.500 contagens de corpo, deformação efetiva de rosto/orelha, dois olhos CC0, quatro objetos de íris/pupila e duas malhas de sobrancelha. O CI não substitui avaliação artística. **A folha visual aprovada ainda não está versionada neste repositório, logo a fidelidade exata não pode ser atestada.**

Status artístico: **não aprovado por padrão**. Não realizar merge ou substituir o protagonista jogável até inspeção e aprovação.

## Execuções e avaliação visual

Aguardando registro de execução e imagens verificadas.
