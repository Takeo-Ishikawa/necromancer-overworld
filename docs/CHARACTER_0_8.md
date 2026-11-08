# Protagonista masculino — versão 0.8

## Referência aprovada
Turnaround enviado pelo usuário em 2026-11-07: homem adulto, corpo musculoso com torso descoberto, cabelo curto grisalho/lilás, calças carvão até a panturrilha com ornamentos dourados, cinto e bolsas de couro, braçadeiras escuras, pés descalços. **Não adicionar** capuz, cajado, túnica, botas ou magia no início do jogo.

## Estado de entrega
Primeira etapa **em andamento**: `tools/blender/generate_necromancer_base.py` cria um *blockout* 3D editável em Blender 4.x e exporta FBX. Corpo, cabelo, roupa e acessórios são objetos separados. **Não é um modelo final fiel ao turnaround**: os volumes são simplificados e ainda faltam escultura anatômica, rosto detalhado, cabelo refinado, topologia adequada à deformação, UV, texturas e esqueleto.

A automação GitHub Actions `Necromancer Character 3D Preview` executa Blender em ambiente isolado, exporta o `.blend` e `.fbx`, renderiza vistas frontal, lateral e posterior e disponibiliza os arquivos como artifact. **A existência do workflow não comprova sua execução bem-sucedida**: verificar o resultado em Actions. Nenhum FBX final foi adicionado ao Unity, e a cena jogável existente permanece inalterada.

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
