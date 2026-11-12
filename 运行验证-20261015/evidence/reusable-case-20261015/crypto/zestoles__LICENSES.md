# BAĞIMLILIK LİSANSLARI

> ## ⚠️ BU DOSYA VERİYİ KAPSAMAZ
>
> Aşağıdaki liste yalnızca **yazılım bağımlılıklarının** lisanslarıdır.
>
> **İndirilen piyasa verisinin lisansı yoktur.** Adım 2 araştırması, kullanılan
> beş veri arşivinin hiçbirinin arşivin yanında bir lisans veya kullanım şartı
> yayınlamadığını tespit etti (`reports/01_veri_kaynaklari.md` §7). Hiçbir
> kaynağın kullanım şartlarını karşıladığımız **doğrulanmış değildir**.
>
> Bu yüzden kural: **veri yeniden dağıtılmaz.** Yalnızca yerel araştırma için
> kullanılır. Proje paylaşılırsa yalnızca kod paylaşılır, veri paylaşılmaz.
> (`config/config.yaml` → `veri.yeniden_dagitim.izin: false`)
>
> Not: `binance/binance-public-data` deposu MIT lisanslıdır, ancak bu lisans o
> deponun **indirme scriptlerini** kapsar — verinin kendisini değil.

Bu dosya `scripts/01_lisans_listesi.py` tarafından üretilir; elle düzenlenmez.
Üretim anı (UTC): **2026-08-18T22:12:15Z**
Toplam paket: **39** (doğrudan: 8, geçişli: 31)

Sürüm bilgisi `requirements.txt` (doğrudan) ve `requirements.lock.txt` (tam ortam)
dosyalarıyla birebir aynı ortamdan okunmuştur.

## Lisans türü dağılımı

| Lisans | Paket sayısı |
|---|---|
| MIT | 8 |
| Apache Software License | 4 |
| BSD License | 4 |
| Apache-2.0 | 4 |
| BSD-3-Clause | 3 |
| MIT License | 2 |
| Python Software Foundation License | 2 |
| PSF-2.0 | 2 |
| Apache-2.0 AND MIT | 1 |
| Mozilla Public License 2.0 (MPL 2.0) | 1 |
| Apache-2.0 OR BSD-3-Clause | 1 |
| Apache License 2.0 | 1 |
| BSD-3-Clause AND 0BSD AND MIT AND Zlib AND CC0-1.0 | 1 |
| MPL-2.0 AND (Apache-2.0 OR MIT) | 1 |
| Apache-2.0 OR BSD-2-Clause | 1 |
| MIT-CMU | 1 |
| Apache Software License; BSD License | 1 |
| Apache Software License; MIT License | 1 |


## Doğrudan bağımlılıklar

Projenin kodunun doğrudan `import` ettiği paketler.

