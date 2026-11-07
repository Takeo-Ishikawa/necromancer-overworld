# GitHub Actions — primeiro APK Android

Workflow: [Necromancer Overworld Android APK](../.github/workflows/android-preview.yml).

## Configuração necessária

Em **Settings > Secrets and variables > Actions > New repository secret** no repositório `necromancer-overworld`:

1. Configure `UNITY_LICENSE` (licença ULF compatível) **ou** `UNITY_SERIAL` (licença serial), conforme sua modalidade de licença GameCI. Para autenticação serial, podem ser necessários `UNITY_EMAIL` e `UNITY_PASSWORD`.
2. Para permitir **atualizar o mesmo APK instalado** entre builds, configure os quatro secrets de assinatura persistente:
   - `PREVIEW_KEYSTORE_BASE64`: conteúdo binário do keystore convertido em Base64 (sem quebras de linha).
   - `PREVIEW_KEYSTORE_PASSWORD`: senha do keystore.
   - `PREVIEW_KEY_ALIAS`: alias da chave existente no keystore.
   - `PREVIEW_KEY_PASSWORD`: senha da chave (pode ser igual à senha do keystore).
3. Nunca envie o arquivo de chave, a senha ou a licença para o Git ou para esta conversa.

É possível **reutilizar a mesma chave de assinatura** do projeto 2D (sem alterar o aplicativo original), desde que configure os secrets neste repositório também. O identificador do aplicativo é diferente, então as instalações são independentes. Os secrets não são copiados automaticamente entre repositórios.

Se a assinatura persistente não estiver configurada, a Unity tentará assinar com chave de debug, e o APK de uma execução poderá não atualizar o da próxima.

## Executar

Acesse **Actions > Necromancer Overworld Android APK > Run workflow**, escolha `main` e execute. O workflow também dispara em alterações do diretório `unity/`.

O método `OverworldAndroidBuild.BuildAndroid` gera a cena e compila Android com IL2CPP/ARM64. O APK deve aparecer no artefato `necromancer-overworld-preview` se a execução for bem-sucedida. O upload está configurado sem ZIP adicional (`archive: false`); dependendo da interface do GitHub, o download ainda pode ser apresentado como artefato.

## Se houver erro

Abra a execução em Actions e compartilhe a etapa que falhou e o trecho relevante do log (sem secrets). Problemas comuns: licença Unity, importação de pacotes, compilação de C#, suporte Android ou assinatura.

## Validação pendente

O código foi enviado ao GitHub, mas ainda não há confirmação de build concluído, APK instalado ou desempenho em dispositivo real. Não considerar a versão 0.1 pronta para distribuição antes desse teste.


## Falha de autenticação Unity HTTP 401 (run 42415922159)

O diagnóstico confirmou que os secrets `UNITY_LICENSE`, `UNITY_EMAIL` e `UNITY_PASSWORD` estavam presentes, mas o GameCI tentou autenticar pela Unity Cloud, recebeu HTTP 401 e falhou após cinco tentativas. Não houve compilação dos scripts do jogo.

Em `Settings > Secrets and variables > Actions` deste repositório, confira novamente o e-mail e a senha da conta Unity associados à licença. O conteúdo dos secrets não é mostrado após salvar, então substitua os valores se estiverem desatualizados. Não envie senhas ou licença no chat.

Se a conta utiliza outro método de autenticação ou a Unity não aceita login por senha no CI, consulte as instruções atuais de licenciamento do GameCI/Unity e configure um método compatível com seu tipo de licença. A mera presença de `UNITY_LICENSE` não garante ativação nesse workflow. No caso de licença serial, configure `UNITY_SERIAL`, `UNITY_EMAIL` e `UNITY_PASSWORD` juntos.

Depois de ajustar as credenciais, execute novamente o workflow. A checagem preliminar agora detecta secrets ausentes, mas não pode validar senhas sem tentar a autenticação na Unity.

**Observação:** neste run os secrets de assinatura persistente também estavam incompletos, então mesmo com a licença corrigida as atualizações de APK ainda não terão assinatura estável.
