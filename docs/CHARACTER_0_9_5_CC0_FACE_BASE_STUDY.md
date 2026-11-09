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

A registrar após a execução do GitHub Actions e inspeção real das oito imagens.
