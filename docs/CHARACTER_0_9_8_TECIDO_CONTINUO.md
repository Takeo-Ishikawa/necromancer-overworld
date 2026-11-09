# Necromancer Overworld — 0.9.8 | Superfície de tecido conectada

## Motivação

Na 0.9.7, criar pernas independentes e tentar conectá-las à pelvis por superfícies sobrepostas gerou emendas visíveis, parecendo bermuda sobre leggings, depois faixas rígidas no quadril. Ambas as soluções foram rejeitadas na inspeção. A 0.9.8 mantém **uma única malha editável e conectada** para a calça visível, em vez de juntar partes incompatíveis.

A fonte do corpo é **Blender Studio Human Base Meshes v1.4.1, Body Male – Realistic, CC0**. Corpo intacto (10.582 vértices / 10.590 faces); dois olhos preservados. SHA-256 das coordenadas dos vértices do corpo e dos olhos comparados antes e depois. Nada de troca de protagonista no Unity ou rigging.

## Alterações propostas

- `tools/blender/realistic_hero_097/assemble_realistic_hero_097.py` passa a aceitar `NECROMANCER_097_BUILD_ONLY=1` para reutilização da cena sem render/export intermediário.
- `tools/blender/realistic_hero_098/assemble_realistic_hero_098.py` cria uma **cópia independente do datablock de roupa**, mantendo a conectividade de faces originais e verificando por BFS o número de componentes.
- Deformação suave em *shape key* separado: diminuição moderada da marcação anatômica na pelve e microdobras longitudinais nas pernas, sem cortar ou colar superfícies. A forma-base permanece acessível como shape key de referência.
- Adiciona uma camada UV própria para o tecido no datablock da roupa, microtextura muito discreta e duas costuras laterais finas projetadas sobre pontos existentes da própria calça.
- A 0.9.7 permanece disponível para comparação. O experimento rejeitado de pernas independentes e pontes fica oculto no `.blend` e fora da exportação FBX.
- Cabelo: conserva os 1.760 fios da 0.9.6 e 180 mechas superiores da 0.9.7; apenas reduz discretamente o brilho das mechas superiores, sem deformar rosto nem adicionar pontas artificiais.

## Critérios de validação

O workflow `.github/workflows/realistic-character-preview-098.yml` usa Blender 4.5.15 LTS no GitHub Actions, exporta `.blend`, `.fbx`, JSON e oito imagens reais (quatro vistas do corpo, rosto 3/4, calças frente/lado, cabelo costas).

Para declarar sucesso técnico, deve verificar-se: corpo inalterado, dois olhos inalterados, **uma só componente conexa para a roupa**, pelo menos 900 quads, shape keys e UV próprios, peças experimentais não exportadas e os oito renders gerados. Para julgar qualidade, será necessário examinar as imagens e identificar possíveis problemas de região pélvica, costuras e clipping.

**Limitação importante:** a superfície é independente como objeto e datablock, mas sua topologia vem de uma casca do corpo original. Ela não equivale a alfaiataria por moldes ou simulação física. Sem a referência aprovada no repositório, não é possível atestar fidelidade visual.

## Execuções e conclusão

A completar após inspeção das imagens reais. PR permanece em rascunho e Unity não é modificado.
