# Protagonista masculino — versão 0.8

## Referência aprovada
Turnaround enviado pelo usuário em 2026-11-07: homem adulto, corpo musculoso com torso descoberto, cabelo curto grisalho/lilás, calças carvão até a panturrilha com ornamentos dourados, cinto e bolsas de couro, braçadeiras escuras, pés descalços. **Não adicionar** capuz, cajado, túnica, botas ou magia no início do jogo.

## Estado de entrega
Primeira etapa **em andamento**: `tools/blender/generate_necromancer_base.py` cria um *blockout* 3D editável em Blender 4.x e exporta FBX. Corpo, cabelo, roupa e acessórios são objetos separados. **Não é um modelo final fiel ao turnaround**: os volumes são simplificados e ainda faltam escultura anatômica, rosto detalhado, cabelo refinado, topologia adequada à deformação, UV, texturas e esqueleto.

A automação GitHub Actions `Necromancer Character 3D Preview` executa Blender em ambiente isolado, exporta o `.blend` e `.fbx`, renderiza vistas frontal, lateral e posterior e disponibiliza os arquivos como artifact. As execuções iniciais falharam: o Blender 4.0.2 do runner não encontrava `numpy` para exportar FBX, e o renderizador Workbench abortou no Linux headless. Foi adicionado `python3-numpy`/PYTHONPATH e o renderizador foi trocado por Cycles CPU. O problema posterior de ausência de OpenImageDenoiser foi corrigido desativando denoising; o workflow `42441775368` concluiu todas as etapas com sucesso, inclusive o upload do artifact. Nenhum FBX final foi adicionado ao Unity, e a cena jogável existente permanece inalterada.

## Como gerar a base
Instalar Blender 4.x e executar a partir da raiz do repositório:

```bash
blender -b --python tools/blender/generate_necromancer_base.py
```

Arquivos locais resultantes: `tools/blender/character_base.blend` e `tools/blender/character_base.fbx`. Para gerar imagens de inspeção, executar `blender -b tools/blender/character_base.blend --python tools/blender/render_character_turnaround.py`. A automação `.github/workflows/character-model-preview.yml` faz as duas etapas e publica o artifact `necromancer-character-0-8-blockout` com os arquivos 3D e as três imagens. Abrir o .blend, corrigir a anatomia e verificar exportação FBX. Não substituir o personagem no jogo antes de aprovar o resultado.

## Pipeline para fidelidade
1. Aprovar silhueta e proporções do corpo nas vistas frontal, lateral e posterior.
2. Esculpir corpo e rosto de acordo com a referência; retopologia deformável e UV.
3. Modelar cabelo em mechas, calças e bordados, braceletes e pés com dedos individualizados; texturizar.
4. Criar armature humanoide e skinning; testar deformações de ombro, cotovelo, quadril, joelho, tornozelo e dedos.
5. Criar animações de idle, caminhada, corrida, soco, chute, impacto e morte, **sem poderes mágicos iniciais**.
6. Importar FBX no Unity, configurar materiais e Animator; conectar ataques desarmados ao combate automático e validar Windows/Android.

## Regra de gameplay
A primeira fase não concede necromancia automaticamente. O desbloqueio da habilidade de reanimar deverá ser tratado em marco separado, com progressão e tutorial. **A mecânica de reanimação existente ainda está habilitada no protótipo 0.7**; não alterar silenciosamente até definir o gatilho de desbloqueio.

## Critérios de aceitação
- Silhueta reconhecível em câmera 2.5D.
- Proporções e vestuário próximos ao turnaround.
- Malha e esqueleto preparados para animações físicas.
- Materiais adequados para Android e Windows.
- Builds e testes concluídos antes de declarar a 0.8 pronta.

## Iteração visual 0.8.1
O gerador foi refinado com queixo, lábios, sobrancelhas, maçãs do rosto, clavículas, oblíquos, dedos separados, abas das bolsas, dobras das calças, faixa pendente do cinto e mais mechas de cabelo. Essas peças continuam modulares e simplificadas. O commit desta iteração dispara uma nova execução do workflow para validar exportação e vistas. **Não interpretar essas melhorias como escultura final ou rigging.**

