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

### Testes técnicos e inspeção real

- [GitHub Actions 45448952592](https://github.com/Takeo-Ishikawa/necromancer-overworld/actions/runs/45448952592): **sucesso técnico**, oito PNGs autênticos inspecionados. A reconstrução eliminou o contorno recortado, mas as duas proteções ficaram largas demais, com aparência de tubos rígidos e bordas horizontais pouco naturais.
- Ajuste posterior: redução conservadora da profundidade e do volume perto dos punhos, maior afunilamento no eixo do braço, inclinação de 3 mm nas bordas de cada anel e microtextura leve no couro. Sem alterações no corpo nem nos olhos originais.
- [GitHub Actions 45449663455](https://github.com/Takeo-Ishikawa/necromancer-overworld/actions/runs/45449663455): **sucesso técnico e oito renders finais inspecionados**. Artefato final `necromancer-realistic-0-9-12-independent-bracers`, ID **14947436737**, com `necromancer_realistic_0912.blend`, `necromancer_realistic_0912.fbx`, `source_metadata.json` e oito PNGs.
- O corpo adulto CC0 permanece com **10.582 vértices / 10.590 faces**, SHA-256 das coordenadas **`38989292ed2dd123c31b8135f2adc18c3202399de1683b74f8bd8cddf9d85e4d`** antes e depois. Os dois olhos também preservaram seus hashes.
- As **duas novas braçadeiras** têm malhas completamente separadas do corpo e entre si, **704 vértices e 672 quads cada**, UV próprias e quatro guias circulares de costura editáveis. O par antigo com bordas recortadas permanece oculto no `.blend` e fora da exportação FBX.
- Em ambas as proteções, raio médio X ~**0,0518 m** e Y ~**0,0632 m** no resultado final, contra ~0,0524 m / 0,0671 m na primeira tentativa. As extremidades foram afuniladas de maneira controlada.
- A calça continua tendo **1.122 vértices e 1.086 faces**, com **uma componente conectada**. Quinto shape key adicionado: `0912 | Relaxed wool forward drape study`; **79 vértices do tecido** sofreram alteração pequena, reversível.

### Parecer artístico

**Evolução aprovada como protótipo técnico, não como personagem final.** A forma das bordas está mais limpa e evita as pontas salientes da 0.9.11, enquanto o segundo ajuste reduz parte da rigidez visual do primeiro loft. No entanto, o couro ainda parece uma proteção tubular simplificada: falta articulação anatômica sutil na seção transversal, encaixe artesanal junto ao punho e variedade visual no material. O tecido pélvico permanece demasiadamente anatômico; o cabelo e o restante do figurino ainda são estudos procedurais.

**Próximo desenvolvimento:** realizar estudo de painéis de couro realmente anatômicos (com superfície frontal e fechamento traseiro), sem regressões de borda; investigar uma calça modelada por moldes/caimento próprio, em vez de deslocar indefinidamente a casca derivada do corpo. A referência conceitual original não está arquivada no repositório, portanto não se afirma fidelidade exata.

**Nenhum arquivo em `unity/` foi modificado.** Rigging e animações não foram adicionados. PR #2 continua **em rascunho**, sem merge no `main`.
