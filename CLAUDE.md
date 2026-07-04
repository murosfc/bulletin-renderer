# CLAUDE.md

Objetivo: sempre que um novo arquivo `boletim.pdf` for adicionado na raiz, gerar a mesma experiencia web moderna deste projeto.

## Regras de trabalho

1. Ler `boletim.pdf` e extrair o texto com `scripts/generate_boletim_json.py`.
2. Atualizar somente os dados em `data/boletim.json` (nao alterar o visual sem solicitacao).
3. Preservar o design de `index.html`, `assets/styles.css` e `assets/app.js`.
4. Garantir que a pagina continue responsiva e com as animacoes ativas.
5. Validar localmente com servidor HTTP simples.

## Comandos obrigatorios

```powershell
C:/Python313/python.exe scripts/generate_boletim_json.py
C:/Python313/python.exe -m http.server 5500
```

## Checklist de entrega

- `data/boletim.json` atualizado com base no novo PDF.
- `assets/boletim-images/` regenerado com as imagens incorporadas do PDF.
- Hero com titulo/referencia da mensagem da semana.
- Bloco de agenda e aniversariantes preenchidos quando disponivel.
- Texto integral disponivel em "Referência Completa".
- Galeria "Imagens do Boletim" exibindo os arquivos extraidos.
- Projeto pronto para deploy na Vercel sem build.

## Observacoes

- Se algum trecho vier truncado pela extracao do PDF, manter o conteudo bruto em `rawPages` para nao perder informacao.
- O PDF pode variar de edicao para edicao; priorizar robustez com fallback no frontend.
