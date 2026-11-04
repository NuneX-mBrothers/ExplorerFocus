"""O preço do PREMIUM no site, a partir do preçário do servidor (tools/precos.json).

O João, 04/11/2026: no site basta o produto base, a licença de 1 ano para 3 computadores, com o preço normal e o de
lançamento (a data de fim ao lado, e o normal sem riscar). As renovações, os outros planos e os computadores a mais
ficam na app.

Escreve as chaves pr_price e pr_price_vat nos 15 dicionários e o texto inglês na raiz. Depois corre-se o
tools/gerar-linguas.py. Quando o preçário mudar, copia-se o precos.json novo para tools/ e corre-se outra vez.
"""
import json, os, re, sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRECOS = os.path.join(RAIZ, "tools", "precos.json")
INDEX = os.path.join(RAIZ, "index.html")

MESES = {
 "en": "January February March April May June July August September October November December",
 "pt": "janeiro fevereiro março abril maio junho julho agosto setembro outubro novembro dezembro",
 "br": "janeiro fevereiro março abril maio junho julho agosto setembro outubro novembro dezembro",
 "es": "enero febrero marzo abril mayo junio julio agosto septiembre octubre noviembre diciembre",
 "fr": "janvier février mars avril mai juin juillet août septembre octobre novembre décembre",
 "de": "Januar Februar März April Mai Juni Juli August September Oktober November Dezember",
 "it": "gennaio febbraio marzo aprile maggio giugno luglio agosto settembre ottobre novembre dicembre",
 "pl": "stycznia lutego marca kwietnia maja czerwca lipca sierpnia września października listopada grudnia",
 "ru": "января февраля марта апреля мая июня июля августа сентября октября ноября декабря",
 "ar": "يناير فبراير مارس أبريل مايو يونيو يوليو أغسطس سبتمبر أكتوبر نوفمبر ديسمبر",
 "hi": "जनवरी फ़रवरी मार्च अप्रैल मई जून जुलाई अगस्त सितंबर अक्टूबर नवंबर दिसंबर",
}

def data(lingua, iso):
    a, m, d = (int(x) for x in iso.split("-"))
    if lingua in ("zh", "zh-TW", "ja"):
        return "%d年%d月%d日" % (a, m, d)
    if lingua == "ko":
        return "%d년 %d월 %d일" % (a, m, d)
    mes = MESES[lingua].split()[m - 1]
    if lingua in ("pt", "br", "es"):
        return "%d de %s de %d" % (d, mes, a)
    if lingua == "de":
        return "%d. %s %d" % (d, mes, a)
    if lingua == "ru":
        return "%d %s %d г." % (d, mes, a)
    if lingua == "en":
        return "%d %s %d" % (d, mes, a)
    return "%d %s %d" % (d, mes, a)

def preco(lingua, centimos):
    inteiro, resto = divmod(centimos, 100)
    if lingua in ("pt", "es", "fr", "de", "it", "pl", "ru"):
        return "%d,%02d €" % (inteiro, resto)
    if lingua == "br":
        return "€ %d,%02d" % (inteiro, resto)
    return "€%d.%02d" % (inteiro, resto)

FRASE = {
 "en": "Premium for 1 year, on 3 computers: <strong>{norm}</strong>. Launch price until {data}: <strong>{lanc}</strong>.",
 "pt": "Premium por 1 ano, em 3 computadores: <strong>{norm}</strong>. Preço de lançamento até {data}: <strong>{lanc}</strong>.",
 "br": "Premium por 1 ano, em 3 computadores: <strong>{norm}</strong>. Preço de lançamento até {data}: <strong>{lanc}</strong>.",
 "es": "Premium durante 1 año, en 3 ordenadores: <strong>{norm}</strong>. Precio de lanzamiento hasta el {data}: <strong>{lanc}</strong>.",
 "fr": "Premium pour 1 an, sur 3 ordinateurs : <strong>{norm}</strong>. Prix de lancement jusqu'au {data} : <strong>{lanc}</strong>.",
 "de": "Premium für 1 Jahr, auf 3 Computern: <strong>{norm}</strong>. Einführungspreis bis zum {data}: <strong>{lanc}</strong>.",
 "it": "Premium per 1 anno, su 3 computer: <strong>{norm}</strong>. Prezzo di lancio fino al {data}: <strong>{lanc}</strong>.",
 "pl": "Premium na 1 rok, na 3 komputery: <strong>{norm}</strong>. Cena premierowa do {data}: <strong>{lanc}</strong>.",
 "ru": "Premium на 1 год, для 3 компьютеров: <strong>{norm}</strong>. Стартовая цена до {data}: <strong>{lanc}</strong>.",
 "ar": "Premium لمدة سنة واحدة، على 3 حواسيب: <strong>{norm}</strong>. سعر الإطلاق حتى {data}: <strong>{lanc}</strong>.",
 "hi": "Premium 1 साल के लिए, 3 कंप्यूटरों पर: <strong>{norm}</strong>। {data} तक लॉन्च कीमत: <strong>{lanc}</strong>।",
 "zh": "Premium 1 年，3 台电脑：<strong>{norm}</strong>。{data}前的首发价：<strong>{lanc}</strong>。",
 "zh-TW": "Premium 1 年，3 台電腦：<strong>{norm}</strong>。{data}前的首發價：<strong>{lanc}</strong>。",
 "ja": "Premium 1 年・パソコン 3 台：<strong>{norm}</strong>。{data}までの発売記念価格：<strong>{lanc}</strong>。",
 "ko": "Premium 1년, 컴퓨터 3대: <strong>{norm}</strong>. {data}까지 출시 기념가: <strong>{lanc}</strong>.",
}

