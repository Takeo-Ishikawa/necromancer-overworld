# Necromancer Overworld — 0.9.2 | Identidade visual em malha CC0

## Escopo implementado

Este passe deriva o corpo original Body Male – Stylized da Blender Studio Human Base Meshes v1.4.1 (CC0), por meio do importador 0.9.1, agora reutilizável com NECROMANCER_IMPORT_ONLY=1. A topologia original de vértices/quads permanece intacta, sem retorno ao gerador de primitivas das versões 0.8.x.

Script: tools/blender/anatomical/sculpt_character_092.py
Workflow: .github/workflows/anatomical-character-preview.yml
Branch: feature/necromancer-anatomy-092
Artefato esperado: necromancer-anatomical-0-9-2-cc0-preview

Progresso técnico:

1. Silhueta mais atlética: ombros, peitoral, cintura, deltoides e pernas deformados de modo suave e simétrico na malha-base; relevos peitoral/abdominal e dorsal.
2. Rosto: mandíbula mais angular, supercílios e íris discretas projetadas na anatomia existente; ainda é uma avaliação inicial de identidade facial.
3. Cabelo: couro cabeludo extraído dos polígonos existentes e 196 mechas em tiras afiladas, com variação de orientação e tom cinza-prateado/lilás. O resultado ainda não substitui um groom artístico dedicado.
4. Roupa: calça escura e braçadeiras extraídas de polígonos anatômicos, folgas e dobras; linhas douradas projetadas na superfície real.
5. Acessórios independentes: cinto, fivela, duas bolsas e fechos. Peito descoberto e pés descalços.
6. Seis imagens reais de inspeção: frente, perfil, costas, três-quartos e dois close-ups do rosto.

## Verificação

O workflow exige preservar as contagens de faces/vértices da base, gerar calça, braçadeiras, scalp, cabelo e seis imagens. O JSON registra fonte, contagens e limitações. O .blend contém curvas de bordado editáveis; apenas no estágio de exportação FBX as curvas são convertidas em geometria.

## Condição de aprovação

**Status: avaliação visual pendente.** Não há folha de referência original versionada no repositório. Conferir cabeça, cabelo, ombros, proporção pernas/tronco, olhos, bordados e roupas nas imagens antes de considerar aprovado. A automação não substitui escultura artística de alta fidelidade.

Nenhum arquivo de unity/ é modificado. Não há rigging, animações ou substituição do personagem jogável.

## Verificação real no GitHub Actions

- Primeiro passe: execução 42527808118 — sucesso, mas as íris ficaram acima dos olhos.
- Segundo passe: execução 42528222390 — sucesso, cabelo estreitado, mas as íris ficaram ocultas atrás dos olhos do asset.
- Terceiro passe: execução [42528534747](https://github.com/Takeo-Ishikawa/necromancer-overworld/actions/runs/42528534747) — **sucesso**, com as íris projetadas corretamente na superfície mais anterior dos objetos anatômicos importados.
- Artefato: necromancer-anatomical-0-9-2-cc0-preview (ID 13636616247, ZIP com .blend, .fbx, seis PNGs e metadados).

As contagens reais lidas de source_metadata.json foram:

- Corpo: 12.502 vértices e 12.500 faces antes e depois do passe, topologia-base preservada.
- Calça: 2.926 faces de casca derivada da malha.
- Braçadeiras: 680 faces no total.
- Scalp: 234 faces.
- Cabelo: 196 mechas, 688 quad faces de fitas.
- Bordados por projeção: 10 curvas.
- Sem rigging; sem troca do personagem jogável no Unity.

### Inspeção visual das seis prévias

Conferidas as imagens reais front, side, back, threequarter, face_front e face_threequarter do último artefato. Resultado técnico consistente: corpo e roupas visíveis, calçado ausente, elementos separados e olhos com pupilas visíveis.

**Problemas artísticos que continuam evidentes e não devem ser confundidos com aprovação:** (1) cabelo tem contorno de scalp excessivamente sólido e mechas ainda artificiais; (2) calças acompanham demais as saliências de joelhos e panturrilhas, parecendo placas ou tecido inflado; (3) rosto e orelhas ainda têm aparência juvenil/genérica em vez de um necromante adulto estilizado; (4) os desenhos dourados são provisórios e não reproduzem a folha de referência ausente do repositório. Para qualidade de personagem de produção, o próximo passe deve privilegiar uma silhueta de alfaiataria própria, groom e escultura facial dirigidos pela arte conceitual real.

Nenhum êxito de CI equivale a aprovação artística.

