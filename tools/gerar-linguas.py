# -*- coding: utf-8 -*-
"""Gera as páginas por idioma do site do ExplorerFocus.

    /        inglês, a raiz
    /pt/ /de/ /zh/ /fr/ /es/ /ja/ …
             a MESMA página com o texto já traduzido no HTML (não por
             JavaScript), com `lang`, título, descrição e canonical próprios,
             e `hreflang` recíproco entre todas.

⛔ Isto não é conteúdo escrito à mão: é GERADO. Sempre que o texto do site
   mudar, correr outra vez. O `__publicar_site_ExplorerFocus.cmd` já o faz,
   DEPOIS de injectar a versão.

📌 Só gera as línguas cujo dicionário existe em i18n/. Acrescentar uma língua é
   escrever o ficheiro e uma linha no LINGUAS.

⚠ É irmão dos geradores do LogViewer e do mBrothers e traz as lições dos dois:
    · aceita a PRÓPRIA SAÍDA como entrada (corrido 2× dá o mesmo ficheiro);
    · o selector troca-se ANTES de prefixar os caminhos;
    · o `lang` do <html> é a etiqueta BCP-47, nunca o código do dicionário
      (o `br` do Brasil é o BRETÃO em BCP-47);
    · o rótulo do botão fechado sai da MESMA lista que a aberta.

⛔ E uma que é só deste site: injecta `window.EF_FREE` com a palavra do grátis
   daquela língua. O `highlightTiers` marca as palavras PREMIUM e a do grátis
   nas notas de 5 cartões, em JavaScript e não nas traduções; sem essa linha
   caía no literal «Free» e as notas das outras 14 línguas perdiam o link
   **sem a página dar um único sinal**.

Ponto de regresso: a etiqueta `antes-das-urls-por-idioma`.
Corre-se da raiz do site:  python tools/gerar-linguas.py
"""
import datetime
import html as H
import io
import json
import os
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = "https://nunex-mbrothers.github.io/ExplorerFocus/"

# código do dicionário → pasta, rótulo no selector, hreflang, og:locale, bandeira
# ⛔ O `lang` do <html> leva o campo `hreflang`, nunca o código do dicionário.
# ⏭️ As oito que faltam para as 16 da app (br, it, pl, ru, ar, hi, zh-TW, ko)
#    entram aqui, uma linha cada, quando os dicionários existirem.
LINGUAS = [
    ("pt", "pt", "Português",      "pt",      "pt_PT", "pt"),
    ("br", "br", "Português (BR)", "pt-BR",   "pt_BR", "br"),
    ("en", "",   "English (US)",   "en",      "en_US", "us"),
    ("es", "es", "Español",      "es",      "es_ES", "es"),
    ("fr", "fr", "Français",       "fr",      "fr_FR", "fr"),
    ("it", "it", "Italiano",       "it",      "it_IT", "it"),
    ("de", "de", "Deutsch",        "de",      "de_DE", "de"),
    ("pl", "pl", "Polski",         "pl",      "pl_PL", "pl"),
    ("ru", "ru", "Русский",        "ru",      "ru_RU", "ru"),
    ("zh", "zh", "中文 (简体)",    "zh-Hans", "zh_CN", "cn"),
    ("ja", "ja", "日本語",          "ja",      "ja_JP", "jp"),
    ("ko", "ko", "한국어",          "ko",      "ko_KR", "kr"),
]

# A barra de línguas da APP, espelhada: as 16, pela ordem dela, mesmo que
# algumas levem à mesma página enquanto não tiverem dicionário. É a mesma
# ordem e as mesmas etiquetas do LogViewer e do mBrothers.
BARRA_DA_APP = [
    ("pt", "Português",      "pt"),
    ("br", "Português (BR)", "br"),
    ("gb", "English (GB)",   "en"),
    ("us", "English (US)",   "en"),
    ("es", "Español",        "es"),
    ("fr", "Français",       "fr"),
    ("it", "Italiano",       "it"),
    ("de", "Deutsch",        "de"),
    ("pl", "Polski",         "pl"),
    ("ru", "Русский",        "ru"),
    ("sa", "العربية",         "ar"),
    ("in", "हिन्दी",           "hi"),
    ("cn", "中文 (简体)",      "zh"),
    ("tw", "中文 (繁體)",      "zh-TW"),
    ("jp", "日本語",          "ja"),
    ("kr", "한국어",           "ko"),
]

