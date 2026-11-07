# -*- coding: utf-8 -*-
r"""Faz o pacote .tar.gz do SITE do ExplorerFocus que a porta de publicação do servidor recebe, e escreve-o no stdout.

    python tools\empacotar.py | ssh … sites@136.144.201.147 publicar explorerfocus

Leva só as páginas do site (https://intrepidparallel.com/explorerfocus/), o version.json incluído, porque a página o
lê para mostrar a versão, o tamanho e o SHA-256. Ficam de fora:
- a pasta StandAlone/ (o .exe e o .zip), que fica no GitHub nos mesmos endereços de sempre;
- o .git, as ferramentas, o docs/ (as páginas que reencaminham no GitHub, com o version.json que a app lê), os .cmd,
  o README e o ficheiro de verificação da propriedade antiga na Search Console (googlee….html).

⛔ Porque não o tar do Windows (06/11/2026, na mBrothers): as pastas iam «só de leitura» (o OneDrive põe esse atributo
   às pastas) e o servidor não conseguia escrever nelas. Aqui as permissões são sempre as normais (pastas 755,
   ficheiros 644), sem dono, e no formato GNU, sem extensões.
⛔ Sem ligações nem ficheiros especiais: a porta recusa-os, e este script não os põe.
"""
import os
import sys
import tarfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FORA_NO_TOPO = {
    ".git", ".gitignore", ".gitattributes", ".claude", ".nojekyll", "tools", "docs", "README.md", "StandAlone",
}


def normal(ti):
    ti.uid = ti.gid = 0
    ti.uname = ti.gname = ""
    ti.mode = 0o755 if ti.isdir() else 0o644
    return ti


def juntar(tar, caminho, nome):
    ti = tar.gettarinfo(caminho, arcname=nome)
    if not (ti.isfile() or ti.isdir()):
        sys.exit("[ERRO] %s não é um ficheiro nem uma pasta normal" % caminho)
    ti = normal(ti)
    if ti.isfile():
        with open(caminho, "rb") as fh:
            tar.addfile(ti, fh)
    else:
        tar.addfile(ti)


def fora(nome):
    n = nome.lower()
    return nome in FORA_NO_TOPO or n.endswith(".cmd") or (n.startswith("google") and n.endswith(".html"))


def main():
    if sys.stdout.isatty():
        sys.exit("[ERRO] o pacote é binário: liga-o ao ssh com |, ou manda-o para um ficheiro com >")
    for f in ("index.html", "privacy.html", "legal.html", "terms.html", "version.json"):
        if not os.path.isfile(os.path.join(RAIZ, f)):
            sys.exit("[ERRO] falta o %s na raiz do site" % f)
    with tarfile.open(fileobj=sys.stdout.buffer, mode="w|gz", format=tarfile.GNU_FORMAT) as tar:
        juntar(tar, RAIZ, ".")
        for pasta, pastas, ficheiros in os.walk(RAIZ):
            rel = os.path.relpath(pasta, RAIZ)
            if rel == ".":
                pastas[:] = [p for p in pastas if not fora(p)]
                ficheiros = [f for f in ficheiros if not fora(f)]
            pastas.sort()
            for p in pastas:
                caminho = os.path.join(pasta, p)
                if os.path.islink(caminho):
                    sys.exit("[ERRO] ligação: %s" % caminho)
                juntar(tar, caminho, "./" + os.path.relpath(caminho, RAIZ).replace(os.sep, "/"))
            for f in sorted(ficheiros):
                caminho = os.path.join(pasta, f)
                juntar(tar, caminho, "./" + os.path.relpath(caminho, RAIZ).replace(os.sep, "/"))
    sys.stdout.buffer.flush()


if __name__ == "__main__":
    main()
