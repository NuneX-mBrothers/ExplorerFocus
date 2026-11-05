"""Os preços do PREMIUM no site, a partir do preçário do servidor (tools/precos.json).

04/11/2026: no site ficam, numa TABELA (o plano, o preço, o preço de lançamento), os três planos, todos para 3 computadores (1 ano, 3 anos e vitalícia), com o preço
normal e o de lançamento ao lado, sem riscar, e a data de fim. As renovações e os computadores a mais ficam na app. A
Stripe compara o que se cobra com o que o site mostra; por isso os três planos que se vendem estão à vista.

Escreve as chaves da tabela e o «Preços» do menu (nav_prices) nos 15 dicionários, e o texto inglês na raiz. Depois corre-se o
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
    return "%d %s %d" % (d, mes, a)

def preco(lingua, centimos):
    inteiro, resto = divmod(centimos, 100)
    if lingua in ("pt", "es", "fr", "de", "it", "pl", "ru"):
        return "%d,%02d €" % (inteiro, resto)
    if lingua == "br":
        return "€ %d,%02d" % (inteiro, resto)
    return "€%d.%02d" % (inteiro, resto)

# A frase de cima: para quantos computadores, e até quando vale o lançamento.
INTRO = {
 "en": "Premium, for 3 computers. The launch price is valid until {data}.",
 "pt": "Premium, para 3 computadores. O preço de lançamento vale até {data}.",
 "br": "Premium, para 3 computadores. O preço de lançamento vale até {data}.",
 "es": "Premium, para 3 ordenadores. El precio de lanzamiento vale hasta el {data}.",
 "fr": "Premium, pour 3 ordinateurs. Le prix de lancement est valable jusqu'au {data}.",
 "de": "Premium, für 3 Computer. Der Einführungspreis gilt bis zum {data}.",
 "it": "Premium, per 3 computer. Il prezzo di lancio vale fino al {data}.",
 "pl": "Premium na 3 komputery. Cena premierowa obowiązuje do {data}.",
 "ru": "Premium для 3 компьютеров. Стартовая цена действует до {data}.",
 "ar": "Premium لـ 3 حواسيب. يسري سعر الإطلاق حتى {data}.",
 "hi": "Premium, 3 कंप्यूटरों के लिए। लॉन्च कीमत {data} तक लागू है।",
 "zh": "Premium，适用于 3 台电脑。首发价有效期至{data}。",
 "zh-TW": "Premium，適用於 3 台電腦。首發價有效期至{data}。",
 "ja": "Premium（パソコン 3 台）。発売記念価格は{data}までです。",
 "ko": "Premium, 컴퓨터 3대. 출시 기념가는 {data}까지입니다.",
}
# Os nomes dos planos. ⛔ A vitalícia diz sempre que é a vida do computador.
PLANOS = {
 "en": ("1 year", "3 years", "Lifetime (for as long as each computer lasts)"),
 "pt": ("1 ano", "3 anos", "Vitalícia (enquanto cada computador durar)"),
 "br": ("1 ano", "3 anos", "Vitalícia (enquanto cada computador durar)"),
 "es": ("1 año", "3 años", "De por vida (mientras dure cada ordenador)"),
 "fr": ("1 an", "3 ans", "À vie (tant que chaque ordinateur fonctionne)"),
 "de": ("1 Jahr", "3 Jahre", "Lebenslang (solange jeder Computer hält)"),
 "it": ("1 anno", "3 anni", "A vita (finché dura ciascun computer)"),
 "pl": ("1 rok", "3 lata", "Dożywotnia (dopóki działa każdy komputer)"),
 "ru": ("1 год", "3 года", "Бессрочная (пока служит каждый компьютер)"),
 "ar": ("سنة واحدة", "3 سنوات", "مدى الحياة (طوال عمر كل حاسوب)"),
 "hi": ("1 साल", "3 साल", "आजीवन (जब तक हर कंप्यूटर चले)"),
 "zh": ("1 年", "3 年", "终身（在每台电脑的使用寿命内）"),
 "zh-TW": ("1 年", "3 年", "終身（在每台電腦的使用壽命內）"),
 "ja": ("1 年", "3 年", "無期限（各パソコンが使える限り）"),
 "ko": ("1년", "3년", "평생 (각 컴퓨터를 쓰는 동안)"),
}
LANCAMENTO = {
 "en": "launch price", "pt": "preço de lançamento", "br": "preço de lançamento", "es": "precio de lanzamiento",
 "fr": "prix de lancement", "de": "Einführungspreis", "it": "prezzo di lancio", "pl": "cena premierowa",
 "ru": "стартовая цена", "ar": "سعر الإطلاق", "hi": "लॉन्च कीमत", "zh": "首发价", "zh-TW": "首發價",
 "ja": "発売記念価格", "ko": "출시 기념가",
}
def linha(lingua, nome, norm, lanc):
    dois = "：" if lingua in ("zh", "zh-TW", "ja") else (" : " if lingua == "fr" else ": ")
    return "<strong>%s</strong>%s%s · %s <strong>%s</strong>" % (nome, dois, norm, LANCAMENTO[lingua], lanc)

# O que se diz do IVA segue o «comIva» do preçário. Sem IVA (04/11): o valor sem impostos, e no pagamento
# junta-se o imposto do país de quem compra, que a Stripe calcula. Nunca uma taxa fixa (os 23 % são só de cá).
IVA = {
 False: {"en": "Prices in euros, before taxes. At checkout, the VAT or sales tax of the buyer's country is added.",
         "pt": "Preços em euros, sem impostos. No pagamento, junta-se o IVA, ou o imposto equivalente, do país de quem compra.",
         "br": "Preços em euros, sem impostos. No pagamento, é somado o imposto sobre vendas do país de quem compra.",
         "es": "Precios en euros, sin impuestos. Al pagar, se añade el IVA o el impuesto equivalente del país del comprador.",
         "fr": "Prix en euros, hors taxes. Au paiement, la TVA ou la taxe équivalente du pays de l'acheteur est ajoutée.",
         "de": "Preise in Euro, ohne Steuern. Beim Bezahlen kommt die Mehrwertsteuer oder die entsprechende Steuer des Landes des Käufers hinzu.",
         "it": "Prezzi in euro, tasse escluse. Al pagamento si aggiunge l'IVA, o l'imposta equivalente, del paese di chi acquista.",
         "pl": "Ceny w euro, bez podatków. Przy płatności doliczany jest VAT lub podobny podatek kraju kupującego.",
         "ru": "Цены в евро, без налогов. При оплате добавляется НДС или аналогичный налог страны покупателя.",
         "ar": "الأسعار باليورو، دون الضرائب. عند الدفع تُضاف ضريبة القيمة المضافة أو ضريبة المبيعات في بلد المشتري.",
         "hi": "कीमतें यूरो में, करों के बिना। भुगतान के समय खरीदार के देश का VAT या बिक्री कर जोड़ा जाता है।",
         "zh": "价格以欧元计，不含税。付款时会加上购买者所在国家的增值税或销售税。",
         "zh-TW": "價格以歐元計，未含稅。付款時會加上購買者所在國家的加值稅或銷售稅。",
         "ja": "価格はユーロ、税抜です。お支払い時に、購入される国の付加価値税または売上税が加算されます。",
         "ko": "가격은 유로이며 세금 별도입니다. 결제할 때 구매자 국가의 부가가치세 또는 판매세가 더해집니다."},
 True: {"en": "Prices in euros, VAT included.", "pt": "Preços em euros, com IVA.", "br": "Preços em euros, com IVA.",
        "es": "Precios en euros, IVA incluido.", "fr": "Prix en euros, TVA comprise.", "de": "Preise in Euro, inkl. MwSt.",
        "it": "Prezzi in euro, IVA inclusa.", "pl": "Ceny w euro, z VAT.", "ru": "Цены в евро, с НДС.",
        "ar": "الأسعار باليورو، شاملة ضريبة القيمة المضافة.", "hi": "कीमतें यूरो में, VAT सहित।",
        "zh": "价格以欧元计，含增值税。", "zh-TW": "價格以歐元計，含加值稅。", "ja": "価格はユーロ、税込です。",
        "ko": "가격은 유로, 부가세 포함입니다."},
}


TITULO = {
 "en": "Prices", "pt": "Preços", "br": "Preços", "es": "Precios", "fr": "Tarifs", "de": "Preise", "it": "Prezzi",
 "pl": "Ceny", "ru": "Цены", "ar": "الأسعار", "hi": "कीमतें", "zh": "价格", "zh-TW": "價格", "ja": "料金", "ko": "가격",
}
COLUNAS = {
 "en": ("Plan", "Price", "Launch price"), "pt": ("Plano", "Preço", "Preço de lançamento"),
 "br": ("Plano", "Preço", "Preço de lançamento"), "es": ("Plan", "Precio", "Precio de lanzamiento"),
 "fr": ("Formule", "Prix", "Prix de lancement"), "de": ("Tarif", "Preis", "Einführungspreis"),
 "it": ("Piano", "Prezzo", "Prezzo di lancio"), "pl": ("Plan", "Cena", "Cena premierowa"),
 "ru": ("Тариф", "Цена", "Стартовая цена"), "ar": ("الخطة", "السعر", "سعر الإطلاق"),
 "hi": ("प्लान", "कीमत", "लॉन्च कीमत"), "zh": ("方案", "价格", "首发价"), "zh-TW": ("方案", "價格", "首發價"),
 "ja": ("プラン", "価格", "発売記念価格"), "ko": ("요금제", "가격", "출시 기념가"),
}

CHAVES = ("nav_prices", "pr_prices_h", "pr_price_intro", "pr_th_plan", "pr_th_price", "pr_th_launch",
          "pr_plan_1ano", "pr_plan_3anos", "pr_plan_vida",
          "pr_p_1ano", "pr_l_1ano", "pr_p_3anos", "pr_l_3anos", "pr_p_vida", "pr_l_vida", "pr_price_vat")

def main():
    p = json.load(open(PRECOS, encoding="utf-8"))
    if p.get("moeda") != "EUR":
        sys.exit("⛔ o preçário não está em euros")
    por_plano = {x["plano"]: x for x in p["planos"]}
    for k in ("1ano", "3anos", "vitalicio"):
        if k not in por_plano:
            sys.exit("⛔ falta o plano «%s» no preçário" % k)
        if por_plano[k]["computadores"] != 3:
            sys.exit("⛔ o plano «%s» já não é para 3 computadores: a frase tem de mudar" % k)
    fins = {x["lancamentoAte"] for x in por_plano.values()}
    if len(fins) != 1:
        sys.exit("⛔ os planos têm datas de fim do lançamento diferentes: a frase de cima tem de mudar")
    fim = fins.pop()

    textos = {}
    for lingua in INTRO:
        t = {"nav_prices": TITULO[lingua], "pr_prices_h": TITULO[lingua],
             # o russo já acaba a data em «г.»: sem um segundo ponto (a revisão de 05/11)
             "pr_price_intro": INTRO[lingua].format(data=data(lingua, fim)).replace("г..", "г."),
             "pr_th_plan": COLUNAS[lingua][0], "pr_th_price": COLUNAS[lingua][1], "pr_th_launch": COLUNAS[lingua][2],
             "pr_price_vat": IVA[bool(p["comIva"])][lingua]}
        for sufixo, plano, nome in zip(("1ano", "3anos", "vida"), ("1ano", "3anos", "vitalicio"), PLANOS[lingua]):
            x = por_plano[plano]
            t["pr_plan_" + sufixo] = nome
            t["pr_p_" + sufixo] = preco(lingua, x["preco"])
            t["pr_l_" + sufixo] = preco(lingua, x["precoDeLancamento"])
        textos[lingua] = t

    for lingua, t in textos.items():
        caminho = os.path.join(RAIZ, "i18n", lingua + ".js")
        s = open(caminho, encoding="utf-8").read()
        s = re.sub(r'^  "pr_price": .*,\n', "", s, flags=re.M)          # a chave de uma linha só, que nunca saiu
        s = re.sub(r'^  "pr_price_[a-z0-9]+": .*,\n', "", s, flags=re.M)
        s = re.sub(r'^  "(nav_prices|pr_prices_h|pr_th_[a-z]+|pr_plan_[a-z0-9]+|pr_[pl]_[a-z0-9]+)": .*,\n', "", s, flags=re.M)
        ancora = re.search(r'^  "pr_soon": .*,$', s, re.M)
        if not ancora:
            sys.exit("⛔ %s: não encontro o pr_soon" % lingua)
        novas = "".join('\n  "%s": %s,' % (c, json.dumps(t[c], ensure_ascii=False)) for c in CHAVES)
        s = s[:ancora.end()] + novas + s[ancora.end():]
        open(caminho, "w", encoding="utf-8", newline="\n").write(s)

    en = textos["en"]
    h = open(INDEX, encoding="utf-8").read()
    h = re.sub(r'      <div class="prem-price">\n.*?\n      </div>\n\n', "", h, flags=re.S)   # o de dentro do cartão
    linhas = "".join(
        '        <tr><td data-i18n="pr_plan_%s">%s</td><td data-i18n="pr_p_%s">%s</td>'
        '<td class="lanc" data-i18n="pr_l_%s">%s</td></tr>\n' % (k, en["pr_plan_" + k], k, en["pr_p_" + k], k, en["pr_l_" + k])
        for k in ("1ano", "3anos", "vida"))
    bloco = ('  <div class="prem-prices" id="prices">\n'
             '    <h3 data-i18n="pr_prices_h">%s</h3>\n'
             '    <p data-i18n="pr_price_intro">%s</p>\n'
             '    <table class="price-table">\n'
             '      <thead><tr><th data-i18n="pr_th_plan">%s</th><th data-i18n="pr_th_price">%s</th>'
             '<th data-i18n="pr_th_launch">%s</th></tr></thead>\n'
             '      <tbody>\n%s      </tbody>\n'
             '    </table>\n'
             '    <p class="prem-price-vat" data-i18n="pr_price_vat">%s</p>\n'
             '  </div>\n\n') % (en["pr_prices_h"], en["pr_price_intro"], en["pr_th_plan"], en["pr_th_price"],
                                en["pr_th_launch"], linhas, en["pr_price_vat"])
    velho = re.compile(r'  <div class="prem-prices" id="prices">\n.*?\n  </div>\n\n', re.S)
    if velho.search(h):
        h = velho.sub(lambda _: bloco, h, count=1)
    else:
        ancora = '  <p class="prem-idea" data-i18n-html="pr_idea3">'
        if h.count(ancora) != 1:
            sys.exit("⛔ index.html: não encontro o sítio da tabela")
        h = h.replace(ancora, bloco + ancora, 1)
    # «Preços» ao lado do «Premium», no menu de cima e no do rodapé
    for recuo in ("      ",):
        premium = recuo + '<a href="#premium" data-i18n="nav_premium">Premium</a>\n'
        precos = recuo + '<a href="#prices" data-i18n="nav_prices">%s</a>\n' % en["nav_prices"]
        if h.count(premium) != 2:
            sys.exit("⛔ index.html: o «Premium» do menu não aparece duas vezes")
        if precos not in h:
            h = h.replace(premium, premium + precos)
    css = ("  .prem-prices { margin: 28px 0 0; padding: 22px 24px; background: var(--bg-2); border: 1px solid var(--border-1); border-radius: 12px; }\n"
           "  .prem-prices h3 { margin: 0 0 6px; font-size: 20px; color: var(--fg-0); }\n"
           "  .prem-prices p { margin: 0; font-size: 14px; line-height: 1.6; color: var(--fg-1); }\n"
           "  .price-table { width: 100%; border-collapse: collapse; margin: 14px 0 0; font-size: 15px; }\n"
           "  .price-table th, .price-table td { text-align: start; padding: 10px 12px; border-bottom: 1px solid var(--border-1); }\n"
           "  .price-table th { font-family: var(--font-mono); font-size: 11px; letter-spacing: 0.08em; text-transform: uppercase; color: var(--fg-3); font-weight: 500; }\n"
           "  .price-table td { color: var(--fg-1); }\n"
           "  .price-table td:first-child { color: var(--fg-0); font-weight: 600; }\n"
           "  .price-table td.lanc { color: var(--accent); font-weight: 600; }\n"
           "  .prem-prices .prem-price-vat { margin-top: 10px; font-size: 12px; color: var(--fg-3); }\n")
    h = re.sub(r"^  (\.prem-price|\[dir=\"rtl\"\] \.prem-card \.prem-price|\.prem-card \.prem-price|\.prem-prices|\.price-table)[^\n]*\n", "", h, flags=re.M)
    ancora = "  .prem-note strong { color: var(--fg-1); font-weight: 600; }\n"
    if h.count(ancora) != 1:
        sys.exit("⛔ index.html: não encontro o sítio do CSS")
    h = h.replace(ancora, ancora + css, 1)
    open(INDEX, "w", encoding="utf-8", newline="\n").write(h)
    for lingua in ("en", "pt", "fr", "ja"):
        print(lingua, "|", " | ".join(textos[lingua][c] for c in ("pr_plan_vida", "pr_p_vida", "pr_l_vida", "pr_th_launch")))
    print("ok: agora o tools/gerar-linguas.py")

if __name__ == "__main__":
    main()
