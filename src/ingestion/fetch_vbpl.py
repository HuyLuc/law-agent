"""Tải nội dung văn bản luật từ vbpl.vn (Cơ sở dữ liệu quốc gia về pháp luật).

vbpl.vn chặn request tự động (WAF phát hiện navigator.webdriver), nên cần
Playwright + Chrome thật (channel="chrome") và một init script xoá cờ
webdriver trước khi trang tải. URL các trang chi tiết phải lấy qua ô tìm
kiếm trên trang chủ vì URL kiểu ItemID cũ (?ItemID=...) đã ngừng dùng.

Chạy: python -m src.ingestion.fetch_vbpl
Cập nhật danh sách DOCS bên dưới khi cần tải văn bản mới hoặc luật thay đổi.
"""

from pathlib import Path

from playwright.sync_api import sync_playwright

RAW_DIR = Path(__file__).resolve().parents[2] / "data" / "raw"

DOCS = [
    ("blld2019", "https://vbpl.vn/van-ban/chi-tiet/bo-luat-lao-dong-so-45-2019-qh14--139264"),
    (
        "nd145_2020",
        "https://vbpl.vn/van-ban/chi-tiet/nghi-dinh-so-145-2020-nd-cp-quy-dinh-chi-tiet-va-huong-dan-thi-hanh-mot-so-dieu-cua-bo-luat-lao-dong-ve-dieu-kien-lao-dong-va-quan-he-lao-dong--152668",
    ),
    (
        "nd293_2025",
        "https://vbpl.vn/van-ban/chi-tiet/nghi-dinh-so-293-2025-nd-cp-quy-dinh-muc-luong-toi-thieu-doi-voi-nguoi-lao-dong-lam-viec-theo-hop-dong-lao-dong--183939",
    ),
]


def fetch_all() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(
            channel="chrome",
            headless=True,
            args=["--disable-blink-features=AutomationControlled"],
        )
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36"
            ),
            locale="vi-VN",
            viewport={"width": 1366, "height": 900},
        )
        context.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )
        page = context.new_page()
        for name, url in DOCS:
            page.goto(url, wait_until="networkidle", timeout=60000)
            page.wait_for_timeout(1500)
            panel = page.query_selector("[id$='panel-toan-van']")
            if panel is None:
                print(f"{name}: KHONG TIM THAY noi dung, url cuoi = {page.url}")
                continue
            html = panel.inner_html()
            out_path = RAW_DIR / f"{name}.html"
            out_path.write_text(html, encoding="utf-8")
            print(f"{name}: da luu {len(html)} ky tu -> {out_path}")
        browser.close()


if __name__ == "__main__":
    fetch_all()
