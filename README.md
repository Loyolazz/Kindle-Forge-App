# Kindle Forge

Conversor visual local para preparar **PDF, CBZ, CBR, ZIP, RAR, 7Z, EPUB com imagens e imagens soltas** para **Kindle, Kobo, PocketBook, Nook, Sony, e-readers genéricos e tablets**.

## Pastas

```text
backend/
  Motor de conversão, API local, testes, histórico e arquivos convertidos.

frontend/
  Interface visual com arrastar-e-soltar, presets, capa, prévia e biblioteca.
```

## Abrir o app

No macOS, você pode dar dois cliques em:

```text
Kindle Forge.command
```

Ou rodar pelo terminal:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -e .
python run.py
```

Depois abra:

```text
http://127.0.0.1:8765
```

## O que já tem

- Conversão em lote de vários arquivos.
- Seleção de pasta inteira pela interface.
- Arrastar-e-soltar de arquivos e pastas.
- Organização de capítulos: arquivos separados, um volume único, ou pasta de imagens por capítulo.
- Pastas mistas com PDFs, CBZ/CBR e imagens na mesma ordem natural do nome.
- Reordenação manual dos arquivos antes de converter: subir, descer, remover, arrastar, ordenar por nome e inverter.
- Mesclagem de PDFs/arquivos em um volume único seguindo a ordem visual da lista.
- Presets: Mangá, Marvel/DC, Manhwa, PDF escaneado, Alta qualidade, Arquivo leve e Auto.
- Divisão automática em partes quando passar do limite configurado, por padrão 200 MB.
- Capa pela primeira página, capa gerada, capa personalizada ou sem capa extra.
- Capa online vinda da busca de metadados.
- Metadados: título, autor, série, volume, editora, idioma e descrição.
- Busca automática de metadados em MangaDex, Google Books e Open Library.
- Prévia processada antes de converter.
- Prévia com capa, original antes do corte, página convertida, detalhe técnico e zoom.
- Progresso visual por etapas durante a conversão.
- Resumo separado de Entrada e Saída ao concluir.
- Histórico local dos arquivos convertidos.
- Botão para limpar o histórico da biblioteca sem apagar os arquivos convertidos.
- Botão para apagar os arquivos convertidos listados na biblioteca.
- Botão para abrir a pasta de saída.
- Botão para abrir o Send to Kindle.

## Dicas de uso

- Para mangá comum: preset **Mangá**.
- Para Marvel, DC e HQ ocidental: preset **Marvel/DC**.
- Para manhwa/webtoon vertical: preset **Manhwa**.
- Se o mangá veio em vários PDFs por capítulo, escolha **Um volume com capítulos** em Organização.
- Se um capítulo veio como várias imagens, escolha **Pasta de capítulo/imagens** ou arraste a pasta inteira.
- Se o arquivo veio sem capa, escolha **Gerar capa** ou **Usar imagem** na seção Capa.
- Para preencher dados automaticamente, digite o nome da série em **Título** e clique em **Buscar metadados**. Ao aplicar um resultado com capa, o app muda para **Capa online**.
- A busca mostra score de confiança e permite aplicar tudo, só a capa ou só a descrição.
- Para mandar ao Kindle, prefira **EPUB** e depois use o botão **Send to Kindle**.

## Organização recomendada

Para montar um volume a partir de capítulos:

```text
One Piece Volume 01/
  One Piece Capitulo 001.pdf
  One Piece Capitulo 002.pdf
  One Piece Capitulo 003/
    001.jpg
    002.jpg
    003.jpg
```

Arraste a pasta inteira e marque **Um volume com capítulos**. O Kindle Forge ordena nomes como `2` antes de `10`, então não precisa renomear tudo manualmente se os arquivos estiverem bem nomeados.

Se a ordem vier errada, como `4.pdf`, `1.pdf`, `2.pdf`, use **Ordenar por nome**, arraste os itens ou use as setas de subir/descer. A conversão em volume único respeita exatamente a ordem exibida na lista.

Para converter capítulos como livros separados, deixe **Cada arquivo vira livro**.

## Suporte a CBR/RAR/7Z

Para CBR/RAR/7Z, instale uma ferramenta de extração. No macOS:

```bash
brew install p7zip
```

## Linha de comando

```bash
cd backend
source .venv/bin/activate
kindle-forge convert "../meu-manga.cbz" --mode manga --format epub --cover generated
```

Exemplo com metadados:

```bash
kindle-forge convert "../volume.cbz" \
  --mode manga \
  --title "Volume 01" \
  --author "Autor" \
  --series "Minha Série" \
  --volume "1" \
  --cover generated \
  --split-size-mb 200
```

## Testes

```bash
cd backend
PYTHONPATH=src python -m unittest discover -s tests
```

## Observações

O perfil padrão continua sendo **Kindle Basic 11 · 1072 x 1448 px**, mas a interface também permite escolher outros leitores. O projeto não remove DRM; use apenas arquivos seus, DRM-free ou que você tenha direito de converter.
