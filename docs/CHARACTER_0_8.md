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