## Iteração visual 0.8.2 — continuidade corporal
O workflow da 0.8.1 concluiu com sucesso (run `42442060059`). O gerador agora mantém cópias das peças anatômicas na coleção oculta `Editable body source - hidden` e gera uma superfície corporal de prévia com voxel remesh (resolução 0,016 m). Cabelo, roupa, acessórios e detalhes faciais continuam independentes. A exportação FBX seleciona apenas as peças visíveis, evitando duplicar o corpo. **Ainda não há retopologia deformável nem rig; a malha de prévia não deve ser usada diretamente para animação.** A nova versão precisa passar pelo workflow e por inspeção das três vistas.

## Versão 0.8.3 — reconstrução da malha com prioridade em fidelidade
A referência visual aprovada mostra um protagonista masculino estilizado de proporções alongadas, rosto adulto, cabelo curto em camadas cinza-lilás, torso atlético exposto, braçadeiras escuras/bronze, calças carvão amplas bordadas em ouro, bolsas de cintura e pés descalços.

Foi criado `tools/blender/generate_necromancer_083.py`, uma **nova construção** (independente dos blockouts 0.8.1 e 0.8.2). O torso, rosto, braços, mãos, panturrilhas, pés e calças agora são malhas geradas por seções anatômicas e superfícies contínuas em vez de peças esféricas. Os volumes do peitoral e abdômen estão integrados à superfície do torso, e as calças recebem dobras procedurais; cabelo, acessórios e bordados são editáveis como elementos separados no `.blend`.

O workflow `Necromancer Character 3D Preview` foi direcionado ao novo gerador e publica o pacote `necromancer-character-0-8-3-remodel` após exportação FBX e renderização das vistas. O gerador anterior permanece para histórico técnico.

**Limitações importantes**: trata-se de uma remodelagem procedural ainda sujeita a aprovação visual. Não corresponde a escultura high-poly, retopologia final, UVs acabadas, rigging ou animações. Não substituir o protagonista jogável no Unity antes de examinar as vistas renderizadas e aprovar a silhueta/rosto/roupas.

## Verificação da remodelagem 0.8.3
O workflow **42443059298** (commit `18a83b4`) terminou com sucesso: novo `.blend`, `.fbx` e vistas frontal, lateral e posterior no artifact `necromancer-character-0-8-3-remodel`. A geometria de ombros/braços/tronco foi reunida para prévia com remesh, enquanto as superfícies anatômicas originais ficaram preservadas numa coleção oculta para edição. As imagens foram inspecionadas. **O resultado ainda não é suficientemente fiel ao conceito para aprovação artística**: falta escultura detalhada do peitoral e abdômen, refinamento adulto do rosto, penteado mais convincente, calças menos rígidas e mãos/pés mais naturais. Não alterar personagem jogável nem iniciar rigging até solucionar esses pontos.

## Iteração 0.8.4 — aproximação ao conceito original
A referência aprovada é a folha de caminhada com oito vistas: homem adulto de cabelos cinza-lilás, peitoral/abdômen fortes mas anatomia natural, olhos expressivos, braços definidos, calça escura com bordados dourados até abaixo dos joelhos, bolsa presa ao cinto, braçadeiras ornamentadas e pés descalços.

Foi desenvolvido `tools/blender/sculpt_necromancer_084.py`, executado **depois** de `generate_necromancer_083.py`. O novo estágio modifica a malha unificada do corpo para criar relevo do peitoral, seis gomos abdominais, oblíquos, músculos dorsais e ombros mais suaves; afina o queixo; substitui o nariz bulboso por geometria angular; reconstrói o cabelo em mechas curvas com divisão central; alonga as calças, reduz sua largura no quadril e adiciona detalhes às braçadeiras e bolsas. A superfície-base, cabelo, roupas e acessórios permanecem editáveis no projeto Blender.

