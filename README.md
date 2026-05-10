# Ô Ăn Quan

Ứng dụng mô phỏng trò chơi Ô Ăn Quan truyền thống của Việt Nam, được phát triển bằng Python.

## 🌟 Tính Năng Nổi Bật

* **Giao diện Pygame:** Khởi chạy game bằng cửa sổ đồ họa với màn hình chọn chế độ chơi.
* **Chế độ chơi:** Hỗ trợ chơi hai người (PvP) và chơi với máy (PvB).
* **Luật chơi:** Xử lý rải quân, ăn liên hoàn, cấm ăn quan non, vay/trả quân và tính điểm cuối ván.
* **AI bot:** Có sẵn các chiến lược Random, Greedy và Minimax + Alpha-Beta.

---

## 🛠 1. Cài đặt hệ thống

**Yêu cầu:** Máy tính cần cài đặt **Python 3.10** trở lên.

Khuyến nghị tạo một môi trường ảo để tránh xung đột thư viện giữa các dự án.

```bash
python -m venv .venv

# Kích hoạt môi trường ảo trên macOS / Linux
source .venv/bin/activate
```

Nếu sử dụng Windows PowerShell, lệnh kích hoạt tương ứng là:

```powershell
.\.venv\Scripts\Activate.ps1
```

Sau khi kích hoạt môi trường ảo, cài đặt các thư viện phụ thuộc bằng lệnh sau:

```bash
pip install -r requirements.txt
```

---

## 🚀 2. Cách chạy Game

Khởi chạy ứng dụng bằng lệnh sau:

```bash
python main.py
```

Hiện tại, `main.py` mở giao diện Pygame và chuyển vào màn hình menu để lựa chọn chế độ chơi.

Nếu cần chạy phiên bản console, hãy sử dụng runner tương ứng trong thư mục `game/ui/`.

### Lưu ý cho VS Code

* Đảm bảo đã chọn đúng Python interpreter từ thư mục `.venv`.
* Khuyến nghị cài đặt extension **Python** và **Pylance** để có trải nghiệm phát triển tốt hơn.
* Nếu gặp lỗi khi mở cửa sổ Pygame, hãy chạy lệnh từ terminal đã kích hoạt `.venv`, sử dụng Python 64-bit và cập nhật driver GPU nếu cần.

### Tài nguyên hình ảnh (Optional)

Đối với chế độ Pygame, có thể đặt các tệp ảnh sprite vào thư mục `assets/images/`. Nếu không có tệp ảnh, game sẽ tự động sử dụng các hình vẽ mặc định.

---

## 📜 3. Luật Chơi Ô Ăn Quan

Ứng dụng tuân theo các quy tắc cơ bản của trò chơi truyền thống như sau:

### Thiết lập ban đầu

* **Bàn cờ:** Gồm 12 ô, trong đó có 2 ô quan ở hai đầu và 10 ô dân chia đều cho hai bên.
* **Quân cờ:** 50 quân dân và 2 quân quan, với mỗi ô dân ban đầu có 5 quân.
* **Giá trị:** 1 Quan = 10 quân dân.
* **Quyền đi trước:** Được xác định bằng Oẳn tù xì.

### Cách rải quân và tính điểm

Người chơi bốc toàn bộ quân ở một ô thuộc quyền kiểm soát của mình và rải lần lượt từng quân theo chiều kim đồng hồ hoặc ngược chiều kim đồng hồ. Khi rải hết quân cuối cùng, một trong các trường hợp sau sẽ được áp dụng, tính từ ô đặt quân cuối:

* **TH1 (Nối tiếp):** CUỐI → ô có quân → Bốc tiếp đống quân đó và rải tiếp.
* **TH2 (Ăn quân):** CUỐI → ô trống → ô có quân → ăn toàn bộ quân trong ô đó.
* **TH3 (Mất lượt):** CUỐI → ô trống → ô trống → mất lượt.
* **TH4 (Đụng quan):** CUỐI → ô quan → mất lượt.
* **TH5 (Ăn quan):** CUỐI → ô trống → ô quan → ăn toàn bộ quan và quân trong đó. **Lưu ý:** Không được ăn quan non.
* **TH6 (Ăn liên hoàn):** CUỐI → ô trống → ô có quân → ô trống → ô có quân → ăn liên hoàn các ô có quân xen kẽ ô trống.

### Cơ chế vay mượn

Khi đến lượt đi mà 5 ô của mình không còn quân nào, hệ thống sẽ lấy 5 quân từ số điểm đã ăn được để rải lại vào 5 ô, mỗi ô 1 quân. Nếu không đủ, trò chơi sẽ tự động ghi nợ từ đối thủ để bảo đảm lượt đi có thể tiếp tục. Số quân vay sẽ được trừ khi tính điểm chung cuộc.

### Kết thúc game

* Game kết thúc khi cả hai ô quan đều không còn quan hoặc quân dân.
* Khi đó, toàn bộ quân dân còn lại trên mỗi bên sẽ được thu hồi và cộng vào điểm.
* Sau khi trừ nợ vay, người chơi có tổng điểm cao hơn sẽ là người chiến thắng.

---

## 🏗 4. Cấu trúc Dự Án

Dự án được tổ chức theo module để thuận tiện cho việc mở rộng và bảo trì.

### Cấu trúc dữ liệu chính

* **Bàn cờ (12 ô):** Ô quan trái ở vị trí 0, ô quan phải ở vị trí 6. Năm ô của người chơi 0 là `[1..5]`, năm ô của người chơi 1 là `[7..11]`.
* **Trạng thái Board (`Board`):** Lưu mảng `seeds` (số lượng quân) và `quan_alive` (trạng thái sống/chết của quan).
* **Trạng thái Engine (`GameEngine`):** Quản lý lượt đi, `captured_by_player` (điểm đã ăn) và `borrowed_by_player` (điểm nợ).

### Các Module Cốt Lõi

* `main.py`: Điểm vào của ứng dụng, khởi chạy giao diện Pygame.
* `game/board.py`: Cung cấp lớp `Board` để thao tác với trạng thái bàn cờ.
* `game/rules.py`: Chứa logic xử lý TH1 đến TH6, cấm ăn quan non, vay mượn và tính điểm chung cuộc.
* `game/engine.py`: Điều phối vòng lặp lượt đi, Oẳn tù xì và luồng xử lý giữa rules và players.
* `game/players/`: Định nghĩa `HumanPlayer` và `BotPlayer`.
* `game/ui/`: Chứa `ConsoleUI` và thư mục `pygame_ui/` phục vụ giao diện đồ họa.

---

## 🧠 5. Mở Rộng Trí Tuệ Nhân Tạo

Game đã được chuẩn bị sẵn interface `Strategy` tại `game/ai/base_strategy.py` để triển khai các bot.

* **RandomStrategy:** Chọn ngẫu nhiên một nước đi hợp lệ.
* **GreedyStrategy:** Chọn nước đi có đánh giá heuristic tốt nhất trong số các nước đi hợp lệ.
* **Minimax + Alpha-Beta Pruning:** Mô phỏng các nước đi tương lai, đánh giá board bằng heuristic và cắt tỉa các nhánh không cần thiết để chọn nước đi phù hợp hơn.

---

## 📦 6. Ghi Chú Nhanh

* `main.py` là điểm vào hiện tại của dự án.
* Giao diện Pygame tích hợp menu chọn PvP hoặc PvB.
* Phiên bản console có thể được chạy thông qua runner trong `game/ui/console_runner.py`.