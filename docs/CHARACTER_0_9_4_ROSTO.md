# Necromancer Overworld — 0.9.4: escultura facial adulta

## Origem e continuidade

A versão 0.9.4 não importa um novo personagem genérico: executa a construção da 0.9.3 em modo `NECROMANCER_093_BUILD_ONLY` e altera os vértices da malha original **Blender Studio Human Base Meshes v1.4.1 — Body Male Stylized (CC0)**. Contagens anatômicas obrigatórias: **12.502 vértices e 12.500 faces**. O arquivo `sculpt_character_093.py` permanece funcional autonomamente e a nova versão está em `sculpt_character_094.py`. O projeto Unity não é alterado.

## Mudanças da 0.9.4

1. Rosto: redução localizada das maçãs arredondadas, mandíbula mais angulada, queixo definido e relevo de nariz, com deformações contínuas nos vértices originais, sem voxel/remesh ou cabeça de primitivas.
2. Olhos: redução adicional da abertura ocular e dimensionamento dos **dois olhos originais** do CC0. As quatro superfícies de íris/pupila foram reposicionadas sobre os olhos alterados para evitar elementos flutuando.
3. Orelhas: aproximação das orelhas ao crânio e ligeira redução da altura, com registro do número de vértices afetados.
4. Sobrancelhas: substituição das duas linhas finas da 0.9.3 por duas pequenas malhas de faixa progressivamente afilada, ancoradas por raycast à superfície da testa. Os traços das pálpebras continuam em curvas editáveis.
5. Materiais: pele com tonalidade pálida fria e cabelo menos brilhante, mantendo os objetos de cabelo e vestuário separados.

## Inspeção programada

O workflow `.github/workflows/anatomical-character-preview.yml` usa Blender 4.5.15 LTS no GitHub Actions. Exporta `necromancer_character_094.blend` e `necromancer_character_094.fbx`, JSON de contagens e **nove renders reais**: frente, perfil, costas, três-quartos, rosto frontal, rosto três-quartos, rosto perfil, detalhe dos olhos e detalhe da calça. O estágio de Blender permanece editável; curvas são convertidas em geometria somente para FBX.

Validações: mesmas 12.502/12.500 contagens de corpo, deformação efetiva de rosto/orelha, dois olhos CC0, quatro objetos de íris/pupila e duas malhas de sobrancelha. O CI não substitui avaliação artística. **A folha visual aprovada ainda não está versionada neste repositório, logo a fidelidade exata não pode ser atestada.**

Status artístico: **não aprovado por padrão**. Não realizar merge ou substituir o protagonista jogável até inspeção e aprovação.

## Execuções e avaliação visual

### Execução inicial

- [42546868308](https://github.com/Takeo-Ishikawa/necromancer-overworld/actions/runs/42546868308) — sucesso técnico, nove PNGs produzidos. **Inspeção visual reprovou o primeiro passe:** bochechas e mandíbula lateral ficaram excessivamente largas; sobrancelhas eram placas espessas. O novo perfil também evidenciou nariz/lábios pouco naturais e cobertura rígida do cabelo na nuca.

### Correção e resultado do segundo passe

- [42547235335](https://github.com/Takeo-Ishikawa/necromancer-overworld/actions/runs/42547235335) — **sucesso verificado**.
- Artefato: `necromancer-anatomical-0-9-4-cc0-preview`, ID **13643638980**, ZIP contendo projeto `.blend`, `.fbx`, nove imagens de inspeção, catálogo de assets e metadados de procedência.
- Corpo preservado: **12.502 vértices / 12.500 faces**, exatamente antes e depois da escultura; deformados **3.497 vértices** na malha, sendo **142** localizados na região das orelhas.
- Dois olhos de origem CC0 presentes; altura de cada malha ocular reduzida de **0,05596 m** para **0,04029 m** neste passe, com quatro objetos de íris/pupila reancorados.
- Duas sobrancelhas reconstruídas como malhas separadas, com espessura reduzida após inspeção.
- **485 mechas** e **2.926 quads de calça** herdados da versão 0.9.3, mantendo componentes editáveis. `unity/` intocado, sem rigging ou animações.

### Avaliação artística das imagens reais

- A frente e a vista três-quartos mostram olhos proporcionalmente menores, orelhas mais discretas e sobrancelhas menos espessas do que no primeiro passe 0.9.4.
- A segunda correção reduziu as bochechas excessivamente largas que o primeiro passe introduziu.
- **O rosto permanece juvenil e não corresponde ainda à identidade visual do necromante masculino aprovado.** Lábios e nariz permanecem arredondados, queixo e mandíbula têm transições artificiais, e a região das pálpebras ficou excessivamente escura.
- A vista de perfil mostra que o cabelo ainda tem uma cobertura geométrica rígida na nuca, com mechas aparentando fitas, não cabelo natural.

**Decisão:** manter versão 0.9.4 como experimento intermediário tecnicamente validado, **não aprovado artisticamente**. A próxima intervenção não deve ser outro conjunto pequeno de deslocamentos genéricos: requer redefinição dirigida dos volumes faciais (nariz, boca, maçã, órbita e mandíbula) com inspeção simultânea em frente/perfil/três-quartos, e reconstrução da implantação posterior do cabelo a partir da referência real. O render da obra aprovada não está versionado no repositório; não se pode garantir semelhança. PR permanece em rascunho e Unity preservado.