O workflow publica `necromancer-character-0-8-4-refinement` com `.blend`, `.fbx` e três vistas de inspeção. **Não substituir o protagonista no jogo até validar visualmente a execução e aprovar a fidelidade**. Essa etapa ainda não consiste em escultura manual de alta fidelidade, topologia de deformação ou rigging. O personagem original da cena Unity não foi modificado.

### Validação executada da 0.8.4
A execução [42443894507](https://github.com/Takeo-Ishikawa/necromancer-overworld/actions/runs/42443894507) concluiu com sucesso: o gerador 0.8.3, o refinamento 0.8.4, a exportação FBX, três renderizações e o upload do pacote `necromancer-character-0-8-4-refinement` (Blender e FBX). As prévias foram inspecionadas visualmente. **A renderização melhorou relevo abdominal e comprimento das calças, mas continua abaixo da fidelidade solicitada**: rosto pouco expressivo, cabelo com aspecto de bloco, ombros quadrados, pés rígidos, calças pouco naturais. Manter o modelo fora da Unity até revisão artística aprovada; não declarar rigging/produção final.

## Iteração 0.8.5 — reconstrução facial e cabelo
Esta iteração acrescenta `tools/blender/sculpt_necromancer_085.py` como estágio posterior aos scripts 0.8.3 e 0.8.4. O script substitui a geometria de olhos e cabelo, reconstrói olhos abertos amendoados, íris âmbar e pupilas, sobrancelhas angulares, orelhas menores, mandíbula mais afilada, maçãs do rosto e detalhes discretos de nariz e boca. O corte cinza-lilás usa mechas 3D com seção transversal, franja dividida para deixar os olhos visíveis, camadas nas têmporas e nuca. Os objetos continuam separáveis no Blender.
O workflow valida e publica, além de frente/lado/costas, novas vistas de rosto de frente e três quartos. O pacote chama-se `necromancer-character-0-8-5-face-hair`. Os arquivos são gerados integralmente pelo GitHub Actions, sem software local; rigging e integração Unity permanecem bloqueados até aprovação artística.

### Verificação prática da 0.8.5
O workflow [42444554363](https://github.com/Takeo-Ishikawa/necromancer-overworld/actions/runs/42444554363), commit `7bdcaba`, concluiu com sucesso a geração dos modelos .blend/.fbx, as três vistas de corpo inteiro e duas inspeções da cabeça. Artifact publicado: `necromancer-character-0-8-5-face-hair`. Corrigimos o nariz muito projetado, a ausência visual da boca e o padrão de pontas radiais da franja; a luz de inspeção foi reduzida para 430 W.

**Inspeção visual crítica:** embora a expressão facial seja legível e o penteado tenha ficado menos regular, a fidelidade à arte ainda é insuficiente. Os ombros permanecem largos e blocados, o peito tem relevo simplificado, a calça ainda está rígida, e as feições precisam de refinamento artístico adicional. A postura de inspeção é simétrica e não corresponde à caminhada retratada na folha conceitual. Esse modelo não deve ser tomado como versão final nem substituído no jogo antes de aprovação artística. O próximo passe deverá priorizar a silhueta e o caimento da roupa, não iniciar rigging.

## Iteração 0.8.6 — silhueta anatômica, calças e adornos
Novo estágio `tools/blender/sculpt_necromancer_086.py`, executado após os geradores 0.8.3, 0.8.4 e 0.8.5 no workflow de prévias. Esta versão modifica a malha corporal existente para reduzir os ombros excessivamente retos e largos, suaviza a junção deltoide/trapézio, ajusta discretamente a largura do rosto, cria variação volumétrica e franzidos na superfície real das calças, alivia o volume artificial na região frontal da cintura, substitui os zig-zags por bordados de folhas e espirais projetados sobre a malha da roupa e diferencia as bolsas direita e esquerda. O projeto Blender continua editável; o FBX é exportado pelo GitHub Actions.

**Critérios de aprovação**: inspecionar frente, perfil, costas e close-ups e comparar a silhueta com o conceito original. O modelo ainda não tem escultura manual de produção, retopologia para deformação, armature nem animações. Não modificar o Unity antes da aprovação.

### Verificação da 0.8.6 — concluída
A execução [42445459435](https://github.com/Takeo-Ishikawa/necromancer-overworld/actions/runs/42445459435), commit `bc63c187`, passou em todas as etapas (geração 0.8.3, refinamentos 0.8.4/0.8.5/0.8.6, FBX, 5 renderizações e upload). Artefato: `necromancer-character-0-8-6-silhouette-cloth`, contendo `character_base.blend`, `character_base.fbx`, vistas frontal/lateral/traseira e duas aproximações do rosto. O modelo foi inspecionado visualmente contra a referência original: ombros estão mais suaves e sem a antiga tampa horizontal evidente; braçadeiras foram realinhadas, o bordado está mais discreto, as calças apresentam pequenas dobras e as bolsas deixaram de ser idênticas.
**Avaliação de qualidade:** melhora localizada, não aprovação final. O formato da cabeça e cabelo permanece simplificado, a anatomia peitoral e abdominal ainda é rígida, as mãos e os pés carecem de detalhe, e o caimento da calça continua aquém da arte. A pose neutra de inspeção não reproduz a caminhada do conceito, por decisão técnica até o rigging. O progresso não deve ser confundido com escultura realista de alta fidelidade. Preservar o personagem jogável atual.

## Iteração 0.8.7 — mãos, pés e anatomia dos membros
O estágio `tools/blender/sculpt_necromancer_087.py` foi adicionado ao pipeline automatizado após a 0.8.6. Substitui as antigas mãos construídas por segmentos simples por uma palma modelada por seções, quatro dedos de comprimento desigual, polegar lateral, juntas suavizadas em uma única superfície e unhas discretas. Os pés descalços agora utilizam seções do calcanhar ao antepé, cinco dedos anatomicamente graduados e união volumétrica com a malha do pé; tornozelos e panturrilhas recebem contornos mais suaves. Bíceps, tríceps, antebraços e serrátil ganham deslocamentos sutis na superfície da malha corporal. Materiais e acessórios permanecem separados. As geometrias substituídas são preservadas numa coleção oculta no arquivo Blender, sem duplicatas visíveis na exportação.

A etapa cria duas inspeções extras (`character_hand_detail.png`, `character_foot_detail.png`) além das cinco já disponíveis, com pacote `necromancer-character-0-8-7-hands-feet`. Verificar o status do workflow antes de afirmar que a execução foi concluída. O arquivo não possui rig, UVs finais nem topologia preparada para animação. O jogador atual no Unity permanece intacto.

### Verificação da 0.8.7 — concluída
A execução final do GitHub Actions [42446344745](https://github.com/Takeo-Ishikawa/necromancer-overworld/actions/runs/42446344745) (commit `9127d3e`) terminou com sucesso, incluindo todas as etapas de geração, scripts 0.8.3–0.8.7, FBX, sete imagens e publicação do artefato `necromancer-character-0-8-7-hands-feet`. O ZIP contém `character_base.blend`, `character_base.fbx`, vistas de corpo inteiro (frente, lado, costas), duas vistas da cabeça e detalhes das mãos e dos pés.

A primeira inspeção havia revelado luvas cilíndricas volumosas nos punhos, unhas parecidas com contas e tornozelos com esferas salientes. O gerador 0.8.7 foi corrigido: retira os antigos cilindros das mãos, alonga dedos, reserva unhas para futura texturização e suaviza tornozelos diretamente na malha da panturrilha sem esferas externas. A segunda inspeção visual confirmou a remoção desses três artefatos.

**Ainda não aprovado como personagem final:** mãos e pés continuam estilizados e simplificados; não há unhas por textura, articulações refinadas, retopologia para skinning ou estrutura óssea. O maior obstáculo restante é a fidelidade global do rosto e da roupa à referência original; a 0.8.7 é um passe incremental anatômico, não um salto para escultura high-poly. O personagem Unity permanece preservado.

## Iteração 0.8.8 — integração corporal e calças contínuas
Novo estágio `tools/blender/sculpt_necromancer_088.py`, executado após a 0.8.7, com prioridade em reduzir a aparência de peças encaixadas na cintura e no quadril. Modifica discretamente a malha unificada do tronco para suavizar transições de peitoral, serrátil, oblíquos e deltoide. Preserva as três malhas de origem das calças em uma coleção oculta e cria uma nova peça contínua `Garment 088 | single draped trousers` por voxel remesh, com volumes e dobras esculpidos sobre a nova superfície, mantendo as barras das calças como elementos independentes. Remove bordados projetados na geometria antiga e recria ornamentos dourados discretos sobre a geometria final. Adiciona materiais procedurais leves de variação de cor e microtextura à pele, ao couro e ao tecido (sem arquivos externos).

O workflow produz também `character_torso_detail.png` e `character_trouser_detail.png`, totalizando nove vistas para revisão de silhueta e materiais. Nome do artifact `necromancer-character-0-8-8-organic-cloth`. **Trata-se de uma modelagem procedural preliminar, ainda sujeita a inspeção e aprovação artística**. Ainda não há rig, skinning nem topologia de deformação. Não substituir o protagonista jogável no Unity sem aprovação.

### Verificação e avaliação visual da 0.8.8
O workflow final [42498482176](https://github.com/Takeo-Ishikawa/necromancer-overworld/actions/runs/42498482176), commit `544333cc`, concluiu com **success**. A exportação publicou `necromancer-character-0-8-8-organic-cloth`: `character_base.blend`, `character_base.fbx` e nove imagens de inspeção (frente, lado, costas, duas aproximações do rosto, mão, pé, tronco e calças). A geração passou pelos estágios 0.8.3–0.8.8, renderizou e validou os arquivos sem falhas. A malha de tecido unificada e a microtextura foram verificadas pelas imagens.

Ao comparar as vistas, a região do quadril aparece mais contínua que na 0.8.7 e os traços artificiais do peitoral foram removidos. **Entretanto, a sombra triangular profunda abaixo do cinto persiste**: a ponte de tecido e o deslocamento no centro não resolveram completamente a topologia visual da virilha. A textura das calças continua irregular e ainda há diferenças grandes de rosto, cabelo e anatomia diante do conceito original. A malha permanece **não aprovada para integração ou rigging**. O próximo passe deve reconstruir a topologia da união superior das pernas e da região da virilha, em vez de aplicar novos deslocamentos superficiais sobre a mesma geometria.

## Iteração 0.8.9 — reconstrução topológica da virilha e pernas
Em vez de continuar deformando a malha com sombra triangular da 0.8.8, foi adicionado `tools/blender/rebuild_trousers_089.py`. O novo estágio gera a calça como **uma única superfície contínua** definida por volumes suaves do quadril e de ambas as pernas. Uma malha quad-dominante é reconstruída pelo algoritmo de *surface nets*, usando NumPy já disponível no GitHub Actions. O algoritmo suaviza a transição da virilha, cria uma peça sem as superfícies internas sobrepostas da versão anterior e regenera os bordados dourados na superfície verdadeira. O gerador inclui verificação automática de cobertura do tecido na linha frontal central em quatro alturas: 0,76 m, 0,82 m, 0,88 m e 0,94 m. A malha 0.8.8 fica preservada, oculta, no arquivo Blender para edição e reversão, mas não aparece no FBX.

O workflow de prévias foi atualizado para o pacote `necromancer-character-0-8-9-trouser-topology` e continua gerando nove vistas. A 0.8.9 exige **inspeção do render final**, pois os testes de continuidade não garantem, por si sós, fidelidade artística. Continuam pendentes retopologia para animação, UVs e rigging; o personagem ativo no Unity não deve ser substituído antes da aprovação.

### Validação executada da 0.8.9
A execução final do workflow [42504050802](https://github.com/Takeo-Ishikawa/necromancer-overworld/actions/runs/42504050802), commit `f484009c`, foi concluída com **success**. O pipeline executou todos os estágios 0.8.3–0.8.9, gerou `.blend` e `.fbx`, validou as quatro alturas da frente da calça e publicou nove imagens de prévia no artifact `necromancer-character-0-8-9-trouser-topology`.

A inspeção da vista frontal e do detalhe da calça confirmou que a antiga sombra triangular profunda da 0.8.8 foi substituída por uma divisão mais baixa e arredondada das pernas. A primeira versão 0.8.9 ficou excessivamente semelhante a uma saia/shorts inflado; uma segunda alteração estreitou o quadril e elevou a linha da virilha. **Ainda existe uma sombra sob o entrepernas e o volume superior da calça continua mais rígido do que a referência**, apesar da melhor continuidade topológica. A malha ainda não tem retopologia apropriada para rigging; não substituir o personagem no Unity. A próxima iteração artística deve trabalhar a cintura, a transição mais natural do quadril e as dobras de roupa do conceito, mantendo a nova superfície única como base.

## Iteração 0.9.0 — caimento de tecido e cintura
O estágio `tools/blender/tailor_necromancer_090.py` é executado depois da malha 0.8.9: não substitui o trabalho de continuidade da virilha, mas modifica a superfície da roupa para reduzir o volume do quadril, ajustar o perfil da cintura e criar dobras verticais e compressões junto aos joelhos e às barras. A região central da virilha recebe uma máscara protetora contra novas deformações profundas. Os bordados são refeitos contra a superfície final, a bolsa direita fica menos volumosa, e a variação de cor/textura do tecido é suavizada.

A malha 0.8.9 anterior é preservada na coleção oculta `Editable 0.8.9 garment before tailoring | hidden` dentro do projeto Blender. O script gera `character_090_metrics.json`, com contagem de faces/vértices, amostras da superfície frontal em quatro alturas e medidas de largura por altura para detectar regressões estruturais. O workflow publica esse relatório junto ao `.blend`, `.fbx` e às nove imagens no artefato `necromancer-character-0-9-0-tailored-cloth`.

**Inspeção necessária:** verificar a largura real do quadril, o caimento das coxas, alinhamento da barra com a panturrilha, e a projeção dos bordados. O sucesso do CI não equivale a uma aprovação visual. Ainda não existe retopologia deformável, armature ou animação; o jogador Unity deve permanecer inalterado.

### Validação final da 0.9.0
A execução [42517395267](https://github.com/Takeo-Ishikawa/necromancer-overworld/actions/runs/42517395267) do commit `152e53e6` concluiu com **success**: todas as etapas 0.8.3–0.9.0, exportação .blend/.fbx, nove imagens de inspeção, métricas JSON e publicação do pacote `necromancer-character-0-9-0-tailored-cloth`. A etapa 0.9.0 passou pelos testes de continuidade frontal e cintura/quadril. O tecido final tem **21.568 vértices e 21.566 faces**. Amostras de superfície frontal no centro (em metros, eixo Y): z=0,765 → -0,14409; z=0,825 → -0,15439; z=0,885 → -0,15946; z=0,945 → -0,15878. As medidas verificam continuidade geométrica, mas não fidelidade artística.

Uma primeira prévia revelou duas costuras escuras artificiais nas coxas e ondulações horizontais frequentes. O estágio foi revisado para retirar essas costuras, reduzir as amplitudes de ondas no gerador 0.8.9 e afinar as barras, validando nova execução do CI. Na prévia final, a cintura ficou um pouco menos inflada, a bolsa direita é mais discreta e o contraste do tecido está mais suave, mas as calças ainda têm caimento geométrico e franzidos repetitivos. A semelhança com a referência original continua **insuficiente para aprovação de personagem final**. Próximos alvos: anatomia global e cabeça/rosto/cabelo com abordagem artística mais apropriada, além de melhor caimento do tecido; adiar rigging e integração Unity.
