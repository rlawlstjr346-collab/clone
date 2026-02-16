import json
from pathlib import Path

import pandas as pd
import streamlit as st

SCRIPT_DIR = Path(__file__).resolve().parent
SLOW_DIR = SCRIPT_DIR / "slow_crawler"
DEFAULT_JSONL = SLOW_DIR / "crawl_results.filtered.jsonl"
FALLBACK_JSONL = SLOW_DIR / "crawl_results.jsonl"


def load_jsonl(path: Path):
    rows = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rows.append(json.loads(line))
                except Exception:
                    continue
    except FileNotFoundError:
        return []
    return rows


def row_to_display(r: dict):
    title = (r.get("model") or r.get("title") or "")[:120]
    price = r.get("price") or r.get("price_text") or ""
    if isinstance(price, (int, float)):
        price = f"{int(price):,}원"
    time_ago = r.get("time_ago") or r.get("uploaded_at") or ""
    source = r.get("source") or ""
    url = r.get("item_url") or r.get("source_url") or ""
    return {"모델": title, "가격": price, "업로드": time_ago, "출처": source, "링크": url}


def main():
    st.set_page_config(page_title="Radar — Crawl Preview", layout="wide")
    st.title("Radar — 크롤 결과 미리보기")

    choice = st.sidebar.radio(
        "데이터 파일",
        ["filtered (권장)", "raw (원본)"],
        index=0,
    )
    path = DEFAULT_JSONL if "filtered" in choice else FALLBACK_JSONL

    st.sidebar.markdown("### 실행/수집 가이드")
    st.sidebar.text("1) 필요한 패키지 설치: pip install -r slow_crawler/requirements.txt")
    st.sidebar.text("2) Playwright 설치: python -m playwright install chromium")
    st.sidebar.text("3) 크롤 실행: python3 slow_crawler/run_slow_crawl.py --keyword 아이폰 --pages 15")
    st.sidebar.caption("민감정보(.env/.streamlit/secrets.toml)는 절대 리포지토리에 올리지 마세요.")

    if not path.exists():
        st.warning(f"파일이 없습니다: `{path}`")
        if FALLBACK_JSONL.exists():
            st.info(f"대체 파일이 있으므로 선택을 'raw (원본)'으로 바꿔보세요: `{FALLBACK_JSONL.name}`")
        st.info("로컬에서 크롤을 돌려 `slow_crawler/crawl_results.jsonl` 또는 `.filtered.jsonl`을 생성하세요.")
        return

    rows = load_jsonl(path)
    st.caption(f"총 **{len(rows)}**건 · `{path.name}`")
    if not rows:
        st.info("행이 없습니다.")
        return

    display = [row_to_display(r) for r in rows]
    df = pd.DataFrame(display)
    st.dataframe(df, use_container_width=True, height=500)

    with st.expander("원본 JSON 샘플 (처음 3건)"):
        for i, r in enumerate(rows[:3]):
            st.json(r)

    st.markdown("---")
    st.markdown(
        "문제가 있으면 `slow_crawler/` 폴더의 `run_slow_crawl.py`와 `requirements.txt`를 확인하세요."
    )


if __name__ == "__main__":
    main()
