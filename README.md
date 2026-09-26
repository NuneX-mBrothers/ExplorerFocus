<div align="center">

<img src="icon-256.png" width="96" height="96" alt="ExplorerFocus">

# ExplorerFocus

**The file organiser for Windows 10 & 11 — your folders, arranged by what you work on.**
A focused file explorer with profiles, rich preview, honest file operations, encrypted vaults, remote/cloud access — and capture tools built in.

[**⬇ Download (.exe)**](https://github.com/NuneX-mBrothers/ExplorerFocus/releases/latest/download/ExplorerFocus.exe) · [**Download (.zip)**](https://github.com/NuneX-mBrothers/ExplorerFocus/releases/latest/download/ExplorerFocus.zip) · [**Website**](https://nunex-mbrothers.github.io/ExplorerFocus/) · [**Releases**](https://github.com/NuneX-mBrothers/ExplorerFocus/releases/latest)

Single `.exe` · no installer · no runtime to install · digitally signed · 16 languages

<img src="shots/01-perfis.webp" width="820" alt="ExplorerFocus with 22 profile tabs across the top and a folder of photos in icon view">

<a href="https://alternativeto.net/software/explorerfocus/about/?utm_source=badge&amp;utm_medium=referral"><img src="https://alternativeto.net/static/badges/badge-compact-color.svg" width="244" height="79" alt="ExplorerFocus | AlternativeTo"></a>

</div>

---

## Why

Windows Explorer treats every folder the same: one window trying to do everything, remembering
nothing. ExplorerFocus is built for people who spend the day in the same handful of folders and
want to reach them fast — and to see what's inside a file without opening it.

## What it does

- **Profiles** — each is a tab with its own folder tree, filters and remembered state. `Ctrl+1`–`9` to switch.
- **Configurable trees** — build them from folders *and* from registry roots; drag to reorder. Disk space shown per root.
- **Multi-pattern search** — `*.cs *.json` in one box, wildcards anywhere, plus opt-in search across profiles.
- **Rich preview** — code with syntax highlighting and folding, Markdown, PDF, Word/Excel/PowerPoint, images, EPUB, audio and video (streamed, so a 2 GB file opens instantly).
- **Honest file operations** — copy/move/delete with real per-file progress, throughput, ETA, pause/resume, up to 6 in parallel, persistent history and 6-way conflict resolution.
- **Encrypted vaults** — file names and contents encrypted in the Cryptomator format. Give a vault a drive letter and every app on the machine can use it; vaults made here also open in Cryptomator on Android, iOS, Mac and Linux. Opening a vault is free; creating one is Premium.
- **Remote & cloud** — SFTP, FTP/FTPS, WebDAV, Dropbox, OneDrive. Browse, preview and operate as if local; edit a remote file and it syncs on save.
- **Books & comics** — preview any EPUB, Kindle, FB2 or comic, and read it in full: plain, or as a two-page paper book with a night version.
- **Capture built in** — screen (with webcam PiP and system audio), video, audio and scanning, without leaving the explorer.
- **The sound of a video** — save the audio of any video Windows can play as MP3, AAC, WMA, WAV, FLAC or ALAC, or make a copy of the video without sound. The original is left untouched.
- **Complete dark theme**, rich hover tooltips, archives browsable as folders, integrated terminals (CMD, PowerShell, Git Bash), per-extension app associations, auto-updates.

## Free vs Premium

**The free version is the complete product for virtually everyone** — all the file management,
profiles, preview, operations, terminals, dark theme, the 16 languages. Nothing expires, nothing
nags.

Premium unlocks a defined set of extras: creating encrypted vaults, full remote access (multiple
connections, all operations, WebDAV, Dropbox, OneDrive), screen and camera recording without
watermark or time cap and with system sound, audio mixing, multi-page scanning with a document
feeder, the complete book reader (EPUB, Kindle formats, FB2 and comics, including the paper mode), and intro/end cards on
recordings. It's a **one-time donation**, not a subscription, activated per machine. Details on the
[website](https://nunex-mbrothers.github.io/ExplorerFocus/#premium).

## First run

ExplorerFocus is digitally signed as of version 1.2.23. The signature is recent, so Windows may
still ask you to confirm on first launch — it takes a while to recognise a new publisher. If it
does, click **More info → Run anyway**. Every release publishes its **SHA-256** in
[`version.json`](version.json) and on the website, so you can verify the file you downloaded.

## Built with

WPF on .NET 10, published as a single-file self-contained `win-x64` executable.
AvalonEdit (code preview) · WebView2 (PDF/Office/Markdown) · SSH.NET · FluentFTP · Media Foundation (capture) ·
Bouncy Castle (vault encryption) · DokanNet (vault drive letters — the Dokany driver itself is not shipped).

## About

Made by **mBrothers** — three brothers who keep talking each other into building things.
Questions, bugs and ideas: [NunexmBrothers@gmail.com](mailto:NunexmBrothers@gmail.com)

Also from us: [**The Absolute LogViewer**](https://nunex-mbrothers.github.io/TheAbsoluteLogViewer/) — a free Windows log viewer with real-time tailing.