# O que se diz do IVA segue o «comIva» do preçário. ⏳ Como se mostra é a ADM_IP que decide (MKT_EF-000098).
IVA = {
 False: {"en": "Prices in euros, before VAT.", "pt": "Preços em euros, sem IVA.", "br": "Preços em euros, sem IVA.",
         "es": "Precios en euros, sin IVA.", "fr": "Prix en euros, hors TVA.", "de": "Preise in Euro, zzgl. MwSt.",
         "it": "Prezzi in euro, IVA esclusa.", "pl": "Ceny w euro, bez VAT.", "ru": "Цены в евро, без НДС.",
         "ar": "الأسعار باليورو، دون ضريبة القيمة المضافة.", "hi": "कीमतें यूरो में, VAT के बिना।",
         "zh": "价格以欧元计，不含增值税。", "zh-TW": "價格以歐元計，未含加值稅。", "ja": "価格はユーロ、税抜です。",
         "ko": "가격은 유로, 부가세 별도입니다."},
 True: {"en": "Prices in euros, VAT included.", "pt": "Preços em euros, com IVA.", "br": "Preços em euros, com IVA.",
        "es": "Precios en euros, IVA incluido.", "fr": "Prix en euros, TVA comprise.", "de": "Preise in Euro, inkl. MwSt.",
        "it": "Prezzi in euro, IVA inclusa.", "pl": "Ceny w euro, z VAT.", "ru": "Цены в евро, с НДС.",
        "ar": "الأسعار باليورو، شاملة ضريبة القيمة المضافة.", "hi": "कीमतें यूरो में, VAT सहित।",
        "zh": "价格以欧元计，含增值税。", "zh-TW": "價格以歐元計，含加值稅。", "ja": "価格はユーロ、税込です。",
        "ko": "가격은 유로, 부가세 포함입니다."},
}

def main():
    p = json.load(open(PRECOS, encoding="utf-8"))
    if p.get("moeda") != "EUR":
        sys.exit("⛔ o preçário não está em euros")
    planos = [x for x in p["planos"] if x["plano"] == "1ano"]
    if len(planos) != 1:
        sys.exit("⛔ não há um plano «1ano» no preçário")
    x = planos[0]
    if x["computadores"] != 3:
        sys.exit("⛔ o plano de 1 ano já não é para 3 computadores: a frase tem de mudar")
    textos = {}
    for lingua in FRASE:
        textos[lingua] = {
            "pr_price": FRASE[lingua].format(norm=preco(lingua, x["preco"]), lanc=preco(lingua, x["precoDeLancamento"]),
                                             data=data(lingua, x["lancamentoAte"])),
            "pr_price_vat": IVA[bool(p["comIva"])][lingua]}

    for lingua, t in textos.items():
        caminho = os.path.join(RAIZ, "i18n", lingua + ".js")
        s = open(caminho, encoding="utf-8").read()
        for chave in ("pr_price", "pr_price_vat"):
            linha = '  "%s": %s,' % (chave, json.dumps(t[chave], ensure_ascii=False))
            padrao = re.compile(r'^  "%s": .*,$' % chave, re.M)
            if padrao.search(s):
                s = padrao.sub(lambda _: linha, s, count=1)
            else:
                ancora = re.search(r'^  "pr_soon": .*,$', s, re.M)
                if not ancora:
                    sys.exit("⛔ %s: não encontro o pr_soon" % lingua)
                s = s[:ancora.end()] + "\n" + linha + s[ancora.end():]
        open(caminho, "w", encoding="utf-8", newline="\n").write(s)

    en = textos["en"]
    h = open(INDEX, encoding="utf-8").read()
    bloco = ('      <div class="prem-price">\n'
             '        <p data-i18n-html="pr_price">%s</p>\n'
             '        <p class="prem-price-vat" data-i18n="pr_price_vat">%s</p>\n'
             '      </div>\n\n') % (en["pr_price"], en["pr_price_vat"])
    velho = re.compile(r'      <div class="prem-price">\n.*?\n      </div>\n\n', re.S)
    if velho.search(h):
        h = velho.sub(lambda _: bloco, h, count=1)
    else:
        ancora = "      <!-- Como se obtém vive DENTRO do cartão do Premium"
        if h.count(ancora) != 1:
            sys.exit("⛔ index.html: não encontro o sítio do preço")
        h = h.replace(ancora, bloco + ancora, 1)
    css = ("  .prem-price { margin: 18px 0 0; font-size: 14px; line-height: 1.6; color: var(--fg-1); }\n"
           "  .prem-price p { margin: 0; }\n"
           "  .prem-price strong { color: var(--fg-0); font-weight: 600; }\n"
           "  .prem-price .prem-price-vat { margin-top: 4px; font-size: 12px; color: var(--fg-3); }\n")
    if ".prem-price {" not in h:
        ancora = "  .prem-note strong { color: var(--fg-1); font-weight: 600; }\n"
        if h.count(ancora) != 1:
            sys.exit("⛔ index.html: não encontro o sítio do CSS")
        h = h.replace(ancora, ancora + css, 1)
    open(INDEX, "w", encoding="utf-8", newline="\n").write(h)
    for lingua in ("en", "pt", "de", "ja"):
        print(lingua, "|", textos[lingua]["pr_price"], "|", textos[lingua]["pr_price_vat"])
    print("ok: agora o tools/gerar-linguas.py")

if __name__ == "__main__":
    main()
