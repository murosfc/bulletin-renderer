# Boletim Renderer

Projeto web estatico para converter `boletim.pdf` em uma pagina moderna, com animacoes e layout responsivo.
O processo tambem extrai as imagens incorporadas no PDF para exibi-las na pagina.

## Como atualizar para um novo boletim (Via IA)

Para atualizar a landing page com o novo boletim semanal utilizando uma Inteligência Artificial (como o Antigravity):

1. Substitua o arquivo `boletim.pdf` na raiz do projeto pelo novo arquivo PDF.
2. Abra o chat com o agente de IA e peça:
   > *"Atualize a landing page com o novo boletim.pdf de acordo com as instruções em UPDATE.md"*
3. O agente irá ler o novo PDF, extrair as novas fotos congregacionais, organizar os aniversariantes/agenda e remontar o `index.html` mantendo o design intacto.
4. Veja as diretrizes completas no arquivo [UPDATE.md](file:///f:/bulletin-renderer/UPDATE.md).

### Testar localmente

Abra um servidor HTTP simples:
```powershell
C:/Python313/python.exe -m http.server 5500
```
E acesse `http://localhost:5500`.

## Deploy na Vercel

1. Importe este repositório na Vercel.
2. Framework preset: `Other`.
3. Build command: vazio.
4. Output directory: `.`
5. Deploy.

## Estrutura

- `index.html`: página principal (landing page estática moderna).
- `assets/styles.css`: folha de estilos premium com o design system da igreja.
- `assets/app.js`: interações do frontend (lightbox de imagens e cópia rápida do PIX).
- `UPDATE.md`: instruções de atualização detalhadas para agentes de IA.
- `.agents/skills/update_bulletin/`: definição de habilidade integrada para automação de IA.
- `boletim.pdf`: arquivo PDF de entrada com a edição da semana.
- `assets/boletim-images/`: imagens extraídas do boletim atual.
- `vercel.json`: configuração de roteamento para Vercel.
