"""Script tam thoi de sinh data/eval/test.jsonl (Tuan 2, Buoi 4-5): 100 cau.

Cau hoi va dieu_can_trich duoc tac gia (Claude) tu tra cuu thu cong tren
data/processed/chunks.jsonl, khong trung voi data/eval/dev.jsonl (van de
dung dieu luat khac hoac goc do khac). Script chi ghi file + kiem tra moi
id trong dieu_can_trich co ton tai that.

QUAN TRONG: sau khi ban duyet va chay script nay lan dau, PLAN.md yeu cau
KHOA file test.jsonl -- khong sua cau hoi nua, chi chay retrieval/agent
tren no de danh gia.

Chay: python scripts/build_test_set.py
"""

# ruff: noqa: C408 -- dict(...) de doc hon {} cho danh sach cau hoi dai

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHUNKS_PATH = ROOT / "data" / "processed" / "chunks.jsonl"
OUT_PATH = ROOT / "data" / "eval" / "test.jsonl"

TEST_SET = [
    # ============ tra_cuu (35) ============
    dict(id="t001", loai="tra_cuu",
         question="Hợp đồng lao động là gì?",
         ground_truth="Là sự thỏa thuận giữa người lao động và người sử dụng lao động về việc làm có trả "
                       "công, tiền lương, điều kiện lao động, quyền và nghĩa vụ của mỗi bên trong quan hệ "
                       "lao động. Trường hợp hai bên thỏa thuận bằng tên gọi khác nhưng có nội dung thể hiện "
                       "về việc làm có trả công, tiền lương và sự quản lý, điều hành, giám sát thì vẫn được "
                       "coi là hợp đồng lao động.",
         dieu_can_trich=["BLLD2019_D13_K0"]),
    dict(id="t002", loai="tra_cuu",
         question="Khi giao kết hợp đồng lao động, người sử dụng lao động phải cung cấp thông tin gì cho người lao động?",
         ground_truth="Phải cung cấp thông tin trung thực về công việc, địa điểm làm việc, điều kiện làm "
                       "việc, thời giờ làm việc/nghỉ ngơi, an toàn vệ sinh lao động, tiền lương, hình thức "
                       "trả lương, bảo hiểm xã hội/y tế/thất nghiệp và các vấn đề khác liên quan mà người "
                       "lao động yêu cầu.",
         dieu_can_trich=["BLLD2019_D16_K0"]),
    dict(id="t003", loai="tra_cuu",
         question="Người sử dụng lao động không được làm những hành vi nào khi giao kết, thực hiện hợp đồng lao động?",
         ground_truth="Không được giữ bản chính giấy tờ tùy thân, văn bằng, chứng chỉ của người lao động; "
                       "không được yêu cầu người lao động bảo đảm bằng tiền hoặc tài sản khác; không được "
                       "buộc người lao động thực hiện hợp đồng để trả nợ cho người sử dụng lao động.",
         dieu_can_trich=["BLLD2019_D17_K0"]),
    dict(id="t004", loai="tra_cuu",
         question="Trường hợp nào một nhóm người lao động được ủy quyền cho 1 người ký hợp đồng lao động chung?",
         ground_truth="Đối với công việc theo mùa vụ hoặc công việc nhất định có thời hạn dưới 12 tháng, "
                       "nhóm người lao động từ đủ 18 tuổi trở lên có thể ủy quyền cho một người trong nhóm "
                       "để giao kết hợp đồng lao động; hợp đồng phải giao kết bằng văn bản và có hiệu lực "
                       "như giao kết với từng người.",
         dieu_can_trich=["BLLD2019_D18_K0"]),
    dict(id="t005", loai="tra_cuu",
         question="Người lao động có được giao kết nhiều hợp đồng lao động cùng lúc với nhiều người sử dụng lao động không?",
         ground_truth="Có, miễn là bảo đảm thực hiện đầy đủ các nội dung đã giao kết ở mỗi hợp đồng.",
         dieu_can_trich=["BLLD2019_D19_K0"]),
    dict(id="t006", loai="tra_cuu",
         question="Hợp đồng lao động xác định thời hạn tối đa là bao nhiêu tháng?",
         ground_truth="Không quá 36 tháng kể từ thời điểm hợp đồng có hiệu lực.",
         dieu_can_trich=["BLLD2019_D20_K0"]),
    dict(id="t007", loai="tra_cuu",
         question="Người sử dụng lao động được chuyển người lao động làm công việc khác so với hợp đồng tối đa bao nhiêu ngày trong 1 năm mà không cần sự đồng ý bằng văn bản?",
         ground_truth="Không quá 60 ngày làm việc cộng dồn trong 1 năm; quá thời hạn này chỉ được thực hiện "
                       "khi người lao động đồng ý bằng văn bản.",
         dieu_can_trich=["BLLD2019_D29_K0"]),
    dict(id="t008", loai="tra_cuu",
         question="Những trường hợp nào được tạm hoãn thực hiện hợp đồng lao động?",
         ground_truth="Một số trường hợp: người lao động thực hiện nghĩa vụ quân sự/dân quân tự vệ; bị tạm "
                       "giữ, tạm giam; phải chấp hành biện pháp đưa vào trường giáo dưỡng/cơ sở cai nghiện "
                       "bắt buộc; lao động nữ mang thai theo Điều 138; được bổ nhiệm quản lý doanh nghiệp "
                       "nhà nước; được ủy quyền thực hiện quyền, trách nhiệm đại diện chủ sở hữu nhà nước...",
         dieu_can_trich=["BLLD2019_D30_K0"]),
    dict(id="t009", loai="tra_cuu",
         question="Hết thời hạn tạm hoãn hợp đồng lao động, người lao động phải có mặt tại nơi làm việc trong bao lâu?",
         ground_truth="Trong thời hạn 15 ngày kể từ ngày hết thời hạn tạm hoãn, và người sử dụng lao động "
                       "phải nhận lại người lao động nếu hợp đồng còn thời hạn (trừ thỏa thuận hoặc quy định "
                       "khác).",
         dieu_can_trich=["BLLD2019_D31_K0"]),
    dict(id="t010", loai="tra_cuu",
         question="Làm việc không trọn thời gian là gì?",
         ground_truth="Là người lao động có thời gian làm việc ngắn hơn thời gian làm việc bình thường theo "
                       "ngày/tuần/tháng theo thỏa thuận, vẫn được hưởng lương, bình đẳng về quyền, nghĩa vụ, "
                       "cơ hội và an toàn vệ sinh lao động như người làm trọn thời gian.",
         dieu_can_trich=["BLLD2019_D32_K0"]),
    dict(id="t011", loai="tra_cuu",
         question="Muốn sửa đổi, bổ sung nội dung hợp đồng lao động phải báo trước bao lâu?",
         ground_truth="Ít nhất 3 ngày làm việc trước khi đề nghị nội dung cần sửa đổi, bổ sung.",
         dieu_can_trich=["BLLD2019_D33_K0"]),
    dict(id="t012", loai="tra_cuu",
         question="Hợp đồng lao động vô hiệu toàn bộ trong những trường hợp nào?",
         ground_truth="Khi toàn bộ nội dung hợp đồng vi phạm pháp luật; người giao kết không đúng thẩm "
                       "quyền hoặc vi phạm nguyên tắc giao kết; công việc đã giao kết là công việc pháp luật "
                       "cấm.",
         dieu_can_trich=["BLLD2019_D49_K0"]),
    dict(id="t013", loai="tra_cuu",
         question="Doanh nghiệp muốn hoạt động cho thuê lại lao động cần điều kiện gì?",
         ground_truth="Phải ký quỹ và được cấp Giấy phép hoạt động cho thuê lại lao động theo quy định của "
                       "Chính phủ.",
         dieu_can_trich=["BLLD2019_D54_K0"]),
    dict(id="t014", loai="tra_cuu",
         question="Thời hạn tập nghề tối đa là bao lâu?",
         ground_truth="Không quá 3 tháng.",
         dieu_can_trich=["BLLD2019_D61_K0"]),
    dict(id="t015", loai="tra_cuu",
         question="Hợp đồng đào tạo nghề phải có những nội dung chủ yếu nào?",
         ground_truth="Nghề đào tạo; địa điểm, thời gian và tiền lương trong thời gian đào tạo; thời hạn cam "
                       "kết làm việc sau khi được đào tạo; chi phí đào tạo và trách nhiệm hoàn trả chi phí "
                       "đào tạo; và các trách nhiệm khác của các bên.",
         dieu_can_trich=["BLLD2019_D62_K0"]),
    dict(id="t016", loai="tra_cuu",
         question="Thỏa ước lao động tập thể có hiệu lực kể từ khi nào?",
         ground_truth="Do các bên thỏa thuận và ghi trong thỏa ước; nếu không thỏa thuận ngày có hiệu lực "
                       "thì có hiệu lực kể từ ngày ký kết.",
         dieu_can_trich=["BLLD2019_D78_K0"]),
    dict(id="t017", loai="tra_cuu",
         question="Mức lương tối thiểu được hiểu như thế nào?",
         ground_truth="Là mức lương thấp nhất trả cho người lao động làm công việc giản đơn nhất trong điều "
                       "kiện lao động bình thường, nhằm bảo đảm mức sống tối thiểu của người lao động và gia "
                       "đình họ; được xác lập theo vùng, ấn định theo tháng, giờ.",
         dieu_can_trich=["BLLD2019_D91_K0"]),
    dict(id="t018", loai="tra_cuu",
         question="Nguyên tắc trả lương cho người lao động là gì?",
         ground_truth="Người sử dụng lao động phải trả lương trực tiếp, đầy đủ, đúng hạn; không được hạn "
                       "chế hoặc can thiệp quyền tự quyết chi tiêu lương, không được ép người lao động chi "
                       "tiêu lương vào mua hàng hóa/dịch vụ của công ty hoặc đơn vị do công ty chỉ định.",
         dieu_can_trich=["BLLD2019_D94_K0"]),
    dict(id="t019", loai="tra_cuu",
         question="Mỗi lần trả lương, người sử dụng lao động phải làm gì?",
         ground_truth="Phải thông báo bảng kê trả lương cho người lao động, ghi rõ tiền lương, tiền lương "
                       "làm thêm giờ, tiền lương làm việc ban đêm, và nội dung, số tiền bị khấu trừ (nếu có).",
         dieu_can_trich=["BLLD2019_D95_K0"]),
    dict(id="t020", loai="tra_cuu",
         question="Lương có thể được trả bằng những hình thức nào?",
         ground_truth="Trả bằng tiền mặt hoặc chuyển khoản qua tài khoản cá nhân của người lao động tại "
                       "ngân hàng; nếu trả qua tài khoản, người sử dụng lao động phải trả các loại phí mở "
                       "tài khoản và phí chuyển tiền lương.",
         dieu_can_trich=["BLLD2019_D96_K0"]),
    dict(id="t021", loai="tra_cuu",
         question="Người lao động hưởng lương theo tháng được trả lương mấy lần trong tháng?",
         ground_truth="Được trả một tháng một lần hoặc nửa tháng một lần, thời điểm trả lương do hai bên "
                       "thỏa thuận và ấn định vào một thời điểm có tính chu kỳ.",
         dieu_can_trich=["BLLD2019_D97_K0"]),
    dict(id="t022", loai="tra_cuu",
         question="Số giờ làm thêm tối đa của người lao động là bao nhiêu trong 1 tháng và 1 năm (trường hợp thông thường)?",
         ground_truth="Không quá 40 giờ trong 1 tháng và không quá 200 giờ trong 1 năm (trừ trường hợp đặc "
                       "biệt theo khoản 3 Điều 107 được làm tới 300 giờ/năm).",
         dieu_can_trich=["BLLD2019_D107_K0"]),
    dict(id="t023", loai="tra_cuu",
         question="Trong trường hợp nào người lao động không được từ chối làm thêm giờ?",
         ground_truth="Khi thực hiện lệnh động viên/huy động bảo đảm nhiệm vụ quốc phòng, an ninh; hoặc "
                       "thực hiện công việc bảo vệ tính mạng con người, tài sản trong phòng ngừa/khắc phục "
                       "thiên tai, hỏa hoạn, dịch bệnh nguy hiểm, thảm họa (trừ trường hợp nguy hiểm đến tính "
                       "mạng, sức khỏe theo pháp luật an toàn vệ sinh lao động).",
         dieu_can_trich=["BLLD2019_D108_K0"]),
    dict(id="t024", loai="tra_cuu",
         question="Lao động nữ được nghỉ thai sản trước và sau khi sinh bao lâu?",
         ground_truth="6 tháng; thời gian nghỉ trước khi sinh không quá 2 tháng. Nếu sinh đôi trở lên thì từ "
                       "con thứ 2, mỗi con được nghỉ thêm 1 tháng.",
         dieu_can_trich=["BLLD2019_D139_K0"]),
    dict(id="t025", loai="tra_cuu",
         question="Lao động chưa thành niên là người bao nhiêu tuổi?",
         ground_truth="Là người lao động chưa đủ 18 tuổi.",
         dieu_can_trich=["BLLD2019_D143_K0"]),
    dict(id="t026", loai="tra_cuu",
         question="Khi sử dụng người chưa đủ 15 tuổi làm việc, người sử dụng lao động phải tuân theo quy định gì?",
         ground_truth="Phải giao kết hợp đồng lao động bằng văn bản với người đó VÀ người đại diện theo "
                       "pháp luật của người đó; bố trí giờ làm không ảnh hưởng học tập; có giấy khám sức "
                       "khỏe phù hợp và kiểm tra định kỳ ít nhất 6 tháng/lần; bảo đảm điều kiện làm việc phù "
                       "hợp.",
         dieu_can_trich=["BLLD2019_D145_K0"]),
    dict(id="t027", loai="tra_cuu",
         question="Thời giờ làm việc tối đa của người chưa đủ 15 tuổi là bao nhiêu?",
         ground_truth="Không quá 4 giờ trong 1 ngày và 20 giờ trong 1 tuần; không được làm thêm giờ, làm "
                       "việc ban đêm.",
         dieu_can_trich=["BLLD2019_D146_K0"]),
    dict(id="t028", loai="tra_cuu",
         question="Người sử dụng lao động sử dụng lao động là người khuyết tật phải bảo đảm điều gì?",
         ground_truth="Phải bảo đảm điều kiện lao động, công cụ lao động, an toàn vệ sinh lao động phù hợp, "
                       "tổ chức khám sức khỏe định kỳ phù hợp, và phải tham khảo ý kiến người khuyết tật khi "
                       "quyết định vấn đề liên quan đến quyền, lợi ích của họ.",
         dieu_can_trich=["BLLD2019_D159_K0"]),
    dict(id="t029", loai="tra_cuu",
         question="Hành vi nào bị nghiêm cấm khi sử dụng lao động là người khuyết tật nặng?",
         ground_truth="Cấm sử dụng người khuyết tật nhẹ suy giảm khả năng lao động từ 51% trở lên, khuyết "
                       "tật nặng hoặc đặc biệt nặng làm thêm giờ, làm việc ban đêm (trừ khi họ đồng ý); cấm "
                       "để họ làm công việc nặng nhọc, độc hại, nguy hiểm mà không có sự đồng ý sau khi đã "
                       "được cung cấp đầy đủ thông tin.",
         dieu_can_trich=["BLLD2019_D160_K0"]),
    dict(id="t030", loai="tra_cuu",
         question="Trong thời gian người lao động nghỉ hưởng chế độ bảo hiểm xã hội, người sử dụng lao động có phải trả lương không?",
         ground_truth="Không phải trả lương, trừ trường hợp hai bên có thỏa thuận khác.",
         dieu_can_trich=["BLLD2019_D168_K0"]),
    dict(id="t031", loai="tra_cuu",
         question="Cơ quan, tổ chức nào có thẩm quyền giải quyết tranh chấp lao động cá nhân?",
         ground_truth="Hòa giải viên lao động; Hội đồng trọng tài lao động; Tòa án nhân dân.",
         dieu_can_trich=["BLLD2019_D187_K0"]),
    dict(id="t032", loai="tra_cuu",
         question="Những tranh chấp lao động cá nhân nào không bắt buộc phải qua thủ tục hòa giải trước khi khởi kiện?",
         ground_truth="Một số trường hợp: xử lý kỷ luật sa thải hoặc bị đơn phương chấm dứt hợp đồng lao "
                       "động; bồi thường thiệt hại, trợ cấp khi chấm dứt hợp đồng; tranh chấp giữa người "
                       "giúp việc gia đình và người sử dụng lao động; tranh chấp về bảo hiểm xã hội/y tế...",
         dieu_can_trich=["BLLD2019_D188_K0"]),
    dict(id="t033", loai="tra_cuu",
         question="Đình công là gì?",
         ground_truth="Là sự ngừng việc tạm thời, tự nguyện và có tổ chức của người lao động nhằm đạt được "
                       "yêu cầu trong quá trình giải quyết tranh chấp lao động, do tổ chức đại diện người lao "
                       "động có quyền thương lượng tập thể tổ chức và lãnh đạo.",
         dieu_can_trich=["BLLD2019_D198_K0"]),
    dict(id="t034", loai="tra_cuu",
         question="Trong thời hạn bao lâu kể từ ngày bắt đầu hoạt động, người sử dụng lao động phải lập sổ quản lý lao động?",
         ground_truth="Trong thời hạn 30 ngày kể từ ngày bắt đầu hoạt động.",
         dieu_can_trich=["ND145_2020_D3_K0"]),
    dict(id="t035", loai="tra_cuu",
         question="Người sử dụng lao động phải định kỳ báo cáo tình hình thay đổi lao động khi nào?",
         ground_truth="Định kỳ 6 tháng (trước ngày 05/6) và hằng năm, báo cáo tình hình thay đổi lao động "
                       "với cơ quan quản lý nhà nước về lao động và cơ quan bảo hiểm xã hội.",
         dieu_can_trich=["ND145_2020_D4_K0"]),

    # ============ tinh_huong (30) ============
    dict(id="h001", loai="tinh_huong",
         question="Công ty ký hợp đồng lao động xác định thời hạn 40 tháng với tôi, có đúng luật không?",
         ground_truth="Không đúng. Hợp đồng lao động xác định thời hạn tối đa chỉ được 36 tháng.",
         dieu_can_trich=["BLLD2019_D20_K0"]),
    dict(id="h002", loai="tinh_huong",
         question="Hợp đồng lao động xác định thời hạn 24 tháng của tôi đã hết hạn, tôi vẫn tiếp tục làm "
                   "việc, 35 ngày sau công ty vẫn chưa ký hợp đồng mới, hợp đồng của tôi lúc này là loại gì?",
         ground_truth="Đã tự động trở thành hợp đồng lao động không xác định thời hạn, vì đã quá 30 ngày kể "
                       "từ ngày hợp đồng cũ hết hạn mà hai bên không ký hợp đồng mới.",
         dieu_can_trich=["BLLD2019_D20_K0"]),
    dict(id="h003", loai="tinh_huong",
         question="Công ty chuyển tôi làm công việc khác so với hợp đồng 70 ngày cộng dồn trong năm mà "
                   "không hỏi ý kiến tôi bằng văn bản, có đúng luật không?",
         ground_truth="Không đúng. Chuyển người lao động làm công việc khác chỉ được tối đa 60 ngày làm "
                       "việc cộng dồn trong 1 năm mà không cần đồng ý; quá 60 ngày phải có sự đồng ý bằng "
                       "văn bản của người lao động.",
         dieu_can_trich=["BLLD2019_D29_K0"]),
    dict(id="h004", loai="tinh_huong",
         question="Tôi hết hạn tạm hoãn hợp đồng lao động, nhưng 20 ngày sau tôi mới đến công ty, công ty "
                   "có quyền không nhận lại tôi không?",
         ground_truth="Có thể. Người lao động phải có mặt tại nơi làm việc trong 15 ngày kể từ ngày hết "
                       "thời hạn tạm hoãn; quá thời hạn này (20 ngày) mà không có thỏa thuận hoặc quy định "
                       "khác thì công ty có căn cứ không nhận lại.",
         dieu_can_trich=["BLLD2019_D31_K0"]),
    dict(id="h005", loai="tinh_huong",
         question="Công ty muốn sửa nội dung mức lương trong hợp đồng của tôi, chỉ báo tôi trước 1 ngày, có đúng luật không?",
         ground_truth="Không đúng. Muốn sửa đổi, bổ sung nội dung hợp đồng lao động phải báo trước ít nhất "
                       "3 ngày làm việc.",
         dieu_can_trich=["BLLD2019_D33_K0"]),
    dict(id="h006", loai="tinh_huong",
         question="Công ty giữ bằng đại học gốc của tôi để 'bảo đảm' tôi không nghỉ việc giữa chừng, có đúng luật không?",
         ground_truth="Không đúng. Pháp luật cấm người sử dụng lao động giữ bản chính giấy tờ tùy thân, văn "
                       "bằng, chứng chỉ của người lao động.",
         dieu_can_trich=["BLLD2019_D17_K0"]),
    dict(id="h007", loai="tinh_huong",
         question="Nhóm 5 người chúng tôi (đều trên 18 tuổi) làm việc mùa vụ 8 tháng, muốn ủy quyền 1 "
                   "người ký hợp đồng lao động chung, có được không?",
         ground_truth="Được. Đây là công việc mùa vụ dưới 12 tháng và cả nhóm đều từ đủ 18 tuổi trở lên, đủ "
                       "điều kiện ủy quyền cho 1 người ký hợp đồng lao động chung bằng văn bản.",
         dieu_can_trich=["BLLD2019_D18_K0"]),
    dict(id="h008", loai="tinh_huong",
         question="Tôi được nhận vào tập nghề tại công ty trong 4 tháng, có đúng luật không?",
         ground_truth="Không đúng. Thời hạn tập nghề tối đa chỉ được 3 tháng.",
         dieu_can_trich=["BLLD2019_D61_K0"]),
    dict(id="h009", loai="tinh_huong",
         question="Công ty cử tôi đi đào tạo ở nước ngoài bằng chi phí công ty nhưng chỉ thỏa thuận miệng, "
                   "không ký hợp đồng đào tạo nghề, có đúng luật không?",
         ground_truth="Không đúng. Khi người lao động được đào tạo nâng cao bằng kinh phí của người sử dụng "
                       "lao động, hai bên phải ký kết hợp đồng đào tạo nghề bằng văn bản (làm thành 2 bản).",
         dieu_can_trich=["BLLD2019_D62_K0"]),
    dict(id="h010", loai="tinh_huong",
         question="Tôi hưởng lương theo tháng, công ty trả lương 2 tháng một lần, có đúng luật không?",
         ground_truth="Không đúng. Người lao động hưởng lương theo tháng phải được trả lương ít nhất một "
                       "tháng một lần (hoặc nửa tháng một lần).",
         dieu_can_trich=["BLLD2019_D97_K0"]),
    dict(id="h011", loai="tinh_huong",
         question="Công ty trả lương qua tài khoản ngân hàng nhưng bắt tôi tự trả phí mở tài khoản và phí "
                   "chuyển tiền, có đúng luật không?",
         ground_truth="Không đúng. Nếu trả lương qua tài khoản cá nhân tại ngân hàng, người sử dụng lao "
                       "động phải trả các loại phí liên quan đến việc mở tài khoản và chuyển tiền lương.",
         dieu_can_trich=["BLLD2019_D96_K0"]),
    dict(id="h012", loai="tinh_huong",
         question="Tháng này tôi đã làm thêm 45 giờ, công ty (không thuộc ngành nghề đặc thù) muốn tôi làm "
                   "thêm nữa trong tháng, có đúng luật không?",
         ground_truth="Không đúng. Số giờ làm thêm không được quá 40 giờ trong 1 tháng đối với trường hợp "
                       "thông thường (không thuộc các ngành nghề đặc thù được phép tới 300 giờ/năm).",
         dieu_can_trich=["BLLD2019_D107_K0"]),
    dict(id="h013", loai="tinh_huong",
         question="Công ty yêu cầu tôi làm thêm giờ để khắc phục hậu quả bão lũ khẩn cấp, tôi có quyền từ chối không?",
         ground_truth="Không. Đây là trường hợp làm thêm giờ đặc biệt (khắc phục hậu quả thiên tai) mà "
                       "người lao động không được từ chối, và không bị giới hạn số giờ làm thêm như thông "
                       "thường.",
         dieu_can_trich=["BLLD2019_D108_K0"]),
    dict(id="h014", loai="tinh_huong",
         question="Tôi sinh đôi, tôi được nghỉ thai sản tổng cộng bao lâu?",
         ground_truth="7 tháng: 6 tháng theo quy định chung, cộng thêm 1 tháng cho con thứ 2 trở đi khi sinh "
                       "đôi trở lên.",
         dieu_can_trich=["BLLD2019_D139_K0"]),
    dict(id="h015", loai="tinh_huong",
         question="Công ty nhận một em 14 tuổi vào làm việc nhưng chỉ ký hợp đồng lao động với em, không "
                   "ký với cha mẹ hoặc người giám hộ, có đúng luật không?",
         ground_truth="Không đúng. Khi sử dụng người chưa đủ 15 tuổi, phải giao kết hợp đồng lao động bằng "
                       "văn bản với cả người đó VÀ người đại diện theo pháp luật của người đó.",
         dieu_can_trich=["BLLD2019_D145_K0"]),
    dict(id="h016", loai="tinh_huong",
         question="Một em 14 tuổi làm việc 5 giờ/ngày cho một xưởng nhỏ, có đúng luật không?",
         ground_truth="Không đúng. Thời giờ làm việc của người chưa đủ 15 tuổi không được quá 4 giờ/ngày và "
                       "20 giờ/tuần.",
         dieu_can_trich=["BLLD2019_D146_K0"]),
    dict(id="h017", loai="tinh_huong",
         question="Công ty bắt nhân viên khuyết tật nặng làm ca đêm mà không hỏi ý kiến họ, có đúng luật không?",
         ground_truth="Không đúng. Pháp luật cấm sử dụng người khuyết tật nặng hoặc đặc biệt nặng làm việc "
                       "ban đêm, trừ khi chính người khuyết tật đó đồng ý.",
         dieu_can_trich=["BLLD2019_D160_K0"]),
    dict(id="h018", loai="tinh_huong",
         question="Tôi bị sa thải, muốn khởi kiện thẳng ra tòa mà không qua hòa giải viên lao động trước, có được không?",
         ground_truth="Được. Tranh chấp về xử lý kỷ luật sa thải là một trong các trường hợp không bắt buộc "
                       "phải qua thủ tục hòa giải trước khi khởi kiện.",
         dieu_can_trich=["BLLD2019_D188_K0"]),
    dict(id="h019", loai="tinh_huong",
         question="Tôi đang nghỉ hưởng chế độ ốm đau do bảo hiểm xã hội chi trả, công ty có phải trả thêm "
                   "lương cho tôi trong thời gian đó không?",
         ground_truth="Không phải, trừ khi hai bên có thỏa thuận khác.",
         dieu_can_trich=["BLLD2019_D168_K0"]),
    dict(id="h020", loai="tinh_huong",
         question="Công ty trả lương cho tôi hằng tháng nhưng không đưa bảng kê chi tiết các khoản khấu trừ, có đúng luật không?",
         ground_truth="Không đúng. Mỗi lần trả lương, người sử dụng lao động phải thông báo bảng kê trả "
                       "lương, ghi rõ lương, lương làm thêm giờ, lương ban đêm và các khoản khấu trừ (nếu có).",
         dieu_can_trich=["BLLD2019_D95_K0"]),
    dict(id="h021", loai="tinh_huong",
         question="Công ty ép tôi phải dùng một phần lương của mình để mua sản phẩm do công ty sản xuất, có đúng luật không?",
         ground_truth="Không đúng. Pháp luật cấm người sử dụng lao động ép buộc người lao động chi tiêu "
                       "lương vào việc mua hàng hóa, dịch vụ của công ty hoặc đơn vị do công ty chỉ định.",
         dieu_can_trich=["BLLD2019_D94_K0"]),
    dict(id="h022", loai="tinh_huong",
         question="Tôi đang có hợp đồng lao động với công ty A, tôi có được ký thêm hợp đồng lao động bán thời gian với công ty B không?",
         ground_truth="Được. Người lao động có thể giao kết nhiều hợp đồng lao động với nhiều người sử dụng "
                       "lao động, miễn bảo đảm thực hiện đầy đủ nội dung đã giao kết ở mỗi hợp đồng.",
         dieu_can_trich=["BLLD2019_D19_K0"]),
    dict(id="h023", loai="tinh_huong",
         question="Tôi bị tạm giam để phục vụ điều tra hình sự, hợp đồng lao động của tôi với công ty sẽ ra sao?",
         ground_truth="Hợp đồng lao động được tạm hoãn thực hiện (không phải chấm dứt), vì bị tạm giữ, tạm "
                       "giam theo quy định pháp luật tố tụng hình sự là một căn cứ tạm hoãn hợp đồng.",
         dieu_can_trich=["BLLD2019_D30_K0"]),
    dict(id="h024", loai="tinh_huong",
         question="Tôi làm việc 4 giờ/ngày (không trọn thời gian) theo thỏa thuận, tôi có bị đối xử bất "
                   "bình đẳng về quyền lợi so với người làm trọn thời gian không?",
         ground_truth="Không được phép đối xử bất bình đẳng. Người làm việc không trọn thời gian vẫn được "
                       "hưởng lương, bình đẳng trong thực hiện quyền/nghĩa vụ, cơ hội và an toàn vệ sinh lao "
                       "động như người làm trọn thời gian.",
         dieu_can_trich=["BLLD2019_D32_K0"]),
    dict(id="h025", loai="tinh_huong",
         question="Một công ty muốn kinh doanh dịch vụ cho thuê lại lao động nhưng không ký quỹ, không xin giấy phép, có được hoạt động không?",
         ground_truth="Không được. Doanh nghiệp cho thuê lại lao động bắt buộc phải ký quỹ và được cấp Giấy "
                       "phép hoạt động cho thuê lại lao động.",
         dieu_can_trich=["BLLD2019_D54_K0"]),
    dict(id="h026", loai="tinh_huong",
         question="Bạn tôi 17 tuổi đi làm, có được xem là lao động chưa thành niên không?",
         ground_truth="Có. Lao động chưa thành niên là người lao động chưa đủ 18 tuổi.",
         dieu_can_trich=["BLLD2019_D143_K0"]),
    dict(id="h027", loai="tinh_huong",
         question="Hợp đồng lao động được ký bởi một người không có thẩm quyền đại diện cho công ty, giá trị pháp lý của hợp đồng này thế nào?",
         ground_truth="Hợp đồng vô hiệu toàn bộ, vì người giao kết không đúng thẩm quyền là một trong các "
                       "căn cứ làm hợp đồng lao động vô hiệu toàn bộ.",
         dieu_can_trich=["BLLD2019_D49_K0"]),
    dict(id="h028", loai="tinh_huong",
         question="Một nhóm công nhân tự phát ngừng việc, không do tổ chức đại diện người lao động lãnh đạo, có được coi là đình công hợp pháp không?",
         ground_truth="Không được coi là đình công theo định nghĩa của luật, vì đình công phải có tổ chức "
                       "và do tổ chức đại diện người lao động có quyền thương lượng tập thể tổ chức, lãnh "
                       "đạo; ngừng việc tự phát không đáp ứng điều kiện này.",
         dieu_can_trich=["BLLD2019_D198_K0"]),
    dict(id="h029", loai="tinh_huong",
         question="Công ty tuyển lao động là người khuyết tật nhưng không tổ chức khám sức khỏe định kỳ phù hợp cho họ, có đúng luật không?",
         ground_truth="Không đúng. Người sử dụng lao động phải bảo đảm điều kiện lao động, công cụ lao động, "
                       "an toàn vệ sinh lao động và tổ chức khám sức khỏe định kỳ phù hợp với người lao động "
                       "là người khuyết tật.",
         dieu_can_trich=["BLLD2019_D159_K0"]),
    dict(id="h030", loai="tinh_huong",
         question="Tôi làm việc theo chế độ tính giờ theo tuần, công ty cho tôi làm thêm giờ khiến tổng "
                   "thời gian làm việc bình thường cộng thêm giờ lên tới 13 giờ trong một ngày, có đúng luật không?",
         ground_truth="Không đúng. Nếu áp dụng thời giờ làm việc bình thường theo tuần, tổng số giờ làm "
                       "việc bình thường và giờ làm thêm không được quá 12 giờ trong 1 ngày.",
         dieu_can_trich=["BLLD2019_D107_K0"]),

    # ============ nhieu_dieu (20) ============
    dict(id="n001", loai="nhieu_dieu",
         question="Em 14 tuổi muốn đi làm thêm hè tại một xưởng nhỏ, công ty cần chuẩn bị giấy tờ gì và tối đa được làm bao nhiêu giờ/ngày?",
         ground_truth="Công ty phải giao kết hợp đồng lao động bằng văn bản với cả em và cha/mẹ hoặc người "
                       "giám hộ, có giấy khám sức khỏe phù hợp và kiểm tra định kỳ ít nhất 6 tháng/lần, bố "
                       "trí giờ làm không ảnh hưởng việc học. Thời giờ làm việc tối đa là 4 giờ/ngày và 20 "
                       "giờ/tuần, không được làm thêm giờ hay làm việc ban đêm.",
         dieu_can_trich=["BLLD2019_D145_K0", "BLLD2019_D146_K0"]),
    dict(id="n002", loai="nhieu_dieu",
         question="Tôi tạm hoãn hợp đồng lao động để đi nghĩa vụ quân sự, khi xuất ngũ tôi có phải quay lại công ty ngay không và trong bao lâu?",
         ground_truth="Thực hiện nghĩa vụ quân sự là một căn cứ hợp lệ để tạm hoãn hợp đồng lao động. Khi "
                       "hết thời hạn tạm hoãn (xuất ngũ), người lao động phải có mặt tại nơi làm việc trong "
                       "15 ngày, và công ty phải nhận lại nếu hợp đồng còn thời hạn.",
         dieu_can_trich=["BLLD2019_D30_K0", "BLLD2019_D31_K0"]),
    dict(id="n003", loai="nhieu_dieu",
         question="Tôi ký hợp đồng đào tạo nghề cam kết làm việc 3 năm sau khi công ty cử đi học, nhưng tôi "
                   "tự ý nghỉ việc ngay sau khóa học mà không báo trước đúng hạn, tôi phải chịu trách nhiệm gì?",
         ground_truth="Đây là đơn phương chấm dứt hợp đồng lao động trái pháp luật (vi phạm nghĩa vụ báo "
                       "trước). Theo hợp đồng đào tạo nghề đã ký, người lao động phải hoàn trả chi phí đào "
                       "tạo; ngoài ra còn không được trợ cấp thôi việc và phải bồi thường nửa tháng tiền "
                       "lương cùng khoản tiền tương ứng những ngày không báo trước.",
         dieu_can_trich=["BLLD2019_D62_K0", "BLLD2019_D40_K0"]),
    dict(id="n004", loai="nhieu_dieu",
         question="Tôi làm việc không trọn thời gian (4 giờ/ngày theo thỏa thuận), công ty có phải đóng "
                   "bảo hiểm xã hội bắt buộc cho tôi như người làm trọn thời gian không?",
         ground_truth="Có. Người làm việc không trọn thời gian được bình đẳng về quyền và nghĩa vụ như "
                       "người làm trọn thời gian, và người sử dụng lao động, người lao động đều phải tham "
                       "gia bảo hiểm xã hội bắt buộc, bảo hiểm y tế, bảo hiểm thất nghiệp theo quy định.",
         dieu_can_trich=["BLLD2019_D32_K0", "BLLD2019_D168_K0"]),
    dict(id="n005", loai="nhieu_dieu",
         question="Một công ty muốn cho tôi làm việc theo hình thức thuê lại lao động tại một doanh nghiệp "
                   "khác, công ty đó cần đáp ứng điều kiện gì và hợp đồng thuê lại phải có nội dung gì?",
         ground_truth="Doanh nghiệp cho thuê lại lao động phải ký quỹ và được cấp Giấy phép hoạt động cho "
                       "thuê lại lao động. Hợp đồng cho thuê lại lao động phải lập bằng văn bản (2 bản), gồm "
                       "địa điểm, vị trí việc làm, nội dung công việc, thời hạn thuê lại, thời giờ làm việc/"
                       "nghỉ ngơi, điều kiện an toàn vệ sinh lao động tại nơi làm việc...",
         dieu_can_trich=["BLLD2019_D54_K0", "BLLD2019_D55_K0"]),
    dict(id="n006", loai="nhieu_dieu",
         question="Tôi là lao động khuyết tật nặng, công ty bố trí tôi làm ca đêm liên tục 7 giờ dù tôi "
                   "không đồng ý, công ty vi phạm những gì?",
         ground_truth="Vi phạm quy định cấm sử dụng lao động khuyết tật nặng làm việc ban đêm khi chưa được "
                       "họ đồng ý. Ngoài ra nếu vẫn làm việc ban đêm liên tục từ 6 giờ trở lên thì còn phải "
                       "được nghỉ giữa giờ ít nhất 45 phút liên tục, nếu công ty không bố trí thì vi phạm cả "
                       "quy định nghỉ giữa giờ.",
         dieu_can_trich=["BLLD2019_D160_K0", "BLLD2019_D109_K0"]),
    dict(id="n007", loai="nhieu_dieu",
         question="Công ty giữ bằng đại học gốc của tôi không trả dù tôi đã nghỉ việc đúng luật, tôi cần "
                   "khởi kiện ở đâu và có bắt buộc hòa giải trước không?",
         ground_truth="Việc công ty giữ bằng gốc là vi phạm quy định cấm giữ giấy tờ tùy thân, văn bằng, "
                       "chứng chỉ của người lao động. Tranh chấp này không thuộc các trường hợp được miễn "
                       "thủ tục hòa giải, nên phải hòa giải qua hòa giải viên lao động trước; nếu không "
                       "thành mới được yêu cầu Hội đồng trọng tài lao động hoặc Tòa án nhân dân giải quyết.",
         dieu_can_trich=["BLLD2019_D17_K0", "BLLD2019_D188_K0"]),
    dict(id="n008", loai="nhieu_dieu",
         question="Nhóm 6 người chúng tôi làm việc mùa vụ 5 tháng muốn ủy quyền 1 người ký hợp đồng lao "
                   "động chung, trong nhóm có 1 bạn 17 tuổi, việc ủy quyền này có áp dụng được với bạn 17 tuổi không?",
         ground_truth="Không áp dụng được với bạn 17 tuổi. Việc ủy quyền ký hợp đồng lao động chung chỉ áp "
                       "dụng cho nhóm người lao động từ đủ 18 tuổi trở lên; bạn 17 tuổi là lao động chưa "
                       "thành niên (chưa đủ 18 tuổi) nên phải giao kết hợp đồng lao động riêng theo quy định "
                       "dành cho lao động chưa thành niên.",
         dieu_can_trich=["BLLD2019_D18_K0", "BLLD2019_D143_K0"]),
    dict(id="n009", loai="nhieu_dieu",
         question="Tôi ký đồng thời 2 hợp đồng lao động với 2 công ty khác nhau, việc đóng bảo hiểm xã hội/"
                   "y tế/thất nghiệp của tôi được xử lý thế nào?",
         ground_truth="Pháp luật lao động cho phép giao kết nhiều hợp đồng lao động cùng lúc. Việc tham gia "
                       "bảo hiểm xã hội, bảo hiểm y tế, bảo hiểm thất nghiệp khi có nhiều hợp đồng lao động "
                       "được thực hiện theo quy định của pháp luật về bảo hiểm xã hội, bảo hiểm y tế, bảo "
                       "hiểm thất nghiệp — chi tiết mức đóng cụ thể thuộc phạm vi Luật Bảo hiểm xã hội, "
                       "ngoài phạm vi 3 văn bản dữ liệu hiện có của agent.",
         dieu_can_trich=["BLLD2019_D19_K0", "BLLD2019_D168_K0"]),
    dict(id="n010", loai="nhieu_dieu",
         question="Công ty tôi thay đổi cơ cấu tổ chức, tạm thời chuyển tôi làm công việc khác 70 ngày "
                   "cộng dồn trong năm nhưng không xin tôi đồng ý bằng văn bản, sau đó cho tôi thôi việc "
                   "luôn với lý do 'không còn vị trí phù hợp', công ty đã vi phạm những gì?",
         ground_truth="Việc chuyển công việc khác quá 60 ngày cộng dồn trong năm mà không có sự đồng ý bằng "
                       "văn bản là vi phạm. Nếu công ty cho thôi việc vì thay đổi cơ cấu tổ chức thì đây là "
                       "trường hợp chấm dứt hợp đồng theo diện thay đổi cơ cấu, công nghệ, người lao động "
                       "được hưởng trợ cấp mất việc làm (không phải bị sa thải tùy tiện).",
         dieu_can_trich=["BLLD2019_D29_K0", "BLLD2019_D34_K0", "BLLD2019_D42_K0"]),
    dict(id="n011", loai="nhieu_dieu",
         question="Công ty trả lương cho tôi qua tài khoản ngân hàng nhưng không đưa bảng kê lương, đồng "
                   "thời yêu cầu tôi phải chi tiêu một phần lương để mua sản phẩm của công ty, công ty vi "
                   "phạm những nguyên tắc nào về tiền lương?",
         ground_truth="Vi phạm 2 nguyên tắc: (1) không được ép buộc người lao động chi tiêu lương vào mua "
                       "hàng hóa, dịch vụ của công ty; (2) mỗi lần trả lương phải thông báo bảng kê trả "
                       "lương cho người lao động.",
         dieu_can_trich=["BLLD2019_D94_K0", "BLLD2019_D95_K0"]),
    dict(id="n012", loai="nhieu_dieu",
         question="Công ty (không thuộc ngành nghề đặc thù) yêu cầu tôi làm thêm giờ để khắc phục sự cố "
                   "cháy nổ khẩn cấp dù đã vượt quá 200 giờ/năm, tôi có quyền từ chối không?",
         ground_truth="Không có quyền từ chối. Khắc phục hậu quả hỏa hoạn là trường hợp làm thêm giờ đặc "
                       "biệt, không bị giới hạn bởi mức trần 200 giờ/năm (hoặc 300 giờ/năm) áp dụng cho "
                       "trường hợp thông thường, và người lao động không được từ chối trong trường hợp này.",
         dieu_can_trich=["BLLD2019_D107_K0", "BLLD2019_D108_K0"]),
    dict(id="n013", loai="nhieu_dieu",
         question="Tôi đang nghỉ thai sản đúng luật, nhưng công ty đã sa thải tôi trong thời gian đó với lý do 'tái cơ cấu nhân sự', có đúng luật không?",
         ground_truth="Không đúng luật. Người lao động nữ có quyền nghỉ thai sản 6 tháng theo luật, và pháp "
                       "luật cấm người sử dụng lao động sa thải hoặc đơn phương chấm dứt hợp đồng lao động "
                       "vì lý do thai sản/nghỉ thai sản.",
         dieu_can_trich=["BLLD2019_D139_K0", "BLLD2019_D137_K0"]),
    dict(id="n014", loai="nhieu_dieu",
         question="Tôi tranh chấp về khoản bồi thường khi công ty đơn phương chấm dứt hợp đồng lao động "
                   "trái luật, tôi có bắt buộc phải qua hòa giải viên lao động trước khi khởi kiện ra tòa không?",
         ground_truth="Không bắt buộc. Tranh chấp về bồi thường thiệt hại, trợ cấp khi chấm dứt hợp đồng "
                       "lao động là một trong các trường hợp không bắt buộc phải qua thủ tục hòa giải, có "
                       "thể khởi kiện thẳng ra Tòa án nhân dân.",
         dieu_can_trich=["BLLD2019_D188_K0", "BLLD2019_D187_K0"]),
    dict(id="n015", loai="nhieu_dieu",
         question="Tôi là người giúp việc gia đình, tranh chấp với chủ nhà về tiền lương chưa trả, tôi có bắt buộc hòa giải trước khi khởi kiện không?",
         ground_truth="Không bắt buộc. Tranh chấp giữa người giúp việc gia đình với người sử dụng lao động "
                       "là một trong các trường hợp không bắt buộc phải qua thủ tục hòa giải trước khi yêu "
                       "cầu Hội đồng trọng tài lao động hoặc Tòa án giải quyết.",
         dieu_can_trich=["BLLD2019_D188_K0", "BLLD2019_D187_K0"]),
    dict(id="n016", loai="nhieu_dieu",
         question="Tôi bị tai nạn lao động phải nghỉ điều trị hưởng chế độ bảo hiểm xã hội, công ty có phải "
                   "trả lương cho tôi trong thời gian đó không, và công ty có được lấy lý do tôi nghỉ dài "
                   "ngày để đơn phương chấm dứt hợp đồng ngay bây giờ không?",
         ground_truth="Trong thời gian nghỉ hưởng chế độ bảo hiểm xã hội, công ty không phải trả lương (trừ "
                       "thỏa thuận khác). Tuy nhiên công ty chỉ được đơn phương chấm dứt hợp đồng vì lý do "
                       "ốm đau/tai nạn khi người lao động đã điều trị liên tục đủ thời hạn luật định (12 "
                       "tháng với hợp đồng không xác định thời hạn, 6 tháng với hợp đồng 12-36 tháng, hoặc "
                       "quá nửa thời hạn với hợp đồng dưới 12 tháng) — nếu chưa đủ thời hạn đó thì chưa được "
                       "chấm dứt ngay.",
         dieu_can_trich=["BLLD2019_D168_K0", "BLLD2019_D36_K0"]),
    dict(id="n017", loai="nhieu_dieu",
         question="Một nhóm 5 người làm việc mùa vụ, trong đó có 1 em 14 tuổi, công ty có thể để em này nằm "
                   "trong nhóm ủy quyền ký hợp đồng lao động chung không, và nếu không thì phải làm gì?",
         ground_truth="Không được. Ủy quyền ký hợp đồng lao động chung chỉ áp dụng cho người từ đủ 18 tuổi "
                       "trở lên. Với em 14 tuổi (chưa đủ 15 tuổi), công ty phải ký hợp đồng lao động riêng "
                       "bằng văn bản với cả em và người đại diện theo pháp luật của em.",
         dieu_can_trich=["BLLD2019_D18_K0", "BLLD2019_D145_K0"]),
    dict(id="n018", loai="nhieu_dieu",
         question="Công ty trả lương cho tôi theo hình thức khoán sản phẩm, công việc kéo dài nhiều tháng, "
                   "công ty có phải tạm ứng lương hằng tháng cho tôi không?",
         ground_truth="Có. Với hình thức trả lương khoán, nếu công việc phải làm trong nhiều tháng thì "
                       "hằng tháng người lao động được tạm ứng tiền lương theo khối lượng công việc đã làm "
                       "trong tháng.",
         dieu_can_trich=["BLLD2019_D96_K0", "BLLD2019_D97_K0"]),
    dict(id="n019", loai="nhieu_dieu",
         question="Công ty đơn phương sửa đổi mức lương trong hợp đồng của tôi mà không thỏa thuận trước, "
                   "tôi không đồng ý nên nghỉ việc ngay lập tức, tôi có bị coi là đơn phương chấm dứt hợp "
                   "đồng trái luật không?",
         ground_truth="Không bị coi là trái luật. Muốn sửa đổi hợp đồng lao động phải có sự thỏa thuận của "
                       "cả hai bên; nếu không thỏa thuận được thì phải tiếp tục thực hiện hợp đồng cũ, công "
                       "ty không được tự ý sửa. Khi người sử dụng lao động không bảo đảm điều kiện đã thỏa "
                       "thuận, người lao động có quyền đơn phương chấm dứt hợp đồng mà không cần báo trước.",
         dieu_can_trich=["BLLD2019_D33_K0", "BLLD2019_D35_K0"]),
    dict(id="n020", loai="nhieu_dieu",
         question="Công ty nhận một em 16 tuổi vào làm việc nhưng không có sự đồng ý của cha mẹ, cũng "
                   "không lập sổ theo dõi riêng cho em, có đúng luật không?",
         ground_truth="Không đúng. Em 16 tuổi là lao động chưa thành niên; khi sử dụng lao động chưa thành "
                       "niên, người sử dụng lao động phải có sự đồng ý của cha, mẹ hoặc người giám hộ, và "
                       "phải lập sổ theo dõi riêng ghi đầy đủ thông tin của người lao động.",
         dieu_can_trich=["BLLD2019_D143_K0", "BLLD2019_D144_K0"]),

    # ============ ngoai_pham_vi (15) ============
    dict(id="o001", loai="ngoai_pham_vi",
         question="Thủ tục thừa kế tài sản khi không có di chúc như thế nào?",
         ground_truth="Thuộc lĩnh vực dân sự/thừa kế, ngoài phạm vi Luật Lao động. Nên tham khảo luật sư "
                       "hoặc quy định về thừa kế trong Bộ luật Dân sự.",
         dieu_can_trich=[]),
    dict(id="o002", loai="ngoai_pham_vi",
         question="Tôi muốn đăng ký kinh doanh hộ cá thể, cần giấy tờ gì?",
         ground_truth="Thuộc lĩnh vực đăng ký kinh doanh, ngoài phạm vi Luật Lao động. Nên liên hệ cơ quan "
                       "đăng ký kinh doanh cấp huyện hoặc tham khảo Luật Doanh nghiệp.",
         dieu_can_trich=[]),
    dict(id="o003", loai="ngoai_pham_vi",
         question="Hợp đồng mua bán nhà đất cần công chứng ở đâu?",
         ground_truth="Thuộc lĩnh vực đất đai/dân sự, ngoài phạm vi Luật Lao động. Nên tham khảo văn phòng "
                       "công chứng hoặc quy định pháp luật đất đai.",
         dieu_can_trich=[]),
    dict(id="o004", loai="ngoai_pham_vi",
         question="Tôi bị hàng xóm gây ồn ào ban đêm, tôi có thể báo công an phường không?",
         ground_truth="Thuộc lĩnh vực an ninh trật tự/hành chính, ngoài phạm vi Luật Lao động. Có thể liên "
                       "hệ công an phường hoặc chính quyền địa phương.",
         dieu_can_trich=[]),
    dict(id="o005", loai="ngoai_pham_vi",
         question="Thủ tục xin visa du lịch sang Nhật Bản cần gì?",
         ground_truth="Thuộc lĩnh vực xuất nhập cảnh, ngoài phạm vi Luật Lao động. Nên tham khảo Đại sứ "
                       "quán/Lãnh sự quán Nhật Bản.",
         dieu_can_trich=[]),
    dict(id="o006", loai="ngoai_pham_vi",
         question="Tôi muốn nhận con nuôi, thủ tục pháp lý thế nào?",
         ground_truth="Thuộc lĩnh vực hôn nhân và gia đình/nuôi con nuôi, ngoài phạm vi Luật Lao động. Nên "
                       "tham khảo Luật Nuôi con nuôi hoặc cơ quan tư pháp địa phương.",
         dieu_can_trich=[]),
    dict(id="o007", loai="ngoai_pham_vi",
         question="Mức phạt vi phạm nồng độ cồn khi lái xe máy là bao nhiêu?",
         ground_truth="Thuộc lĩnh vực giao thông đường bộ, ngoài phạm vi Luật Lao động. Nên tham khảo Nghị "
                       "định xử phạt vi phạm hành chính về giao thông đường bộ.",
         dieu_can_trich=[]),
    dict(id="o008", loai="ngoai_pham_vi",
         question="Tôi muốn khởi kiện đòi nợ cá nhân (không liên quan lao động), cần nộp đơn ở đâu?",
         ground_truth="Thuộc lĩnh vực dân sự, ngoài phạm vi Luật Lao động. Nên tham khảo Bộ luật Tố tụng "
                       "dân sự hoặc nộp đơn tại Tòa án nhân dân có thẩm quyền.",
         dieu_can_trich=[]),
    dict(id="o009", loai="ngoai_pham_vi",
         question="Thủ tục đăng ký bảo hộ nhãn hiệu (thương hiệu) như thế nào?",
         ground_truth="Thuộc lĩnh vực sở hữu trí tuệ, ngoài phạm vi Luật Lao động. Nên tham khảo Cục Sở hữu "
                       "trí tuệ hoặc Luật Sở hữu trí tuệ.",
         dieu_can_trich=[]),
    dict(id="o010", loai="ngoai_pham_vi",
         question="Tôi muốn xin giấy phép xây dựng nhà ở, cần liên hệ cơ quan nào?",
         ground_truth="Thuộc lĩnh vực xây dựng, ngoài phạm vi Luật Lao động. Nên liên hệ Phòng Quản lý đô "
                       "thị hoặc UBND cấp huyện nơi xây dựng.",
         dieu_can_trich=[]),
    dict(id="o011", loai="ngoai_pham_vi",
         question="Luật bảo vệ người tiêu dùng quy định gì về đổi trả hàng hóa?",
         ground_truth="Thuộc lĩnh vực bảo vệ người tiêu dùng, ngoài phạm vi Luật Lao động. Nên tham khảo "
                       "Luật Bảo vệ quyền lợi người tiêu dùng.",
         dieu_can_trich=[]),
    dict(id="o012", loai="ngoai_pham_vi",
         question="Tôi muốn thành lập một quỹ từ thiện, thủ tục pháp lý ra sao?",
         ground_truth="Thuộc lĩnh vực quỹ xã hội/từ thiện, ngoài phạm vi Luật Lao động. Nên tham khảo Nghị "
                       "định về tổ chức, hoạt động của quỹ xã hội, quỹ từ thiện.",
         dieu_can_trich=[]),
    dict(id="o013", loai="ngoai_pham_vi",
         question="Mức án phạt cho tội trộm cắp tài sản theo Bộ luật Hình sự là gì?",
         ground_truth="Thuộc lĩnh vực hình sự, ngoài phạm vi Luật Lao động. Nên tham khảo Bộ luật Hình sự "
                       "hoặc luật sư hình sự.",
         dieu_can_trich=[]),
    dict(id="o014", loai="ngoai_pham_vi",
         question="Tôi muốn xin cấp lại hộ chiếu bị mất, cần làm gì?",
         ground_truth="Thuộc lĩnh vực xuất nhập cảnh/hộ tịch, ngoài phạm vi Luật Lao động. Nên liên hệ cơ "
                       "quan quản lý xuất nhập cảnh.",
         dieu_can_trich=[]),
    dict(id="o015", loai="ngoai_pham_vi",
         question="Quy định về đăng ký tạm trú tạm vắng khi chuyển nơi ở là gì?",
         ground_truth="Thuộc lĩnh vực cư trú/hành chính, ngoài phạm vi Luật Lao động. Nên liên hệ công an "
                       "phường/xã nơi cư trú.",
         dieu_can_trich=[]),
]


