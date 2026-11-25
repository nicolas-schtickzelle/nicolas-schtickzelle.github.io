#!/usr/bin/env python3
"""
Download every image / file that the original Wix site referenced, and store it
locally under assets/ with a human-readable filename.

Run once (needs internet):   python tools/download_assets.py

After this the website is completely self-contained: nothing is loaded from
wixstatic.com any more.
"""
import os
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(HERE, "assets", "img")
FILES = os.path.join(HERE, "assets", "files")

WIX_MEDIA = "https://static.wixstatic.com/media/"
WIX_FILES = "https://www.nicolas-schtickzelle.net/_files/ugd/"

# friendly name  ->  original Wix media id
IMAGES = {
    # --- identity / branding -------------------------------------------------
    "logo.png": "a893d2_6c8bbdb0000c45b4a94784a8307423e5~mv2.png",
    "nicolas-portrait.png": "a893d2_f58a6edf14094c92aa1b1b6a7f9a75ea~mv2.png",
    "uclouvain-logo.png": "a893d2_2e0eb62fc7b549a7958e66e015931e57~mv2.png",
    "eli-logo.png": "a893d2_944ad7bb013a47fda122a925dda60cb5~mv2_d_1200_1202_s_2.png",
    "eliv-logo.png": "a893d2_dae0029d08da43d694392fe0d7830961~mv2.png",
    "qcb-group-logo.gif": "a893d2_61e24cb228284b4882ab4bf4cf2e4093~mv2.gif",
    "scholar-badge.jpg": "a893d2_c12655d30841468eb0e375fac972bdef~mv2.jpg",
    "hero-home.jpg": "11062b_f0d5e0c342cc49dca298de0225d2247cf000.jpg",
    # --- social icons --------------------------------------------------------
    "icon-google-scholar.png": "a893d2_a2b43bdd91da4ba8ad01cbdb796766cc~mv2.png",
    "icon-researchgate.png": "a893d2_25ac691c862a4cf58d3f9fb1124ae259~mv2.png",
    "icon-academia.png": "a893d2_6376f3f789e74760829b28e97ff92ce3~mv2.png",
    "icon-wos.png": "a893d2_9ba79da73b07477f9e67c471b59723c0~mv2.png",
    "icon-linkedin.png": "6ea5b4a88f0b4f91945b40499aa0af00.png",
    # --- research interests --------------------------------------------------
    "ri-green-field.jpg": "65d3de374ace430083f740220d95b3c3.jpg",
    "ri-harvest.jpg": "1c325fe25b4e081d13af79d1812d2d58.jpg",
    "ri-dairy-farm.jpg": "cc69d0bae17e495da6cf2d0ebe099c04.jpg",
    "ri-field-01.jpg": "a893d2_713ea0d1542249598d57dcfe8aff76a4~mv2.jpg",
    "ri-field-02.jpg": "a893d2_d9db141dc6e24b2a8ec89c1da9ccd0b9~mv2.jpg",
    "ri-field-03.jpg": "a893d2_5c57b438a2d14da1bef7765aedbb3543~mv2.jpg",
    "ri-lab-01.jpg": "a893d2_375ada092b0c4ea4a17d23f5f85669a7~mv2.jpg",
    "ri-lab-02.jpg": "a893d2_684fa82619f7461395211700cd71e8c3~mv2.jpg",
    "ri-lab-03.png": "a893d2_8e300f11672e4211a8b97c3bdd3cd264~mv2.png",
    "ri-salmon.jpg": "a893d2_17fb8c105f1d49ca84ff50e9131ddcfd~mv2.jpg",
    "ri-landscape-01.jpg": "a893d2_5fae142b8b0442b0837b11f354bd2fac~mv2.jpg",
    "ri-landscape-02.jpg": "a893d2_c612a9c7aa1d45948f96b2326dacfe75~mv2.jpg",
    "ri-landscape-03.jpg": "a893d2_e88654f41c8341f3988f3bdb46906e4d~mv2.jpg",
    "boloria-mating.jpg": "a893d2_661673d25975414fab7ede4830449477~mv2.jpg",
    "boloria-marked.jpg": "a893d2_e502edcba51e4badb92d24a8c1c4f3f0~mv2_d_1704_2272_s_2.jpg",
    "tetrahymena-cell.jpg": "a893d2_7f1445a2870f4d7a96ba0d89fc3bef40~mv2.jpg",
    "tetrahymena-trajectories.jpg": "a893d2_b1ef1bdc69f74118b86e5ae80b9f5191~mv2.jpg",
    "boloria-paths.jpg": "a893d2_d4a88a32c3894f07a493f914f86cd037~mv2.jpg",
    "pva-crystal-ball.png": "a893d2_ee14a87d6bf4474fa9e569c3234d29a4~mv2.png",
    "beaver-dam.jpg": "a893d2_726d21cd82ad424da168cccdfc79b769~mv2.jpg",
    "macaque.jpg": "a893d2_b7914d362b124d9a831751c5ef52b58d~mv2.jpg",
    "artificial-landscape.png": "a893d2_5d0838b1c02b43e6913cbbe4e8ba4aee~mv2.png",
    "image-analysis.png": "a893d2_f9dda9574a0d4ac7b9abdf27939c1768~mv2.png",
    "cple.png": "a893d2_1e131ad92eff44cab214b5f462dcf54b~mv2_d_1890_1512_s_2.png",
    # --- publications --------------------------------------------------------
    "news-bmc-biology-2025.png": "a893d2_9518cffd72e849cdb02cde5e22e2afd7~mv2.png",
    # --- mentoring -----------------------------------------------------------
    "mentees-map.jpg": "a893d2_ef73c2dcc20d4105978b102789b511a1~mv2_d_2800_2000_s_2.jpg",
    "mentee-bastogne.jpg": "a893d2_4b3ea7eae7b64ea885cd3d7f153e3c5b~mv2.jpg",
    "mentee-brans.jpg": "a893d2_8e9443cd40bb4bb98c00878ccd0857a5~mv2.jpg",
    "mentee-dacek.jpg": "a893d2_afb6a419ffb94af88af4f895766cc591~mv2.jpg",
    "mentee-debruin.jpg": "a893d2_f0591ff6af0a414c90502e813eddafc0~mv2.jpg",
    "mentee-choutt.jpg": "a893d2_b8f091aecd004954a81ecc4ccdddc289~mv2.jpg",
    "mentee-dubois.jpg": "a893d2_6c6eb6da370c48c3b4e8a143d4d23b91~mv2.jpg",
    "mentee-gielen.jpg": "a893d2_48e7ca0c6abe4cbdb11debe3848e000e~mv2.jpg",
    "mentee-jacob.jpg": "a893d2_90445f4ad88f48a8993c9c337e24a932~mv2.jpg",
    "mentee-laurent.jpg": "a893d2_3483235221df4e1191dcdd38486932be~mv2.jpg",
    "mentee-lebigre.jpg": "a893d2_15662bba8d8f40789042c8f07ae440f4~mv2.jpg",
    "mentee-legrand.jpg": "a893d2_4e02dcd342d44300bf9d5d32996f87f4~mv2.jpg",
    "mentee-manzi.png": "a893d2_a81c0bb077ff41258076e968afb7c6d5~mv2.png",
    "mentee-mitchell.jpg": "a893d2_03ffaaa744df4c01b2be6663143ce411~mv2.jpg",
    "mentee-moreljournel.png": "a893d2_f8c839013aa040b4a2ebe964646470dd~mv2.png",
    "mentee-pennekamp.jpg": "a893d2_281c0b7ccad646f599244106a7751e1e~mv2.jpg",
    "mentee-radchuk.jpg": "a893d2_b4bbff9e8aa6435e927de264abd3e849~mv2.jpg",
    "mentee-svendsen.jpg": "a893d2_2b08d44c58ca49bf8f25067d06601efd~mv2.jpg",
    "mentee-thuillier.jpg": "a893d2_b2fcdfc8895e457aa07727e4beefb2b1~mv2.jpg",
    "mentee-turlure.jpg": "a893d2_af0c7413a1cd49809aad2c3a78047ef5~mv2.jpg",
    "mentee-raffard.png": "a893d2_f2fe3c84de994b8d899d678a6c7c3323~mv2.png",
    # --- teaching ------------------------------------------------------------
    "lbio1283-01.png": "a893d2_cc662d4884374eb59d5faad605497445~mv2.png",
    "lbio1283-02.png": "a893d2_81ba16034d7c4c0bb56fa8c35e615916~mv2.png",
    "lbio1283-03.png": "a893d2_380ffd61a0c04591ab9c06481d7c4b21~mv2.png",
    "lboe2120-01.png": "a893d2_1e76f28fcc3e489e9f521c13d19fae21~mv2.png",
    "lboe2120-02.png": "a893d2_9ab2324661f44b0ea54d2ab5dd3a6852~mv2.png",
    "lboe2120-03.png": "a893d2_7df8b17f109944928ec4f393fa86298e~mv2.png",
    "lbio1116-01.png": "a893d2_69742b2c2eae4934acf47a074c4dd1c7~mv2.png",
    "lbio1116-02.png": "a893d2_196cad45cb804b95923f6af63f677f65~mv2.png",
    "lbio1116-03.png": "a893d2_bc27ad24e2ce48508f1aba3d08075662~mv2.png",
    "lboe2112-01.png": "a893d2_7f7a87034c5c4ad38573ae42f5566af2~mv2.png",
    "lboe2112-02.png": "a893d2_1805e13e91c74b2ab35fcf1ff2d7c9a1~mv2.png",
    "lboe2112-03.png": "a893d2_7f4aacb1c784492a96da7f39139b2112~mv2.png",
    # --- outreach ------------------------------------------------------------
    "outreach-talk-2019.jpg": "a893d2_7e6639339acf4a059c7e1463fddf26e1~mv2_d_2240_1488_s_2.jpg",
    "outreach-researchers-night.jpg": "a893d2_64e32ee32c564d759cf44fab42c0806f~mv2_d_2594_1960_s_2.jpg",
    "outreach-conservation-conf.jpg": "a893d2_e637be1f6749460fb7d0f6168339b8b6~mv2_d_3216_2136_s_2.jpg",
    "poster-natagora-2013.jpg": "a893d2_ba9d9324a6984332b38e531d75a24635~mv2_d_2674_3708_s_4_2.jpg",
    "poster-natagora-2014.jpg": "a893d2_f608c07db72643fc872584ba38113b18~mv2_d_2497_3532_s_4_2.jpg",
    "researchers-night-2010.png": "a893d2_dc61aaec2658459d9c31ae68c94cac1e~mv2.png",
    "printemps-sciences-2019.png": "a893d2_178a74646b1b415393f60a67ad97c501~mv2.png",
    "pds-2019-01.jpg": "a893d2_b091fbb274b24309b130517eeb462381~mv2_d_2240_1488_s_2.jpg",
    "pds-2019-02.jpg": "a893d2_b051f6d8af78416b9804584fb26b2d72~mv2_d_2240_1488_s_2.jpg",
    "pds-2019-03.jpg": "a893d2_f18f743dcc3249d18abed97acf39210d~mv2_d_1488_2240_s_2.jpg",
    "pds-2019-04.png": "a893d2_3acab449ffb24e10bc1462613611c2f8~mv2.png",
    "uda-2019.png": "a893d2_567ec16042284e73b1cfc1860e1fa7ac~mv2.png",
    "press-fnrs-70.png": "a893d2_c71bbc59c7f847748357eb0e5162bb18~mv2.png",
    "press-athena-365.png": "a893d2_eaafe95aaae042ab9fcb5ff32dcd3647~mv2.png",
    "press-rtl-2024.png": "a893d2_52d289d9a0b84704844872556890feda~mv2.png",
    "press-fnrs-81.png": "a893d2_dfbfb216eb6344e6a399e3e4144867a1~mv2.png",
    "press-athena-257.png": "a893d2_b793f35b5ecb447bae9756639f8d6af5~mv2.png",
    "press-huffpost-2023.png": "a893d2_420de2f244de42a4b91ffc7eedf7b8bf~mv2.png",
    # --- contact -------------------------------------------------------------
    "vcard-qr.png": "a893d2_62ba502a59454aaaab7028483cc8a689~mv2_d_1380_1380_s_2.png",
}

