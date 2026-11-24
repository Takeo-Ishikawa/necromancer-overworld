# Necromancer Overworld 0.9.9 — revisão do tecido e costuras

Esta etapa responde aos dois problemas observados nos oito renders da 0.9.8: saliência anatômica excessiva na frente das calças e costuras com zigue-zague causadas por escolher o vértice mais externo de cada intervalo vertical.

## Procedimento

- A anatomia e os dois olhos originais continuam imutáveis, protegidos por hash das coordenadas de todos os vértices da base CC0 **Body Male - Realistic**, Blender Studio v1.4.1.
- O tecido permanece uma **malha conectada**, com sua própria UV e dois shape keys de referência da 0.9.8. A 0.9.9 acrescenta o terceiro shape key `099 | Woven fabric front drape`, suavizando somente vértices na região pélvica frontal, com queda gradual nas bordas da seleção.
- As duas costuras laterais antigas são ocultas. No lugar delas, o Blender calcula **164 interseções reais com a superfície avaliada** da roupa, uma por altura da linha lateral de cada perna, e gera duas curvas Bézier editáveis, sem saltos entre vértices.
- Os projetos de tubos independentes e pontes da 0.9.7 permanecem arquivados e ocultos no `.blend`.
- Não se altera `unity/`, não há rigging nem animações.

## Artefatos previstos

O workflow `.github/workflows/realistic-character-preview-099.yml` usa Blender 4.5.15 LTS para produzir `.blend`, `.fbx`, metadados JSON e oito renders. A integração no Unity está bloqueada até aprovação artística.

## Verificação

Pendente de inspeção dos renders e do GitHub Actions. Uma compilação bem-sucedida não substitui avaliação visual.
