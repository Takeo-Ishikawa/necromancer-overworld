# Compilação para Windows (x64)

Workflow: `.github/workflows/windows-preview.yml`.

A compilação usa o Unity 2022.3.62f2 e GameCI em um runner Linux para produzir um executável **Windows x64**, sem necessidade de um runner Windows. O método `OverworldWindowsBuild.BuildWindows` recria a mesma cena utilizada pelo APK e exporta o jogo em `build/StandaloneWindows64/`.

## Como compilar

1. Abra a aba **Actions** do repositório e selecione **Necromancer Overworld Windows EXE**.
2. Clique em **Run workflow**, selecione `main` e execute. O workflow também dispara em alterações de `unity/**`.
3. Quando terminar, abra a execução e baixe o artefato `necromancer-overworld-windows-x64`.
4. Extraia o ZIP completo e execute `NecromancerOverworld.exe` no Windows 64 bits. **Não mova apenas o EXE:** a pasta `NecromancerOverworld_Data` e eventuais DLLs devem permanecer ao lado dele.

## Requisitos e notas

- Reutiliza os mesmos secrets `UNITY_LICENSE`, `UNITY_EMAIL`, `UNITY_PASSWORD` e opcionalmente `UNITY_SERIAL` do workflow Android. Não precisa de keystore Android.
- O Unity Windows Standalone é gerado com backend Mono; o Android continua usando IL2CPP ARM64. Isso reduz o custo de compilação do protótipo desktop.
- O projeto não usa assinatura de código Windows. O SmartScreen pode exibir um aviso em máquinas que não reconhecem o executável.
- O build Windows não altera o workflow Android nem a versão 2D original.
- O ZIP é um artefato do GitHub Actions; não é um instalador.
- O método de build foi adicionado ao repositório, mas a execução ainda precisa ser validada nos logs do GitHub Actions.
