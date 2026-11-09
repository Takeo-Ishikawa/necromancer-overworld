# Necromancer Overworld — 0.9.7: modelagem de tecido e cabelo superior

## Objetivo

Dar continuidade às melhorias da 0.9.6 sem alterar o rosto adulto realista. O cabelo superior estava excessivamente curto; as calças continuavam seguindo exatamente a anatomia do corpo. Esta etapa substitui as pernas das calças por geometria de tecido **independente** e sobrepõe camadas de cabelo suavemente elevadas aos 1.760 fios já existentes.

## Implementação

- Fonte original: Blender Studio Human Base Meshes v1.4.1 (CC0), **Body Male – Realistic**. Topologia 10.582 vértices, 10.590 faces.
- Script `tools/blender/realistic_hero_097/assemble_realistic_hero_097.py`. O script 0.9.6 agora oferece `NECROMANCER_096_BUILD_ONLY=1` para reutilizar a cena sem renders/exports redundantes. A 0.9.6 continua funcionando de maneira autônoma.
- **Calças:** o casco 0.9.6 permanece oculto e editável como comparativo, mas deixa de ser renderizado/exportado. A região superior das calças é extraída das faces de origem, e **dois tubos de tecido independentes**, cada um com 28 anéis e 32 vértices por seção, são construídos em continuidade. As seções são medidas de verdade sobre cada perna, com margens de folga e dobras discretas. Bainhas em tecido e costuras laterais são objetos separados.
- **Cabelo:** mantém os 1.760 fios guiados à malha scalp CC0 da 0.9.6. Adiciona 265 fios longos e discretamente elevados, em dois objetos separados para coroa e franja; as pontas retornam em direção ao couro cabeludo para evitar o efeito de espinhos.
- **Integridade:** SHA-256 de coordenadas do corpo e dos dois olhos comprovam que as malhas humanas originais não foram deformadas. Nenhuma alteração em `unity/`, nenhuma troca do personagem jogável, nenhum rigging ou animação.
- **Entregas:** Blender `.blend`, FBX, JSON de verificações, oito renders reais pelo workflow `.github/workflows/realistic-character-preview-097.yml`.

## Critérios de avaliação visual

A inspeção real de frente e três-quartos deve verificar se a transição entre pelvis e duas pernas de tecido é contínua, se o novo perfil das calças tem folga plausível nos joelhos e se as costuras/bainhas não flutuam. O cabelo deve mostrar camadas na coroa sem repetir a aparência de fios presos em uma capa ou de mechas pontiagudas.

**Este é um protótipo artístico ainda não aprovado.** A referência conceitual original continua ausente do repositório. Preservar rascunho do PR e personagem atual do Unity até avaliação.

## Execução

Pendente de verificar o GitHub Actions e inspecionar os PNGs de forma efetiva.
