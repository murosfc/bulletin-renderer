# Automação do Boletim Semanal

Fluxo completo, do upload no Firebase até o deploy na Vercel, sem intervenção manual:

```
Upload semanal do PDF → Firebase (onDocumentCreated no projeto ipmacae)
    └─ chamada HTTPS: repository_dispatch neste repositório (evento "novo-boletim")
          └─ GitHub Action (.github/workflows/boletim.yml):
               baixa o PDF → Claude Code segue UPDATE.md → valida com screenshots
                    └─ commit + push na main → Vercel deploya automaticamente
```

## Lado GitHub (este repositório) — já implementado

- `.github/workflows/boletim.yml`: workflow disparado por `repository_dispatch`
  (tipo `novo-boletim`, payload `{ "pdf_url": "..." }`) ou manualmente via
  `workflow_dispatch` para testes.
- As capturas de tela da validação ficam disponíveis como artifact
  (`validacao-boletim`) em cada execução, junto com um `RESUMO.md` do que mudou.
- Antes do commit, `scripts/validate_boletim.py` confere a assinatura do PDF,
  os campos essenciais do JSON e todos os assets referenciados pelo HTML.
  Quando algo falha, o commit e o deploy são bloqueados.

- Se a assinatura Claude estiver no limite de uso (429/529), o passo do Claude
  tenta de novo a cada 15 min por até ~5h (o reset da janela de 5h). O PDF já
  foi baixado no início, então o link assinado expirar não atrapalha.

**Secret necessário no repositório** (Settings → Secrets and variables →
Actions):

- `CLAUDE_CODE_OAUTH_TOKEN`: usa a assinatura Claude Pro/Max existente (e
  divide o limite de uso com ela). Gere o token na sua máquina com
  `claude setup-token` e cole o valor no secret.

## Lado Firebase (projeto ipmacae) — código para integrar

Adicionar ao código das functions (2ª geração, Node 18+). Ajuste o caminho da
collection e o campo que guarda o caminho do PDF no Storage conforme o seu
projeto:

```js
const { onDocumentCreated } = require("firebase-functions/v2/firestore");
const { defineSecret } = require("firebase-functions/params");
const { getStorage } = require("firebase-admin/storage");

const githubPat = defineSecret("GITHUB_PAT");

exports.onBoletimCreated = onDocumentCreated(
  { document: "boletins/{id}", secrets: [githubPat] },
  async (event) => {
    const data = event.data.data();

    // Campo com o caminho do arquivo no Storage, ex.: "boletins/2026-07-12.pdf"
    const storagePath = data.storagePath;
    if (!storagePath) {
      console.error("Documento sem storagePath; nada a fazer.");
      return;
    }

    // URL assinada válida por 1h — o workflow baixa o PDF em segundos
    const [pdfUrl] = await getStorage()
      .bucket()
      .file(storagePath)
      .getSignedUrl({ action: "read", expires: Date.now() + 60 * 60 * 1000 });

    const res = await fetch(
      "https://api.github.com/repos/murosfc/bulletin-renderer/dispatches",
      {
        method: "POST",
        headers: {
          Authorization: `Bearer ${githubPat.value()}`,
          Accept: "application/vnd.github+json",
          "X-GitHub-Api-Version": "2022-11-28",
        },
        body: JSON.stringify({
          event_type: "novo-boletim",
          client_payload: { pdf_url: pdfUrl },
        }),
      }
    );

    if (!res.ok) {
      throw new Error(`GitHub dispatch falhou: ${res.status} ${await res.text()}`);
    }
    console.log("Workflow de atualização do boletim disparado com sucesso.");
  }
);
```

> Se a sua function existente já é a `onDocumentCreated` que processa o upload,
> basta mover o trecho da URL assinada + `fetch` para dentro dela e declarar o
> secret `GITHUB_PAT` nas opções.

**Secret necessário no Firebase:**

```bash
firebase functions:secrets:set GITHUB_PAT
# cole o token quando solicitado, depois:
firebase deploy --only functions
```

O token deve ser um **fine-grained personal access token** do GitHub com acesso
apenas ao repositório `murosfc/bulletin-renderer` e permissão
**Contents: Read and write** (é o que o endpoint `dispatches` exige).

## Como testar

1. **Só o workflow (sem Firebase):** aba Actions → "Atualizar Boletim" →
   "Run workflow" → cole qualquer URL pública/assinada de um PDF de boletim.
2. **Ponta a ponta:** faça o upload semanal normalmente e acompanhe a execução
   na aba Actions; ao final, confira o commit na main e o deploy da Vercel.

## Alerta de falha

Quando a atualização falha de vez (depois das novas tentativas), o workflow:

- abre ou comenta a issue `🚨 Falha na atualização automática do boletim`
  (label `automacao`);
- manda um push para todos os usuários `superUser` do app IP Macaé, pela
  Cloud Function `notifyBulletinRenderFailure` do projeto `ipmacae-app`
  (código em `functions/src/notify-bulletin-render-failure.f.ts` no repo
  ipmacae). Não há secret: o workflow envia um token OIDC do GitHub
  (permissão `id-token: write`) e a function confere a assinatura e que o
  token veio do `boletim.yml` deste repositório.

## Solução de problemas

- **Push recusado no workflow:** verifique se a branch `main` tem proteção
  bloqueando o bot; se tiver, permita o `github-actions[bot]` ou troque o passo
  final para abrir PR.
- **Function retorna 404 no dispatch:** o PAT não tem acesso ao repositório ou
  expirou.
- **Extração ruim em alguma edição:** o artifact `validacao-boletim` contém o
  `RESUMO.md` e as capturas para diagnosticar; o conteúdo bruto fica sempre em
  `data/boletim.json` → `rawPages`.
