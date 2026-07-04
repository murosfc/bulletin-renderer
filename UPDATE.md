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
   - Foto e aviso do Ministério Desperta Débora (ou outro ministério que esteja na página 3).
   - Lista de tags dos Pedidos de Oração.
   - Organograma de liderança (verifique se há alterações nos nomes de Pastores, Presbíteros ou Diáconos).
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
3. Apresente o resultado final e as capturas de tela para o usuário.
