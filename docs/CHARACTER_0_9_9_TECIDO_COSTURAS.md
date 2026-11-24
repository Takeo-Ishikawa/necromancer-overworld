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

### Resultado efetivamente verificado

- Primeira execução [45417508146](https://github.com/Takeo-Ishikawa/necromancer-overworld/actions/runs/45417508146): **falhou** no primeiro raio de busca da costura lateral esquerda, z=0,245. A correção passou a procurar a superfície em diversas profundidades e usar projeção na malha quando não há interseção lateral.
- Segunda execução [45417703707](https://github.com/Takeo-Ishikawa/necromancer-overworld/actions/runs/45417703707): **sucesso** no Blender 4.5.15 LTS e na verificação automatizada; os oito renders foram examinados.
- Artefato: `necromancer-realistic-0-9-9-garment-seam-refine`, ID **14933001810**; inclui `necromancer_realistic_099.blend`, `necromancer_realistic_099.fbx`, oito PNGs e `source_metadata.json`.
- Integridade: **10.582 vértices / 10.590 faces** no corpo realista CC0, hashes de corpo e olhos idênticos antes e depois. A calça continua com **1.122 vértices / 1.086 faces**, apenas uma componente conectada, e agora tem **três shape keys**, incluindo o ajuste frontal.
- **109 vértices da região pélvica** receberam tratamento de tecido; **164 projeções** de costura produziram duas curvas Bézier editáveis; a maior distância entre pontos de controle foi de aproximadamente 5,6 cm. Todas as versões experimentais de calça separada e as costuras 0.9.8 ficaram ocultas.

### Avaliação artística dos PNGs

A região frontal ficou discretamente mais uniforme e as duas costuras têm segmentos mais suaves que o método anterior de ligar vértices isolados. As sombras e a silhueta do corpo adulto não sofreram alterações.

**Não está artisticamente concluído:** as costuras laterais ainda fazem uma curva excessiva ao redor da panturrilha e terminam antes da bainha. A pelve continua mais marcada do que seria esperado em tecido solto. O cabelo, bolsas, fivela e braçadeiras continuam provisórios. A modelagem de tecido é derivada de topologia corporal, não um figurino de produção.

Próxima prioridade: prolongar costuras até as bainhas, suavizar a guia na região do joelho, corrigir o volume pélvico sem afetar a anatomia, refinar os acessórios. Nenhuma integração no Unity ou merge no `main` até aprovação visual.
