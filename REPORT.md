# BÁO CÁO THỰC HÀNH MLOPS LAB (DAY 21 - CI/CD CHO AI SYSTEMS)

- **Học viên**: Nguyễn Văn Duy
- **Mã học viên**: 2A202601749
- **Khóa học**: AIInAction - VinUni (K3)
- **Repository URL**: https://github.com/DuyNguyen91/Track2-Day21-2A202601749-NguyenVanDuy

---

## 1. Kết Quả Thí Nghiệm & Lựa Chọn Siêu Tham Số (Bước 1)

Trong quá trình thực nghiệm cục bộ và theo dõi bằng MLflow, mô hình **RandomForestClassifier** đã được huấn luyện qua nhiều bộ siêu tham số khác nhau:

| Lần chạy | Siêu tham số (`n_estimators`, `max_depth`, `min_samples_split`) | Accuracy | F1-Score |
|---|---|:---:|:---:|
| **Thí nghiệm 1** | `n_estimators: 50`, `max_depth: 3`, `min_samples_split: 2` | 0.5580 | 0.5185 |
| **Thí nghiệm 2** | `n_estimators: 100`, `max_depth: 5`, `min_samples_split: 2` | 0.5640 | 0.5534 |
| **Thí nghiệm 3 (Tốt nhất)** | `n_estimators: 200`, `max_depth: 20`, `min_samples_split: 2` | **0.6440** | **0.6417** |

### Lý do lựa chọn bộ siêu tham số tốt nhất:
- Khi tăng `max_depth` từ `3` lên `20` và `n_estimators` lên `200`, mô hình học được các ranh giới phân loại phi tuyến tính phức tạp hơn giữa các đặc trưng hóa học của rượu vang (độ cồn, độ axit, sunphat,...).
- Độ chính xác (`Accuracy`) tăng từ **55.80%** lên **64.40%** và `F1-Score` tăng lên **64.17%**, giúp mô hình có khả năng khái quát hóa tốt nhất trên tập `eval.csv`. Bộ tham số này được lưu vào `params.yaml` cho toàn bộ pipeline CI/CD.

---

## 2. Kết Quả Pipeline CI/CD & Huấn Luyện Liên Tục (Bước 2 & Bước 3)

Hệ thống được triển khai trên nền tảng **AWS (Amazon S3 + EC2 Instance Ubuntu 24.04)**:
- **DVC**: Quản lý và phiên bản hóa dữ liệu lưu trữ trên remote `s3://my-mlops-bucket-duyleo/dvc`.
- **GitHub Actions**: Tự động kích hoạt quy trình 4 giai đoạn (**Unit Test ➔ Train ➔ Eval Gate (>= 0.70) ➔ Deploy**).
- **FastAPI Serving**: Chạy dưới dạng daemon systemd service trên EC2 VM, phục vụ suy luận qua cổng `8000`.

### So sánh hiệu năng mô hình giữa Bước 2 và Bước 3:

| Giai đoạn | Số lượng mẫu huấn luyện | Accuracy | F1-Score | Trạng thái Deploy |
|---|:---:|:---:|:---:|:---:|
| **Bước 2 (Giai đoạn 1)** | 2,998 mẫu (`train_phase1.csv`) | 0.6440 | 0.6417 | Triển khai ban đầu |
| **Bước 3 (Continuous Training)** | 5,996 mẫu (`train_phase1` + `phase2`) | **0.7540** | **0.7521** | Đạt Eval Gate (>=0.70) & Auto-Deploy |

> **Nhận xét**: Khi kỹ sư dữ liệu commit file dữ liệu mới (`.dvc`), GitHub Actions tự động kích hoạt pipeline, huấn luyện lại trên 5,996 mẫu giúp Accuracy vượt ngưỡng chất lượng (đạt 75.40%) và tự động cập nhật model mới lên EC2 VM mà không cần can thiệp thủ công.

---

## 3. Khó Khăn Gặp Phải & Cách Giải Quyết

1. **Lỗi phiên bản Python 3.14 & thiếu `pkg_resources` khi cài đặt MLflow**:
   - *Nguyên nhân*: Phiên bản `setuptools >= 70.0.0` đã loại bỏ hoàn toàn `pkg_resources` mà MLflow 2.13.0 yêu cầu.
   - *Cách giải quyết*: Hạ cấp `setuptools` xuống phiên bản `setuptools<70.0.0` (`setuptools==69.5.1`) giúp MLflow hoạt động bình thường.
2. **Quyền truy cập AWS S3 (`AccessDenied`) & Cấu hình DVC trên Windows**:
   - *Nguyên nhân*: IAM User ban đầu thiếu chính sách quyền tạo và quản lý bucket; DVC cần thêm plugin `dvc-s3`.
   - *Cách giải quyết*: Cấp chính sách `AmazonS3FullAccess` (hoặc Policy phân quyền ObjectAdmin cho bucket), đồng thời cài đặt `dvc-s3` và cập nhật `requirements.txt`.
3. **Phân quyền Private Key SSH trên Windows**:
   - *Nguyên nhân*: Lỗi `WARNING: UNPROTECTED PRIVATE KEY FILE` khi SSH từ PowerShell.
   - *Cách giải quyết*: Dùng tiện ích `icacls` để reset và chỉ cấp quyền đọc duy nhất cho tài khoản người dùng hiện tại.