def main() -> None:
    known_ids = {json.loads(line)["id"] for line in CHUNKS_PATH.open(encoding="utf-8")}

    missing = []
    for item in TEST_SET:
        for cid in item["dieu_can_trich"]:
            if cid not in known_ids:
                missing.append((item["id"], cid))
    if missing:
        raise SystemExit(f"Cac id khong ton tai trong chunks.jsonl: {missing}")

    counts: dict[str, int] = {}
    for item in TEST_SET:
        counts[item["loai"]] = counts.get(item["loai"], 0) + 1
    assert len(TEST_SET) == 100, f"Can 100 cau, hien co {len(TEST_SET)}"
    expected_counts = {"tra_cuu": 35, "tinh_huong": 30, "nhieu_dieu": 20, "ngoai_pham_vi": 15}
    assert counts == expected_counts, f"Phan bo sai: {counts}, can {expected_counts}"
    print("Phan bo theo loai:", counts)

    dev_path = CHUNKS_PATH.parent.parent / "eval" / "dev.jsonl"
    dev_questions = {json.loads(line)["question"] for line in dev_path.open(encoding="utf-8")}
    overlap = [item["id"] for item in TEST_SET if item["question"] in dev_questions]
    if overlap:
        raise SystemExit(f"Cau hoi trung voi dev.jsonl: {overlap}")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUT_PATH.open("w", encoding="utf-8") as f:
        for item in TEST_SET:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
    print(f"Da ghi {len(TEST_SET)} cau vao {OUT_PATH}")


if __name__ == "__main__":
    main()