RTL = {"ar"}

# páginas soltas que não são traduzidas mas têm de continuar no sitemap
SOLTAS = ["privacy.html", "dropbox-flow.html"]


def existe(cod):
    return os.path.exists(os.path.join(RAIZ, "i18n", cod + ".js"))


def dicionario(cod):
    """Lido pelo próprio node: 25 KB de literais não se desmontam com regex."""
    js = ("global.window={I18N:{}};require(%s);"
          "process.stdout.write(JSON.stringify(window.I18N[%s]||null));"
          % (json.dumps(os.path.join(RAIZ, "i18n", cod + ".js").replace("\\", "/")),
             json.dumps(cod)))
    r = subprocess.run(["node", "-e", js], capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0 or not r.stdout or r.stdout.strip() == "null":
        sys.exit("⛔ não consegui ler o dicionário %s: %s" % (cod, (r.stderr or r.stdout).strip()[:200]))
    return json.loads(r.stdout)


def traduzir(pagina, d, cod):
    """`data-i18n` (texto), `data-i18n-html` (com HTML lá dentro) e
    `data-i18n-attr` (atributos).
    ⚠ O formato do `data-i18n-attr` deste site é o NOME DO ATRIBUTO sozinho,
      com a chave a vir do `data-i18n` do mesmo elemento — é como a
      `<meta description>` já estava escrita. O do mBrothers é `attr:chave`.
      Aceitam-se os dois, para os geradores poderem convergir."""
    faltas, feitas = [], 0

    def troca(m, escapar):
        nonlocal feitas
        abre, chave, fecha = m.group(1), m.group(3), m.group(5)
        v = d.get(chave)
        if v is None:
            faltas.append(chave)
            return m.group(0)
        feitas += 1
        return abre + (H.escape(v, quote=False) if escapar else v) + fecha

    p_htm = re.compile(r'(<([a-zA-Z][\w-]*)\b[^>]*\bdata-i18n-html="([^"]+)"[^>]*>)(.*?)(</\2>)', re.S)
    p_txt = re.compile(r'(<([a-zA-Z][\w-]*)\b[^>]*\bdata-i18n="([^"]+)"[^>]*>)(.*?)(</\2>)', re.S)
    pagina = p_htm.sub(lambda m: troca(m, False), pagina)
    pagina = p_txt.sub(lambda m: troca(m, True), pagina)

    def troca_attr(m):
        nonlocal feitas
        tag = m.group(0)
        spec = m.group(1)
        pares = []
        if ":" in spec:
            for par in spec.split(";"):
                if ":" in par:
                    a, k = par.split(":", 1)
                    pares.append((a.strip(), k.strip()))
        else:
            mk = re.search(r'\bdata-i18n="([^"]+)"', tag)
            if mk:
                pares.append((spec.strip(), mk.group(1)))
        for attr, chave in pares:
            v = d.get(chave)
            if v is None:
                faltas.append(chave)
                continue
            novo, n = re.subn(r'\b%s="[^"]*"' % re.escape(attr),
                              '%s="%s"' % (attr, H.escape(v, quote=True)), tag, count=1)
            if n:
                tag = novo
                feitas += 1
        return tag

    pagina = re.sub(r'<[a-zA-Z][^>]*\bdata-i18n-attr="([^"]+)"[^>]*>', troca_attr, pagina)

    if faltas:
        sys.exit("⛔ [%s] chaves sem tradução: %s" % (cod, sorted(set(faltas))[:8]))
    return pagina, feitas


def prefixar(pagina):
    """Numa subpasta, os caminhos relativos passam a ../ — menos as âncoras, o
    mailto: e tudo o que já é absoluto. `../` e `./` ficam como estão: são os
    do selector, que já vem escrito relativo à pasta certa."""
    def f(m):
        v = m.group(2)
        if re.match(r'^(https?:|//|#|mailto:|data:|/|\.\./|\./)', v):
            return m.group(0)
        return m.group(1) + "../" + v + m.group(3)
    return re.sub(r'(\s(?:src|href|data-full|poster)=")([^"]+)(")', f, pagina)


def url_de(pasta):
    return BASE + (pasta + "/" if pasta else "")


def bandeira(fl):
    return ('<svg class="lang-fl" viewBox="0 0 20 14" aria-hidden="true">'
            '<use href="#fl-%s"/></svg>' % fl)


def selector(activas, pasta_actual):
    pasta_de = {c: p for c, p, *_ in activas}
    etiqueta_de = {c: h for c, _p, _r, h, _l, _f in activas}
    para = lambda p: (("../" + p + "/") if p else "../") if pasta_actual else ((p + "/") if p else "./")
    cod_actual = next(c for c, p, *_ in activas if p == pasta_actual)
    fl_actual, rot_actual = next(((fl, r) for fl, r, c in BARRA_DA_APP if c == cod_actual),
                                 ("us", "English (US)"))
    itens = []
    for fl, rot, cod in BARRA_DA_APP:
        if cod not in pasta_de:          # sem dicionário ainda → o inglês
            cod = "en"
        marca = ' aria-current="true"' if cod == cod_actual and fl == fl_actual else ""
        itens.append('          <a class="lang-btn" href="%s" lang="%s"%s>%s<span>%s</span></a>'
                     % (para(pasta_de[cod]), etiqueta_de[cod], marca, bandeira(fl), rot))
    return ('      <details class="lang-picker">\n'
            '        <summary class="lang-cur" title="Language">%s<span>%s</span></summary>\n'
            '        <div class="lang-list">\n%s\n        </div>\n'
            '      </details>\n' % (bandeira(fl_actual), rot_actual, "\n".join(itens)))


def uma_vez(pagina, velho, novo, rot):
    n = pagina.count(velho)
    if n != 1:
        sys.exit("⛔ [%s] «%s…» aparece %d vezes" % (rot, velho[:50], n))
    return pagina.replace(velho, novo)


# ── a página de origem ──────────────────────────────────────────────────────
origem = io.open(os.path.join(RAIZ, "index.html"), encoding="utf-8", newline="").read()
nl = "\r\n" if "\r\n" in origem else "\n"
base_lf = origem.replace("\r\n", "\n")

activas = [l for l in LINGUAS if existe(l[0])]
if not activas:
    sys.exit("⛔ não há um único dicionário em i18n/")
print("línguas com dicionário: %s" % ", ".join(c for c, *_ in activas))

m_sel = re.search(r' *<details class="lang-picker"[^>]*>\n(?:.*?\n)*? *</details>\n', base_lf)
if not m_sel:
    sys.exit("⛔ não achei o bloco do selector de línguas")
SEL_ANTIGO = m_sel.group(0)

# ⚠ o padrão apanha a PRÓPRIA SAÍDA: à segunda corrida o cabeçalho já é o novo
m_hl = re.search(r'(?:<!--(?:(?!-->).)*?-->\n)? *<link rel="alternate" hreflang="x-default"[^>]*>\n'
                 r'(?: *<link rel="alternate" hreflang="[a-zA-Z-]+"[^>]*>\n)*', base_lf, re.S)
if not m_hl:
    sys.exit("⛔ não achei o bloco hreflang")
HL_ANTIGO = m_hl.group(0)

m_alt = re.search(r'(?: *<meta property="og:locale:alternate"[^>]*>\n)+', base_lf)
ALT_ANTIGO = m_alt.group(0) if m_alt else None

COMENTARIO = (
    "<!-- Uma porta por lingua. Cada pagina tem canonical propria e hreflang\n"
    "     reciproco; o texto vai JA TRADUZIDO no HTML, sem JavaScript.\n"
    "     As pastas por idioma sao GERADAS por tools/gerar-linguas.py, que o\n"
    "     .cmd de publicar corre DEPOIS de injectar a versao.\n"
    "     Regresso: etiqueta antes-das-urls-por-idioma. -->\n")


def bloco_hreflang(activas):
    l = ['<link rel="alternate" hreflang="x-default" href="%s">' % BASE]
    for cod, pasta, _rot, hl, _loc, _fl in activas:
        l.append('<link rel="alternate" hreflang="%s" href="%s">' % (hl, url_de(pasta)))
    return "\n".join(l)


for cod, pasta, rot, hl, loc, fl in activas:
    d = dicionario(cod)
    pag = base_lf
    url = url_de(pasta)

    direccao = ' dir="rtl"' if cod in RTL else ""
    if pasta:
        pag = uma_vez(pag, '<html lang="en">',
                      '<html lang="%s"%s data-lang-fixa="%s">' % (hl, direccao, cod), cod)
    pag = uma_vez(pag, HL_ANTIGO, COMENTARIO + bloco_hreflang(activas) + "\n", cod)
    pag = uma_vez(pag, '<link rel="canonical" href="%s">' % BASE,
                  '<link rel="canonical" href="%s">' % url, cod)
    pag = uma_vez(pag, '<meta property="og:url" content="%s">' % BASE,
                  '<meta property="og:url" content="%s">' % url, cod)
    pag = uma_vez(pag, '<meta property="og:locale" content="en_US">',
                  '<meta property="og:locale" content="%s">' % loc, cod)
    if ALT_ANTIGO:
        outras = "".join('<meta property="og:locale:alternate" content="%s">\n' % l[4]
                         for l in activas if l[0] != cod)
        pag = uma_vez(pag, ALT_ANTIGO, outras, cod)
    pag = uma_vez(pag, '"url": "%s",' % BASE, '"url": "%s",' % url, cod)

    feitas = 0
    if pasta:
        pag, feitas = traduzir(pag, d, cod)

    # o cabeçalho social reescreve-se SEMPRE, mesmo na raiz: é dali que sai o
    # que aparece nos resultados de pesquisa e nas pré-visualizações
    for padrao, chave in [(r'(<meta property="og:title" content=")[^"]*(")', "page_title"),
                          (r'(<meta property="og:description" content=")[^"]*(")', "page_desc"),
                          (r'(<meta name="twitter:title" content=")[^"]*(")', "page_title"),
                          (r'(<meta name="twitter:description" content=")[^"]*(")', "page_desc")]:
        pag = re.sub(padrao, lambda m: m.group(1) + H.escape(d[chave], quote=True) + m.group(2),
                     pag, count=1)

    # ⛔ Duas linhas que o `prefixar()` NÃO consegue dar: ele arruma `src`/`href`
    #    no HTML e não vê o que está dentro do JavaScript.
    #    EF_FREE  → a palavra do grátis, para o `highlightTiers` marcar as notas
    #               dos cartões (sem ela caía no literal «Free»).
    #    EF_ROOT  → o caminho até à raiz, para o `fetch` do `version.json`. Numa
    #               pasta por idioma um `fetch('version.json')` ia buscar
    #               /pt/version.json e dava 404 — e a página anunciava a versão
    #               e o SHA-256 do fallback, que estão velhos.
    linhas_js = ('<script>window.EF_FREE=%s;window.EF_ROOT=%s;</script>\n'
                 % (json.dumps(d["badge_free"], ensure_ascii=False),
                    json.dumps("../" if pasta else "")))
    pag = re.sub(r'<script>window\.EF_FREE=.*?</script>\n', "", pag)
    pag = uma_vez(pag, "</head>", linhas_js + "</head>", cod)

    # ⛔ o selector troca-se ANTES do prefixar
    pag = uma_vez(pag, SEL_ANTIGO, selector(activas, pasta), cod)
    if pasta:
        pag = prefixar(pag)

    destino = os.path.join(RAIZ, pasta, "index.html") if pasta else os.path.join(RAIZ, "index.html")
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    io.open(destino, "w", encoding="utf-8", newline="").write(pag.replace("\n", nl))
    print("✅ %-6s %s" % (pasta + "/" if pasta else "raiz",
                         ("%d textos" % feitas) if pasta else "inglês, só o cabeçalho"))

# ── sitemap ─────────────────────────────────────────────────────────────────
hoje = datetime.date.today().isoformat()
linhas = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for cod, pasta, *_ in sorted(activas, key=lambda l: l[1]):
    linhas.append('  <url><loc>%s</loc><lastmod>%s</lastmod><changefreq>weekly</changefreq>'
                  '<priority>%s</priority></url>' % (url_de(pasta), hoje, "1.0" if not pasta else "0.8"))
for f in SOLTAS:
    linhas.append('  <url><loc>%s%s</loc><lastmod>%s</lastmod><changefreq>yearly</changefreq>'
                  '<priority>0.3</priority></url>' % (BASE, f, hoje))
linhas.append("</urlset>")
io.open(os.path.join(RAIZ, "sitemap.xml"), "w", encoding="utf-8", newline="").write(nl.join(linhas) + nl)
print("✅ sitemap.xml · %d endereços (%d línguas + %d soltas) · lastmod %s"
      % (len(activas) + len(SOLTAS), len(activas), len(SOLTAS), hoje))