DOCS = {
    "natagora-programme-2013.pdf": "a893d2_01724744f330472bb2ce18aa99447ecd.pdf",
    "natagora-programme-2014.pdf": "a893d2_b0757c362c4f483f8572a848919b94e3.pdf",
    "press-fnrs-81.pdf": "a893d2_72c3d479b7134e8eba9871f71673fee3.pdf",
    "press-athena-257.pdf": "a893d2_6cb690fd47504ff2b002b771181d91a5.pdf",
}

UA = {"User-Agent": "Mozilla/5.0 (site-migration script)"}


def grab(url, dest):
    if os.path.exists(dest) and os.path.getsize(dest) > 0:
        return "skip"
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r, open(dest, "wb") as f:
        f.write(r.read())
    return "ok"


def main():
    os.makedirs(IMG, exist_ok=True)
    os.makedirs(FILES, exist_ok=True)
    ok = skipped = failed = 0
    for name, media_id in IMAGES.items():
        try:
            res = grab(WIX_MEDIA + media_id, os.path.join(IMG, name))
            ok += res == "ok"
            skipped += res == "skip"
        except Exception as exc:  # noqa: BLE001
            failed += 1
            print(f"  FAILED {name}: {exc}", file=sys.stderr)
        time.sleep(0.05)
    for name, file_id in DOCS.items():
        try:
            res = grab(WIX_FILES + file_id, os.path.join(FILES, name))
            ok += res == "ok"
            skipped += res == "skip"
        except Exception as exc:  # noqa: BLE001
            failed += 1
            print(f"  FAILED {name}: {exc}", file=sys.stderr)
        time.sleep(0.05)
    print(f"downloaded={ok}  already-present={skipped}  failed={failed}")


if __name__ == "__main__":
    main()
