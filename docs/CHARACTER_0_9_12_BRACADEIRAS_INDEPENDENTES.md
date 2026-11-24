# Necromancer Overworld — 0.9.12: modelagem independente de braçadeiras

O objetivo é corrigir o problema remanescente da 0.9.11: **contornos pontiagudos nos punhos**, herdados das faces da malha anatômica que originou as antigas braçadeiras.

## Implementação

1. A versão 0.9.11 é importada sem renderização intermediária pela variável `NECROMANCER_0911_BUILD_ONLY=1`. O corpo original `Body Male – Realistic` do pacote Blender Studio Human Base Meshes v1.4.1 (**CC0**) e ambos os olhos são preservados sem alteração de coordenadas.
2. As duas proteções antigas do antebraço continuam disponíveis no `.blend`, mas são arquivadas e ocultas para render/export.
3. Duas novas braçadeiras de couro, com **malhas e topologia inteiramente próprias**, são modeladas a partir de seções reais da geometria original: 22 anéis longitudinais, 32 pontos radiais por anel, 704 vértices e 672 quads por lado. O formato central e o raio variam conforme o braço; as duas extremidades têm planos de corte regulares. Espessura do couro por modificador Solidify e suavização de arestas.
4. Materiais de couro preto-carbonizado e acabamentos escuros integram os punhos às próprias faces da malha. UV própria em cada proteção. Quatro costuras circulares finas, diretamente calculadas nos anéis modelados, são editáveis.
5. Calça: **mesma malha contínua** das versões anteriores, sem tecidos sobrepostos. Acrescentado um quinto *shape key* para suavização e pequena folga frontal reversível. Isso não constitui alfaiataria definitiva, mas deixa o experimento verificável.
6. `unity/`, a cena do personagem jogável, rigging e animações seguem **inalterados**.

## Validação e decisão artística

O workflow `.github/workflows/realistic-character-preview-0912.yml` testa invariantes anatômicas, contagem de quads independentes, UV, shape key, oito renders autênticos e exportações Blender/FBX.

A passagem dos testes comprova integridade da pipeline, não aprova automaticamente a aparência. É necessário inspecionar especialmente se os novos volumes de couro encaixam naturalmente no antebraço e se o punho não ficou excessivamente volumoso. Caso haja regressão, ocultar as duas novas malhas no Blender e restituir o acabamento da 0.9.11. PR permanece em rascunho.

## Execuções e conclusão

A preencher somente após conferir o resultado real.
