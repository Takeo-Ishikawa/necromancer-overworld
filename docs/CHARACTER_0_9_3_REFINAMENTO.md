# Necromancer Overworld — 0.9.3: rosto adulto, corte em camadas, alfaiataria

## Mudanças em relação à 0.9.2

Este passe parte das **mesmas 12.502 vértices e 12.500 faces** da malha oficial Blender Studio Human Base Meshes v1.4.1, Body Male – Stylized (CC0). Nenhuma primitiva substitui ou reconstrói a anatomia. `sculpt_character_092.py` pode retornar sem exportar/renderizar quando `NECROMANCER_092_BUILD_ONLY=1`, permitindo que o novo script `sculpt_character_093.py` refine objetos existentes.

1. **Expressão adulta:** redimensionamento dos dois objetos oculares originais; ajuste da mandíbula, nariz, maçãs do rosto, orelhas, sobrancelhas e pálpebras, preservando a malha humana. Íris reancoradas nos olhos modificados.
2. **Cabelo com camadas:** substituição das fitas rígidas da 0.9.2 por 485 mechas afiladas que partem de pontos da superfície real do scalp, em três distribuições (coroa, franja e têmporas). Fundação mais escura e discreta.
3. **Calças:** reorganização suave das seções horizontais da malha extraída do corpo, suprimindo volumes anatômicos exagerados de joelho e panturrilha; interpolação de caimento com afunilamento, pregas discretas e transição no quadril e tornozelo.
4. **Materiais:** pele menos clara e com microtextura; tecido escuro com relevo discreto; fios dourados menos brilhantes, seguindo costura e bainha em vez de setas.
5. **Editabilidade:** cabelo, roupa, rosto e acessórios em coleções independentes; `.blend` salvo com curvas editáveis, `.fbx` exportado separadamente.

## Pipeline e critérios objetivos

- Branch: `feature/necromancer-anatomy-092`, mantendo o PR #1 em rascunho.
- Script: `tools/blender/anatomical/sculpt_character_093.py`.
- Workflow: `.github/workflows/anatomical-character-preview.yml` (Blender 4.5.15 LTS no GitHub Actions).
- Artefato: `necromancer-anatomical-0-9-3-cc0-preview` contendo `.blend`, `.fbx`, sete PNGs e JSONs de proveniência.
- A CI valida integridade das contagens da malha de origem, corpo, olhos CC0, vestimenta, cabelo, exportações e renders.
- Não modifica a pasta `unity/`. Sem rigging, animação ou substituição do protagonista jogável.

## Avaliação artística

**Não aprovar automaticamente pelo status do CI.** Conferir as sete imagens geradas. A referência visual original não consta do repositório; portanto não é possível afirmar fidelidade definitiva. Rosto, franja e pregas gerados continuam sendo um protótipo automatizado, ainda sujeito a escultura artística e ajustes específicos.

## Execuções verificadas

Esta seção deverá ser atualizada somente após a inspeção das imagens reais e dos artefatos produzidos.
