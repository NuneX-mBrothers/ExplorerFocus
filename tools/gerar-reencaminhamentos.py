# -*- coding: utf-8 -*-
"""Gera, em docs/, as páginas que o GitHub Pages passa a servir para reencaminhar o site antigo.

O site do ExplorerFocus muda-se para https://intrepidparallel.com/explorerfocus/ (decisão de 06/11/2026, com a 2.2.0).
Quem chegar pelos endereços antigos (https://nunex-mbrothers.github.io/ExplorerFocus/…) vai para a página equivalente
no endereço novo: a portuguesa para a portuguesa, a privacidade para a privacidade.

    docs/index.html, docs/<língua>/index.html, docs/privacy.html, docs/legal.html, docs/dropbox-flow.html
            reencaminham já (meta refresh + location.replace) e dizem ao Google qual é a página verdadeira (canonical).
            A privacidade é a que as versões antigas da app abrem.
    docs/404.html
            qualquer outro endereço antigo que não exista em docs/: troca /ExplorerFocus/ por /explorerfocus/.
    docs/googlee….html
            o ficheiro de verificação da Search Console, para se continuar a ver o endereço antigo durante a mudança.

⛔ Em docs/ vivem TAMBÉM os ficheiros que as instalações da app leem, e que a engenharia lá põe e que têm de responder
   nos mesmos endereços de sempre: o version.json (as atualizações) e a pasta StandAlone/. Este gerador NUNCA apaga
   nada em docs/, e nunca escreve por cima de um ficheiro que não seja seu.
⛔ Sem nada de terceiros nestas páginas: só reencaminham.
⚠ O GitHub Pages só serve docs/ depois de a fonte passar para «main, /docs», o que se faz no dia da 2.2.0, na ordem
  combinada com a engenharia e com o OK de quem publica.

Corre-se da raiz do site:  python tools/gerar-reencaminhamentos.py
"""
import glob
import html as H
import os
import shutil
import sys

sys.stdout.reconfigure(encoding="utf-8")

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOVO = "https://intrepidparallel.com/explorerfocus/"
DOCS = os.path.join(RAIZ, "docs")
NAO_SAO_LINGUAS = {"docs", "tools", "i18n", "fonts", "shots", "dropbox-flow", "StandAlone"}
SOLTAS = ("privacy.html", "legal.html", "dropbox-flow.html")
# o que é da app, e que este gerador nunca toca
DA_APP = ("version.json", "StandAlone")

MODELO = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>ExplorerFocus</title>
<link rel="canonical" href="{url}">
<meta http-equiv="refresh" content="0; url={url}">
<script>location.replace({url_js} + location.search + location.hash);</script>
<style>body{{margin:0;min-height:100vh;display:flex;align-items:center;justify-content:center;background:#0E0F11;color:#e6e6e6;font-family:Segoe UI,system-ui,sans-serif;padding:0 16px}}a{{color:#7aa2ff}}</style>
</head>
<body>
<p>ExplorerFocus has moved to <a href="{url}">{mostrar}</a>.</p>
</body>
</html>
"""

PAGINA_404 = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>ExplorerFocus</title>
<meta name="robots" content="noindex">
<meta http-equiv="refresh" content="0; url={novo}">
<script>
  /* /ExplorerFocus/qualquer/coisa -> https://intrepidparallel.com/explorerfocus/qualquer/coisa */
  var resto = location.pathname.replace(/^\\/ExplorerFocus\\/?/i, "");
  location.replace({novo_js} + resto + location.search + location.hash);
</script>
<style>body{{margin:0;min-height:100vh;display:flex;align-items:center;justify-content:center;background:#0E0F11;color:#e6e6e6;font-family:Segoe UI,system-ui,sans-serif;padding:0 16px}}a{{color:#7aa2ff}}</style>
</head>
<body>
<p>ExplorerFocus has moved to <a href="{novo}">{mostrar}</a>.</p>
</body>
</html>
"""


def escrever(rel, texto):
    if rel.replace("\\", "/").split("/")[0] in DA_APP:
        sys.exit("[ERRO] %s é da app, e este gerador não lhe toca" % rel)
    f = os.path.join(DOCS, rel)
    os.makedirs(os.path.dirname(f), exist_ok=True)
    with open(f, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(texto)


def mostrar(url):
    return H.escape(url.replace("https://", "").rstrip("/"))


def pagina(url):
    return MODELO.format(url=H.escape(url, quote=True), url_js='"%s"' % url, mostrar=mostrar(url))


def main():
    linguas = sorted(d for d in os.listdir(RAIZ)
                     if d not in NAO_SAO_LINGUAS and not d.startswith(".")
                     and os.path.isfile(os.path.join(RAIZ, d, "index.html")))
    escrever("index.html", pagina(NOVO))
    for d in linguas:
        escrever(os.path.join(d, "index.html"), pagina(NOVO + d + "/"))
    for s in SOLTAS:
        if not os.path.isfile(os.path.join(RAIZ, s)):
            sys.exit("[ERRO] falta o %s na raiz do site" % s)
        escrever(s, pagina(NOVO + s))
    escrever("404.html", PAGINA_404.format(novo=H.escape(NOVO, quote=True), novo_js='"%s"' % NOVO, mostrar=mostrar(NOVO)))
    escrever(".nojekyll", "")
    for g in glob.glob(os.path.join(RAIZ, "google*.html")):
        shutil.copyfile(g, os.path.join(DOCS, os.path.basename(g)))
    print("✅ docs/: entrada, %d línguas (%s), %s, 404, verificação da Search Console; os ficheiros da app não se tocam"
          % (len(linguas), " ".join(linguas), ", ".join(SOLTAS)))


if __name__ == "__main__":
    main()
