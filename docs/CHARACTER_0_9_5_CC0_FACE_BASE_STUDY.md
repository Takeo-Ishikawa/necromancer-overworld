# Necromancer Overworld — 0.9.5: estudo de base facial adulta CC0

## Mudança de estratégia

A sequência 0.9.2–0.9.4 mostrou piora na identidade do protagonista. Novas deformações sobre um rosto originalmente estilizado, com olhos e bochechas de traços juvenis, não corrigiram o problema. **A 0.9.4 fica preservada em outra branch e não deve ser considerada a base de produção aprovada.**

O pacote oficial Blender Studio Human Base Meshes v1.4.1 (CC0) inclui duas malhas masculinas editadas por artistas: `Body Male - Stylized` e `Body Male - Realistic`. Este estudo trabalha diretamente com ambas, **sem escultura procedural facial e sem usar primitivas**.

## Entrega deste estudo

- Script: `tools/blender/studies/compare_cc0_male_bases_095.py`.
- Workflow isolado: `.github/workflows/character-base-study-095.yml`.
- Cada base é importada da coleção oficial e normalizada para 1,90 m.
- Iluminação, material fosco, câmera e escala iguais para permitir uma comparação justa em quatro vistas por modelo.
- O Blender salva as duas coleções editáveis no mesmo `.blend` e exporta o FBX original da opção realista, sem integrá-lo ao jogo.
- JSON inclui número de vértices, faces, objetos oculares e checagem estrita de equivalência topológica dos polígonos. Se o número de vértices ou a ordem dos polígonos diferirem, **não é permitido copiar deformações de um modelo para outro** sem uma transformação própria.

## Critérios de decisão

A base realista só deve substituir a estilizada no próximo estágio se as imagens reais demonstraram qualidade facial adulta, melhor perfil, proporções adequadas e olhos anatomicamente coerentes. Caso seja demasiado realista, utilizar a geometria realista como referência de escultura ou transferência controlada, e combinar com o tratamento estilizado de materiais e cabelo somente após validar a compatibilidade.

**Nenhuma alteração em `unity/`, nenhuma substituição do herói jogável e nenhuma preparação de rigging.** A folha conceitual aprovada continua ausente do repositório, de modo que o estudo avalia coerência anatômica, não identidade artística final.

## Resultado de execução

- GitHub Actions [42551358033](https://github.com/Takeo-Ishikawa/necromancer-overworld/actions/runs/42551358033): **sucesso**, oito renders reais, .blend de comparação e FBX da base realista.
- Base Stylized: 12.502 vértices, 12.500 faces, largura de cabeça aferida 0,2958 m.
- Base Realistic: 10.582 vértices, 10.590 faces, largura de cabeça aferida 0,2050 m (em ambos os casos normalizados para 1,90 m).
- Ordem de loops e contagem de vértices **não compatíveis**; transferência de vértices direta seria incorreta.
- Inspeção frontal e de perfil: base realista com olhos menores, mandíbula/nariz mais adultos e orelhas proporcionais. A base estilizada tem traços infantis, sobretudo olhos/orelhas excessivos.
- Decisão: adotar a malha **Realistic como candidata** ao herói, sem copiar a escultura facial da 0.9.4. O estudo sozinho não valida cabelo/roupas ou a semelhança final à arte aprovada.
