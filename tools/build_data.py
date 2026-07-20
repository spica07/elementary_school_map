# -*- coding: utf-8 -*-
"""schools_raw.json (공공데이터포털 전국초중등학교위치표준데이터, pk=15021148)
-> assets/js/data.js 생성 (전국 초등학교만 추출)
"""
import json
import re
import sys
from datetime import date
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

TOOLS = Path(__file__).resolve().parent
BASE = TOOLS.parent
RAW = TOOLS / "schools_raw.json"
GRD_RAW = TOOLS / "schoolInfoGrd_raw.json"
OUT = BASE / "assets" / "js" / "data.js"


def load_seoul_student_stats():
    """서울 열린데이터광장 schoolInfoGrd(학교별·학급별 학생수 현황)에서
    학교명 -> 최신 연도 학생수 통계 매핑을 만든다. 서울만 제공되는 데이터라
    다른 지역은 이 필드가 비어 있다."""
    if not GRD_RAW.exists():
        return {}
    rows = json.loads(GRD_RAW.read_text(encoding="utf-8"))
    elem = [r for r in rows if r.get("SCHL_GRD_CD") == "02" and r.get("EXCL_YN") != "Y"]
    best = {}
    for r in elem:
        name = (r.get("SCHL_NM") or "").strip()
        year = r.get("PBLNT_YR") or ""
        if not name or not year:
            continue
        if name in best and best[name][0] >= year:
            continue
        best[name] = (year, r)

    def to_num(v, cast=int):
        try:
            return cast(v)
        except (TypeError, ValueError):
            return None

    stats = {}
    for name, (year, r) in best.items():
        grades = []
        for g in range(1, 7):
            sc = to_num(r.get(f"SCYR{g}_STDNT_CNT"))
            cc = to_num(r.get(f"SCYR{g}_CLAS_CNT"))
            if sc is None and cc is None:
                continue
            grades.append({"grade": g, "studentCount": sc or 0, "classCount": cc or 0})
        stats[name] = {
            "studentCount": to_num(r.get("STDNT_SUM")),
            "classCount": to_num(r.get("CLAS_CNT_SUM")),
            "teacherCount": to_num(r.get("TCR_CNT")),
            "studentsPerClass": to_num(r.get("CLAS_STDNT_CNT_SUM"), float),
            "specialClassCount": to_num(r.get("SPCL_CLAS_CNT")),
            "statYear": year,
            "grades": grades,
        }
    return stats

REGION_PREFIX = [
    ("서울특별시", "서울"), ("서울시", "서울"), ("서울", "서울"),
    ("부산광역시", "부산"), ("부산", "부산"),
    ("대구광역시", "대구"), ("대구", "대구"),
    ("인천광역시", "인천"), ("인천", "인천"),
    ("광주광역시", "광주"), ("광주", "광주"),
    ("대전광역시", "대전"), ("대전", "대전"),
    ("울산광역시", "울산"), ("울산", "울산"),
    ("세종특별자치시", "세종"), ("세종특별시", "세종"), ("세종", "세종"),
    ("경기도", "경기"), ("경기", "경기"),
    ("강원특별자치도", "강원"), ("강원도", "강원"), ("강원", "강원"),
    ("충청북도", "충북"), ("충북", "충북"),
    ("충청남도", "충남"), ("충남", "충남"),
    ("전북특별자치도", "전북"), ("전라북도", "전북"), ("전북", "전북"),
    ("전라남도", "전남"), ("전남", "전남"),
    ("경상북도", "경북"), ("경북", "경북"),
    ("경상남도", "경남"), ("경남", "경남"),
    ("제주특별자치도", "제주"), ("제주도", "제주"), ("제주", "제주"),
]

REGION_ORDER = ["서울", "부산", "대구", "인천", "광주", "대전", "울산", "세종",
                "경기", "강원", "충북", "충남", "전북", "전남", "경북", "경남", "제주"]