| Paket | Sürüm | Lisans | Proje adresi |
|---|---|---|---|
| `ccxt` | 4.5.74 | MIT | [https://ccxt.com](https://ccxt.com) |
| `matplotlib` | 3.11.1 | Python Software Foundation License | [https://matplotlib.org](https://matplotlib.org) |
| `pandas` | 3.0.5 | BSD License | [https://pandas.pydata.org](https://pandas.pydata.org) |
| `pip-licenses` | 5.5.5 | MIT | — |
| `psutil` | 7.2.2 | BSD-3-Clause | [https://github.com/giampaolo/psutil](https://github.com/giampaolo/psutil) |
| `pyarrow` | 25.0.1 | Apache-2.0 | [https://arrow.apache.org/](https://arrow.apache.org/) |
| `PyYAML` | 6.0.3 | MIT License | [https://pyyaml.org/](https://pyyaml.org/) |
| `requests` | 2.34.2 | Apache Software License | [https://github.com/psf/requests](https://github.com/psf/requests) |

## Geçişli bağımlılıklar

Yukarıdakilerin gerektirdiği paketler. Kod bunları doğrudan kullanmaz.

| Paket | Sürüm | Lisans | Proje adresi |
|---|---|---|---|
| `aiohappyeyeballs` | 2.7.1 | Python Software Foundation License | [https://github.com/aio-libs/aiohappyeyeballs](https://github.com/aio-libs/aiohappyeyeballs) |
| `aiohttp` | 3.14.3 | Apache-2.0 AND MIT | [https://github.com/aio-libs/aiohttp](https://github.com/aio-libs/aiohttp) |
| `aiohttp-fast-zlib` | 0.3.0 | Apache Software License | [https://github.com/bluetooth-devices/aiohttp-fast-zlib](https://github.com/bluetooth-devices/aiohttp-fast-zlib) |
| `aiosignal` | 1.4.0 | Apache Software License | [https://github.com/aio-libs/aiosignal](https://github.com/aio-libs/aiosignal) |
| `attrs` | 26.1.0 | MIT | [https://www.attrs.org/en/stable/changelog.html](https://www.attrs.org/en/stable/changelog.html) |
| `certifi` | 2026.6.17 | Mozilla Public License 2.0 (MPL 2.0) | [https://github.com/certifi/python-certifi](https://github.com/certifi/python-certifi) |
| `cffi` | 2.0.0 | MIT | [https://cffi.readthedocs.io/en/latest/whatsnew.html](https://cffi.readthedocs.io/en/latest/whatsnew.html) |
| `charset-normalizer` | 3.4.7 | MIT | [https://github.com/jawah/charset_normalizer/blob/master/CHANGELOG.md](https://github.com/jawah/charset_normalizer/blob/master/CHANGELOG.md) |
| `contourpy` | 1.3.3 | BSD License | [https://github.com/contourpy/contourpy](https://github.com/contourpy/contourpy) |
| `cryptography` | 50.0.0 | Apache-2.0 OR BSD-3-Clause | [https://github.com/pyca/cryptography](https://github.com/pyca/cryptography) |
| `cycler` | 0.12.1 | BSD License | [https://matplotlib.org/cycler/](https://matplotlib.org/cycler/) |
| `fonttools` | 4.63.0 | MIT | [http://github.com/fonttools/fonttools](http://github.com/fonttools/fonttools) |
| `frozenlist` | 1.8.0 | Apache-2.0 | [https://github.com/aio-libs/frozenlist](https://github.com/aio-libs/frozenlist) |
| `idna` | 3.18 | BSD-3-Clause | [https://github.com/kjd/idna](https://github.com/kjd/idna) |
| `kiwisolver` | 1.5.0 | BSD License | [https://github.com/nucleic/kiwi](https://github.com/nucleic/kiwi) |
| `multidict` | 6.7.1 | Apache License 2.0 | [https://github.com/aio-libs/multidict](https://github.com/aio-libs/multidict) |
| `numpy` | 2.5.2 | BSD-3-Clause AND 0BSD AND MIT AND Zlib AND CC0-1.0 | [https://numpy.org](https://numpy.org) |
| `orjson` | 3.11.9 | MPL-2.0 AND (Apache-2.0 OR MIT) | [https://github.com/ijl/orjson](https://github.com/ijl/orjson) |
| `packaging` | 26.3 | Apache-2.0 OR BSD-2-Clause | [https://github.com/pypa/packaging](https://github.com/pypa/packaging) |
| `pillow` | 12.3.0 | MIT-CMU | [https://python-pillow.github.io](https://python-pillow.github.io) |
| `propcache` | 0.5.2 | Apache Software License | [https://github.com/aio-libs/propcache](https://github.com/aio-libs/propcache) |
| `pycparser` | 3.0 | BSD-3-Clause | [https://github.com/eliben/pycparser](https://github.com/eliben/pycparser) |
| `pyparsing` | 3.3.2 | MIT | [https://github.com/pyparsing/pyparsing/](https://github.com/pyparsing/pyparsing/) |
| `python-dateutil` | 2.9.0.post0 | Apache Software License; BSD License | [https://github.com/dateutil/dateutil](https://github.com/dateutil/dateutil) |
| `six` | 1.17.0 | MIT License | [https://github.com/benjaminp/six](https://github.com/benjaminp/six) |
| `typing_extensions` | 4.16.0 | PSF-2.0 | [https://github.com/python/typing_extensions](https://github.com/python/typing_extensions) |
| `tzdata` | 2026.3 | Apache-2.0 | [https://github.com/python/tzdata](https://github.com/python/tzdata) |
| `urllib3` | 2.7.0 | MIT | [https://github.com/urllib3/urllib3/blob/main/CHANGES.rst](https://github.com/urllib3/urllib3/blob/main/CHANGES.rst) |
| `winloop` | 0.6.3 | Apache Software License; MIT License | — |
| `yarl` | 1.24.5 | Apache-2.0 | [https://github.com/aio-libs/yarl](https://github.com/aio-libs/yarl) |
| `zlib-ng` | 1.0.0 | PSF-2.0 | [https://github.com/pycompression/python-zlib-ng](https://github.com/pycompression/python-zlib-ng) |

---
*Yeniden üretmek için:* `.venv\Scripts\python.exe scripts\01_lisans_listesi.py`
