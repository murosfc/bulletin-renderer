# Guia de Atualização do Boletim Semanal (Instruções para a IA)

Olá! Este arquivo serve como instrução detalhada para você (IA) atualizar esta landing page quando o usuário adicionar um novo arquivo `boletim.pdf` na raiz do projeto.

Siga os passos abaixo cuidadosamente para ler o novo PDF e remontar a landing page mantendo o design moderno e premium já estabelecido.

---

## 📋 Passos para Atualização

### Passo 1: Extração de Conteúdo do PDF
1. O usuário irá substituir o arquivo `boletim.pdf` na raiz.
2. Execute um script Python simples em segundo plano para extrair todo o texto e imagens do PDF. Você pode gerar um script temporário na pasta de scratch do seu ambiente com este conteúdo:
   ```python
   import pypdf
   import os
   
   # Extrair texto
   reader = pypdf.PdfReader("boletim.pdf")
   with open("scratch_extracted_text.txt", "w", encoding="utf-8") as f:
       for i, page in enumerate(reader.pages):
           f.write(f"=== PAGE {i+1} ===\n")
           f.write(page.extract_text() or "")
           f.write("\n\n")
   ```
3. O script padrão do repositório (`scripts/generate_boletim_json.py`) também pode ser rodado para extrair as imagens automaticamente para a pasta `assets/boletim-images/`. As imagens extraídas serão:
   - `page-02-img-01.jpg` a `page-02-img-NN.jpg` (Fotos congregacionais da Vida em Comunidade).
   - `page-03-img-03.jpg` (Foto de grupo do Desperta Déboras ou outro ministério específico).

### Passo 2: Leitura e Análise do Conteúdo
Abra o arquivo de texto extraído (`scratch_extracted_text.txt`) e identifique as seguintes partes estruturais:
1. **Metadados**:
   - Número da edição (ex: "Nº 1880").
   - Data do boletim (ex: "Domingo, 05 de julho de 2026").
2. **Mensagem Pastoral / Sermão**:
   - Título da mensagem (em caixa alta).
   - Passagem bíblica de referência (ex: "Marcos 4:35-41").
   - Nome do autor (geralmente começa com "Rev.").
   - Parágrafos do corpo do texto (leia os blocos sem alterar o conteúdo textual).
   - Versículo em destaque ao final (com citação do livro/capítulo/versículo, ex: "Provérbios 3:5-6").
3. **Agenda Semanal**:
   - Identifique os dias e horários da semana.
   - **ATENÇÃO especial a avisos ou cancelamentos** (ex: "Excepcionalmente não teremos culto"). Se houver, adicione a classe CSS `cancelled` na respectiva linha da agenda no HTML.
4. **Aniversariantes**:
   - Associe corretamente as datas com os nomes dos aniversariantes daquela semana (às vezes a extração do PDF coloca em colunas, certifique-se de alinhar cada pessoa à sua data correta).
5. **Pedidos de Oração**:
   - Liste todos os nomes citados sob "Ore por esses irmãos".
6. **Dados de Contribuição e Liderança**:
   - Chave PIX (CNPJ ou conta).
   - Nomes da liderança local (Pastores, Presbíteros e Diáconos).
7. **Escala de Serviços**:
   - Equipes de Louvor e Junta Diaconal escaladas para o domingo corrente e o próximo.

