# Necromancer Overworld — versão 0.9.6 | Corte tridimensional e alfaiataria

## Escopo e base

Esta versão continua a partir da anatomia adulta original `Body Male - Realistic` do Blender Studio Human Base Meshes v1.4.1 (CC0). O script `tools/blender/realistic_hero_095/assemble_realistic_hero_095.py` pode ser chamado com `NECROMANCER_095_ASSEMBLY_ONLY=1` para preservar o estágio sem exportações redundantes. A nova implementação fica isolada em `tools/blender/realistic_hero_096/assemble_realistic_hero_096.py`.

**Atenção:** A cabeça, o rosto, o corpo e os dois olhos importados da versão realista não são esculpidos novamente. O novo script calcula SHA-256 das coordenadas (double float) de todos os 10.582 vértices do corpo e dos dois olhos antes e depois da edição. O workflow falha se qualquer posição mudar. A topologia do corpo contém 10.590 faces e permanece igual.

## Mudanças reais no modelo

1. **Cabelo:** as antigas fitas achatadas da 0.9.5 são eliminadas. Novo conjunto de **103 mechas com seção transversal elíptica tridimensional**, agrupadas em coroa, franja, têmporas e nuca. Cada grupo é malha independente, com pontas afiladas e espessura real, além de pequenas curvas de fios discretos editáveis. As raízes são extraídas diretamente da malha scalp derivada da cabeça oficial, com verificação da altura mínima para evitar mechas no pescoço/costas. O resultado ainda é uma aproximação estilizada que exige inspeção.
2. **Calças:** os polígonos da roupa continuam derivados do corpo original e são reajustados por seções de cada perna: redução da aparência arredondada dos joelhos, silhueta mais estreita nas panturrilhas e bainha com folga. A transformação respeita o envelope anatômico com margem para reduzir interseções. Acrescentadas duas curvas sutis de costura dourada nas bainhas.
3. **Editabilidade:** cabelos, underlay, calças e costuras em coleções Blender independentes; bordados e fios continuam curvas no `.blend` e são convertidos temporariamente para malhas na exportação FBX.
4. **Segurança:** nenhuma mudança em `unity/`, nenhum rigging ou animação e nenhum novo rosto. A referência visual aprovada ainda não está versionada no repositório.

## CI e verificações

- Workflow independente: `.github/workflows/realistic-character-preview-096.yml` — Blender 4.5.15 LTS no GitHub Actions.
- Saída: `necromancer_realistic_096.blend`, `necromancer_realistic_096.fbx`, metadados e **oito renders reais**: frente, lado, costas, três-quartos, rosto frontal, rosto três-quartos, detalhe do cabelo traseiro e detalhe da calça.
- O sucesso do CI prova apenas que geometrias, exportações e invariantes foram produzidos. A qualidade artística deve ser julgada pelas imagens reais e confrontada com o conceito quando disponível.

## Execução e parecer visual

Pendente de registro após execução e inspeção dos PNGs. O PR permanece em rascunho e o protagonista de Unity não é substituído.
