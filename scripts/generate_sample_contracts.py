"""Tao 10 hop dong lao dong mau (.docx) de do precision/recall cua
contract_rules.py (PLAN.md Tuan 4 Buoi 3-4): 8 hop dong co cai loi, 2 dung.

Chay: python scripts/generate_sample_contracts.py
"""

import json
from pathlib import Path

from docx import Document

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "data" / "eval" / "contracts"

# Moi hop dong: (ten file, cac dong noi dung, danh sach quy_tac du kien bi vi pham)
CONTRACTS: list[tuple[str, list[str], list[str]]] = [
    (
        "contract_01_dung.docx",
        [
            "HỢP ĐỒNG LAO ĐỘNG",
            "Bên A (Người sử dụng lao động): Công ty TNHH Thương mại ABC, địa chỉ Quận 1, TP.HCM (Vùng I).",
            "Bên B (Người lao động): Nguyễn Văn A.",
            "Loại hợp đồng: không xác định thời hạn.",
            "Vị trí công việc: Nhân viên kinh doanh (yêu cầu trình độ trung cấp), địa điểm làm việc tại văn phòng công ty.",
            "Thời gian thử việc: 25 ngày.",
            "Lương thử việc: 8.500.000 đồng/tháng.",
            "Lương chính thức: 10.000.000 đồng/tháng, trả hằng tháng qua chuyển khoản.",
            "Chế độ nâng bậc, nâng lương: xét mỗi năm 1 lần theo quy chế công ty.",
            "Thời giờ làm việc: 8 giờ/ngày, 44 giờ/tuần. Nghỉ trưa 1 giờ.",
            "Trang bị bảo hộ lao động: được cấp đầy đủ theo quy định.",
            "Bảo hiểm xã hội, y tế, thất nghiệp: đóng đầy đủ theo quy định pháp luật.",
            "Đào tạo, bồi dưỡng nâng cao trình độ, kỹ năng nghề: công ty tổ chức đào tạo định kỳ.",
        ],
        [],
    ),
    (
        "contract_02_dung.docx",
        [
            "HỢP ĐỒNG LAO ĐỘNG",
            "Bên A: Công ty Cổ phần Dịch vụ Kế toán XYZ, địa chỉ Quận Hải Châu, Đà Nẵng (Vùng II).",
            "Bên B: Trần Thị B.",
            "Loại hợp đồng: xác định thời hạn 24 tháng.",
            "Vị trí công việc: Kế toán trưởng (yêu cầu trình độ cao đẳng trở lên), địa điểm làm việc tại trụ sở công ty.",
            "Thời gian thử việc: 55 ngày.",
            "Lương thử việc: 12.000.000 đồng/tháng.",
            "Lương chính thức: 14.000.000 đồng/tháng.",
            "Chế độ nâng bậc, nâng lương: theo thỏa ước lao động tập thể.",
            "Thời giờ làm việc: 8 giờ/ngày, 48 giờ/tuần. Nghỉ giữa ca 1 giờ.",
            "Trang bị bảo hộ lao động: theo quy định của công ty.",
            "Bảo hiểm xã hội, y tế, thất nghiệp: đóng đầy đủ theo quy định.",
            "Đào tạo, bồi dưỡng nâng cao trình độ, kỹ năng nghề: được cử tham gia khóa đào tạo hằng năm.",
        ],
        [],
    ),
    (
        "contract_03_loi_thu_viec.docx",
        [
            "HỢP ĐỒNG LAO ĐỘNG",
            "Bên A: Công ty TNHH Bảo vệ An Ninh DEF, Vùng I.",
            "Bên B: Lê Văn C.",
            "Loại hợp đồng: xác định thời hạn 12 tháng.",
            "Vị trí công việc: Nhân viên bảo vệ (công việc phổ thông, không yêu cầu bằng cấp), địa điểm làm việc tại cổng công ty.",
            "Thời gian thử việc: 20 ngày.",
            "Lương thử việc: 5.500.000 đồng/tháng.",
            "Lương chính thức: 6.000.000 đồng/tháng.",
            "Chế độ nâng bậc, nâng lương: xét hằng năm.",
            "Thời giờ làm việc: 8 giờ/ngày, 48 giờ/tuần. Nghỉ giữa ca 30 phút.",
            "Trang bị bảo hộ lao động: cấp đồng phục, còi, đèn pin.",
            "Bảo hiểm xã hội, y tế, thất nghiệp: đóng đầy đủ theo quy định.",
            "Đào tạo, bồi dưỡng nâng cao trình độ, kỹ năng nghề: tập huấn nghiệp vụ bảo vệ định kỳ.",
        ],
        ["thoi_gian_thu_viec"],
    ),
    (
        "contract_04_loi_luong_thu_viec.docx",
        [
            "HỢP ĐỒNG LAO ĐỘNG",
            "Bên A: Công ty TNHH Sản xuất GHI, Vùng I.",
            "Bên B: Phạm Thị D.",
            "Loại hợp đồng: không xác định thời hạn.",
            "Vị trí công việc: Nhân viên vận hành máy (trình độ trung cấp), địa điểm làm việc tại nhà máy công ty.",
            "Thời gian thử việc: 25 ngày.",
            "Lương thử việc: 6.300.000 đồng/tháng.",
            "Lương chính thức: 9.000.000 đồng/tháng.",
            "Chế độ nâng bậc, nâng lương: xét mỗi 2 năm.",
            "Thời giờ làm việc: 8 giờ/ngày, 48 giờ/tuần. Nghỉ giữa ca 30 phút.",
            "Trang bị bảo hộ lao động: cấp đầy đủ đồ bảo hộ.",
            "Bảo hiểm xã hội, y tế, thất nghiệp: đóng đầy đủ theo quy định.",
            "Đào tạo, bồi dưỡng nâng cao trình độ, kỹ năng nghề: đào tạo tại chỗ.",
        ],
        ["luong_thu_viec"],
    ),
    (
        "contract_05_loi_luong_toi_thieu.docx",
        [
            "HỢP ĐỒNG LAO ĐỘNG",
            "Bên A: Công ty TNHH Dệt May JKL, Quận Bình Tân, TP.HCM (Vùng I).",
            "Bên B: Hoàng Văn E.",
            "Loại hợp đồng: xác định thời hạn 12 tháng.",
            "Vị trí công việc: Công nhân may (trình độ trung cấp), địa điểm làm việc tại xưởng may số 2.",
            "Thời gian thử việc: 20 ngày.",
            "Lương thử việc: 3.700.000 đồng/tháng.",
            "Lương chính thức: 4.200.000 đồng/tháng.",
            "Chế độ nâng bậc, nâng lương: xét hằng năm theo năng suất.",
            "Thời giờ làm việc: 8 giờ/ngày, 48 giờ/tuần. Nghỉ giữa ca 30 phút.",
            "Trang bị bảo hộ lao động: cấp khẩu trang, găng tay.",
            "Bảo hiểm xã hội, y tế, thất nghiệp: đóng đầy đủ theo quy định.",
            "Đào tạo, bồi dưỡng nâng cao trình độ, kỹ năng nghề: đào tạo tay nghề 1 tuần đầu.",
        ],
        ["luong_toi_thieu_vung"],
    ),
    (
        "contract_06_loi_gio_ngay.docx",
        [
            "HỢP ĐỒNG LAO ĐỘNG",
            "Bên A: Công ty TNHH Xây dựng MNO, Vùng II.",
            "Bên B: Đỗ Văn F.",
            "Loại hợp đồng: xác định thời hạn 12 tháng.",
            "Vị trí công việc: Kỹ thuật viên công trình (trình độ trung cấp), địa điểm làm việc tại công trình dự án.",
            "Thời gian thử việc: 20 ngày.",
            "Lương thử việc: 7.000.000 đồng/tháng.",
            "Lương chính thức: 8.000.000 đồng/tháng.",
            "Chế độ nâng bậc, nâng lương: xét hằng năm.",
            "Thời giờ làm việc: 10 giờ/ngày, 50 giờ/tuần. Nghỉ giữa ca 30 phút.",
            "Trang bị bảo hộ lao động: mũ bảo hộ, giày bảo hộ.",
            "Bảo hiểm xã hội, y tế, thất nghiệp: đóng đầy đủ theo quy định.",
            "Đào tạo, bồi dưỡng nâng cao trình độ, kỹ năng nghề: đào tạo an toàn lao động.",
        ],
        ["gio_lam_ngay", "gio_lam_tuan"],
    ),
    (
        "contract_07_loi_gio_tuan.docx",
        [
            "HỢP ĐỒNG LAO ĐỘNG",
            "Bên A: Công ty TNHH Bán lẻ PQR, Vùng I.",
            "Bên B: Vũ Thị G.",
            "Loại hợp đồng: xác định thời hạn 12 tháng.",
            "Vị trí công việc: Nhân viên bán hàng (công việc phổ thông), địa điểm làm việc tại cửa hàng chi nhánh.",
            "Thời gian thử việc: 6 ngày.",
            "Lương thử việc: 5.700.000 đồng/tháng.",
            "Lương chính thức: 6.500.000 đồng/tháng.",
            "Chế độ nâng bậc, nâng lương: xét hằng năm.",
            "Thời giờ làm việc: 9 giờ/ngày, 6 ngày/tuần (tổng 54 giờ/tuần). Nghỉ giữa ca 30 phút.",
            "Trang bị bảo hộ lao động: đồng phục cửa hàng.",
            "Bảo hiểm xã hội, y tế, thất nghiệp: đóng đầy đủ theo quy định.",
            "Đào tạo, bồi dưỡng nâng cao trình độ, kỹ năng nghề: đào tạo kỹ năng bán hàng.",
        ],
        ["gio_lam_ngay", "gio_lam_tuan"],
    ),
    (
        "contract_08_loi_thieu_noi_dung.docx",
        [
            "HỢP ĐỒNG LAO ĐỘNG",
            "Bên A: Công ty TNHH Công nghệ STU, Vùng I.",
            "Bên B: Ngô Văn H.",
            "Loại hợp đồng: không xác định thời hạn.",
            "Vị trí công việc: Lập trình viên (trình độ cao đẳng trở lên).",
            "Thời gian thử việc: 50 ngày.",
            "Lương thử việc: 15.000.000 đồng/tháng.",
            "Lương chính thức: 17.000.000 đồng/tháng.",
            "Thời giờ làm việc: 8 giờ/ngày, 40 giờ/tuần.",
            "Trang bị bảo hộ lao động: máy tính, thiết bị làm việc.",
        ],
        ["noi_dung_bat_buoc"],
    ),
    (
        "contract_09_nhieu_loi_1.docx",
        [
            "HỢP ĐỒNG LAO ĐỘNG",
            "Bên A: Công ty TNHH Vận tải VWX, Vùng III.",
            "Bên B: Bùi Thị I.",
            "Loại hợp đồng: xác định thời hạn 6 tháng.",
            "Vị trí công việc: Lái xe (công việc phổ thông), địa điểm làm việc theo tuyến vận tải công ty.",
            "Thời gian thử việc: 15 ngày.",
            "Lương thử việc: 4.000.000 đồng/tháng.",
            "Lương chính thức: 6.500.000 đồng/tháng.",
            "Chế độ nâng bậc, nâng lương: xét hằng năm.",
            "Thời giờ làm việc: 8 giờ/ngày, 48 giờ/tuần. Nghỉ giữa ca 30 phút.",
            "Trang bị bảo hộ lao động: cấp áo phản quang, mũ bảo hiểm.",
            "Bảo hiểm xã hội, y tế, thất nghiệp: đóng đầy đủ theo quy định.",
            "Đào tạo, bồi dưỡng nâng cao trình độ, kỹ năng nghề: tập huấn lái xe an toàn.",
        ],
        ["thoi_gian_thu_viec", "luong_thu_viec"],
    ),
    (
        "contract_10_nhieu_loi_2.docx",
        [
            "HỢP ĐỒNG LAO ĐỘNG",
            "Bên A: Công ty TNHH Chế biến Thực phẩm YZA, Vùng IV.",
            "Bên B: Đặng Văn K.",
            "Loại hợp đồng: xác định thời hạn 12 tháng.",
            "Vị trí công việc: Công nhân chế biến (công việc phổ thông).",
            "Thời gian thử việc: 6 ngày.",
            "Lương thử việc: 3.200.000 đồng/tháng.",
            "Lương chính thức: 3.500.000 đồng/tháng.",
            "Chế độ nâng bậc, nâng lương: xét hằng năm.",
            "Thời giờ làm việc: 9 giờ/ngày, 54 giờ/tuần.",
            "Trang bị bảo hộ lao động: găng tay, tạp dề.",
        ],
        ["luong_toi_thieu_vung", "gio_lam_ngay", "gio_lam_tuan", "noi_dung_bat_buoc"],
    ),
]


def build_docx(path: Path, lines: list[str]) -> None:
    doc = Document()
    for line in lines:
        doc.add_paragraph(line)
    doc.save(path)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ground_truth = {}
    for filename, lines, expected_rules in CONTRACTS:
        build_docx(OUT_DIR / filename, lines)
        ground_truth[filename] = expected_rules
        print(f"{filename}: {expected_rules or '(không lỗi)'}")

    (OUT_DIR / "ground_truth.json").write_text(
        json.dumps(ground_truth, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"\nDa tao {len(CONTRACTS)} hop dong mau vao {OUT_DIR}")


if __name__ == "__main__":
    main()