### Passo 3: Atualização do HTML
1. Edite o arquivo [index.html](file:///f:/bulletin-renderer/index.html). **Não modifique as classes CSS ou a estrutura de tags gerais**, pois elas definem o estilo moderno da página.
2. Substitua o conteúdo das seguintes seções com os novos dados:
   - Metadados do cabeçalho (`edition-meta`).
   - Título e passagem no Hero.
   - Corpo do sermão (preservando o primeiro caractere estilizado como *drop cap* no primeiro parágrafo).
   - Versículo em destaque no bloco `sermon-verse-box`.
   - Grid de aniversariantes da semana.
   - Linhas do cronograma da Agenda Semanal.
   - Galeria de imagens `gallery-grid` (verifique quantas imagens foram extraídas no passo 1 e insira as tags correspondentes com `data-src` apontando para `assets/boletim-images/page-02-img-XX.jpg`).
   - **Legendas das Fotos em formato de badge (SEMPRE VERIFICAR)**: As fotos da galeria costumam ter uma legenda associada no layout original do PDF (ex.: "Célula 19", "Célula 05" abaixo de cada foto), que normalmente **não** vem embutida na imagem extraída — ela é um texto solto na página, capturado separadamente em `rawPages`/`community.summary` no JSON. Quando existir essa legenda, insira um `<div class="gallery-item-footer">Célula NN</div>` logo após a tag `<img>` dentro de cada `.gallery-item` — o CSS já renderiza isso como um badge escuro sempre visível no canto inferior esquerdo da foto (não é um efeito de hover). **Se a página não tiver nenhuma legenda associada às fotos, não insira `gallery-item-footer` nenhum** (não invente legendas genéricas).

     ⚠️ **NÃO assuma que a ordem das legendas no texto extraído (`rawPages`) bate com a ordem sequencial dos arquivos `page-02-img-01`, `-02`, `-03`...** — já testamos isso na edição 1884 e as duas ordens de extração (texto do PDF e `page.images` do pypdf) vêm **embaralhadas** em relação à posição visual real da foto na página. Associar por ordem sequencial gera legenda errada silenciosamente (foi o motivo do commit `0b9328b` ter removido todas as legendas antes). O único método confiável é casar cada legenda com sua foto pela **posição geométrica real** no PDF, assim:

     1. Renderize a página em questão (normalmente página 2) como imagem para enxergar o grid real e a ordem visual das legendas (topo→baixo, esquerda→direita). Use PyMuPDF (`pip install pymupdf` se não estiver instalado):
        ```python
        import fitz  # pip install pymupdf
        doc = fitz.open("boletim.pdf")
        page = doc[1]  # página 2 (índice 0-based)
        page.get_pixmap(dpi=150).save("scratch_page2.png")
        ```
        Abra `scratch_page2.png` com o Read tool e leia visualmente qual legenda fica sob qual foto, na ordem de leitura (linha a linha, esquerda para direita).
     2. Pegue a posição (bounding box) e as dimensões em pixel de cada imagem da mesma página:
        ```python
        for info in page.get_image_info(xrefs=True):
            print(info["xref"], info["bbox"], info["width"], info["height"])
        ```
        Ordene os resultados por `(y0, x0)` do bbox — essa ordem é a ordem visual real (linha a linha) e deve bater com a lista de legendas lida no passo 1. Isso te dá `xref → legenda`.
     3. Para saber a qual arquivo `page-02-img-XX.jpg` (gerado por `scripts/generate_boletim_json.py`) cada `xref` corresponde, compare as dimensões em pixel: `width`/`height` do `get_image_info` (passo 2) contra `PIL.Image.open(caminho).size` de cada arquivo extraído. As dimensões batem exatamente (mesma imagem, apenas re-extraída por bibliotecas diferentes) e isso resolve a maioria dos casos.
     4. Se duas fotos tiverem exatamente a mesma largura/altura (empate), desambigue recortando a região do `xref` no PNG renderizado no passo 1 (usando o bbox × `dpi/72` como fator de escala) e comparando visualmente essa área com os arquivos candidatos via Read tool.
     5. Só depois de montar o mapeamento completo (`page-02-img-XX.jpg → "Célula NN"`), escreva os `gallery-item-footer` no HTML.
   - Foto e aviso do Ministério Desperta Débora (ou outro ministério que esteja na página 3).
   - Lista de tags dos Pedidos de Oração.
   - Organograma de liderança (verifique se há alterações nos nomes de Pastores, Presbíteros ou Diáconos, e também atualize os Presidentes das Sociedades Internas UPH/SAF/UMP/UPA e o Responsável pelo CETH conforme extraídos do PDF).
   - **Hierarquia de Colunas (Responsividade)**: O arquivo está estruturado em `.main-column` (conteúdo semanal dinâmico) e `.side-column` (informações institucionais estáticas). Mantenha a ordem dos elementos dentro delas para que o fluxo de leitura móvel (mobile) comece com o conteúdo principal e termine com o institucional.
   - **Escala de Serviços**: Atualize a escala de louvor e junta diaconal no bloco `.escala-grid` para o domingo atual e o próximo.
   - **Padding Compacto**: O design utiliza paddings reduzidos (`1.5rem` nos cards principais no desktop, `1.25rem` no mobile e `1rem` em telas estreitas, e `1.25rem` no `.identity-item` interno) para garantir que a página fique elegante e compacta. Não altere estes valores sem necessidade.
   - **Atenção ao Botão de Copiar PIX**: O botão deve permanecer no formato de botão de ícone (contendo as tags `<svg>` da classe `icon-copy` e `icon-check`). Não insira texto dentro do botão, pois isso causa quebra de linha no CNPJ.
   - **Atenção ao Card de Contribuição**: O card `.pix-card` deve possuir um gradiente de fundo escuro fixado no CSS para manter a legibilidade do texto branco tanto no tema claro quanto no tema escuro.

### Passo 4: Validação
1. Inicie o servidor HTTP local na porta 5500:
   ```powershell
   python -m http.server 5500
   ```
2. Abra o navegador usando o agente do browser para verificar:
   - Se o layout está perfeitamente alinhado.
   - Se o botão de copiar a chave PIX funciona.
   - Se o lightbox de imagens carrega e fecha normalmente.
   - **Se houver legendas de célula**: tire um screenshot da `.gallery-section` (ex.: com Playwright, já que não há `chromium-cli` neste ambiente Windows) e compare badge a badge com o PNG renderizado do PDF no Passo 3 — cada legenda precisa estar sobre a foto certa, não só "presente".
3. Apresente o resultado final e as capturas de tela para o usuário.

### Diretriz Permanente de Leitura no Mobile
- Em telas menores, mantenha o padding dos cards mais compacto para melhorar a leitura.
- Referência atual de layout: em até 768px use `padding: 1.75rem` em `.card`; em até 480px use `padding: 1.25rem`.
- Evite voltar para padding amplo no mobile (ex.: `2.5rem`), pois prejudica o conforto visual do conteúdo textual.