DISTRICT_RE = re.compile(r"^\s*([가-힣]{1,8}?(?:시|군|구))(?=\s|[가-힣])")


def parse_region_district(addr):
    if not addr:
        return None, None
    addr = addr.strip()
    for prefix, region in REGION_PREFIX:
        if addr.startswith(prefix):
            rest = addr[len(prefix):].strip()
            m = DISTRICT_RE.match(rest)
            district = m.group(1) if m else None
            return region, district
    return None, None


def main():
    raw = json.load(open(RAW, encoding="utf-8"))
    recs = raw["records"]
    print("원본(전국 초중고):", len(recs))

    elem = [r for r in recs if r.get("SCHOOL_SE") == "초등학교" and r.get("OPER_STTUS") == "운영"]
    print("초등학교(운영중):", len(elem))

    seoul_stats = load_seoul_student_stats()
    print("서울 학생수 통계 확보:", len(seoul_stats), "곳")

    out = []
    skipped = []
    ref_dates = []
    for r in elem:
        name = re.sub(r"\s+", " ", (r.get("SCHOOL_NM") or "")).strip()
        addr = (r.get("RDNMADR") or r.get("LNMADR") or "").strip()
        region, district = parse_region_district(addr)
        if not region or not name:
            skipped.append((name, addr))
            continue
        try:
            lat = round(float(r["LATITUDE"]), 6)
            lng = round(float(r["LONGITUDE"]), 6)
        except (TypeError, ValueError, KeyError):
            skipped.append((name, "좌표없음"))
            continue
        if not (33.0 < lat < 38.7 and 124.5 < lng < 131.9):
            skipped.append((name, "좌표범위밖"))
            continue

        fond = (r.get("FOND_TYPE") or "").strip()
        kind = fond if fond in ("공립", "사립", "국립") else "공립"

        ref = r.get("REFERENCE_DATE") or ""
        if ref:
            ref_dates.append(ref)

        item = {
            "name": name,
            "kind": kind,
            "region": region,
            "district": district or "",
            "address": addr,
            "lat": lat,
            "lng": lng,
            "isBranch": (r.get("BNHH_SE") == "분교"),
            "eduOffice": (r.get("EDC_SPORT_NM") or "").strip(),
            "foundedDate": (r.get("FOND_DATE") or "").strip(),
        }
        stat = seoul_stats.get(name) if region == "서울" else None
        if stat:
            item.update(stat)
        out.append(item)

    out.sort(key=lambda x: (REGION_ORDER.index(x["region"]), x["district"], x["name"]))
    for i, it in enumerate(out, 1):
        it["id"] = i

    print("정제 후:", len(out), "| 제외:", len(skipped))
    for s in skipped[:10]:
        print("  제외:", s)

    from collections import Counter
    print("지역별:", dict(Counter(x["region"] for x in out)))
    print("설립구분:", dict(Counter(x["kind"] for x in out)))
    print("분교:", sum(1 for x in out if x["isBranch"]))
    seoul_total = sum(1 for x in out if x["region"] == "서울")
    seoul_matched = sum(1 for x in out if x["region"] == "서울" and "studentCount" in x)
    print(f"서울 학생수 매칭: {seoul_matched}/{seoul_total}")

    meta = {
        "surveyDate": date.today().isoformat(),
        "source": "교육부 전국초중등학교위치표준데이터 (데이터기준일자 " + (max(ref_dates) if ref_dates else "미상") +
                  "), 서울 열린데이터광장 서울시 학교별·학급별 학생수 현황",
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("// 자동 생성 파일 — tools/build_data.py 가 생성. 직접 수정하지 마세요.\n")
        f.write("window.DATA_META = " + json.dumps(meta, ensure_ascii=False) + ";\n")
        f.write("window.SCHOOLS = " + json.dumps(out, ensure_ascii=False, separators=(",", ":")) + ";\n")
    print("저장:", OUT, "|", OUT.stat().st_size, "bytes")


if __name__ == "__main__":
    main()
