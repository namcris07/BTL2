# 🎮 Cờ Gánh AI - Deep Q-Network (DQN)

Đây là dự án Bài tập lớn (BTL2) môn Nhập môn Trí tuệ Nhân tạo. Dự án hiện thực giải thuật Học tăng cường (Reinforcement Learning) với mạng Nơ-ron tích chập (CNN) kết hợp thuật toán Deep Q-Network (DQN) để chơi tự động trò chơi **Cờ Gánh**.

## 📂 Cấu trúc dự án

Dự án được chia thành các module với chức năng riêng biệt:

- `a2_260408.py`: File chứa logic luật chơi Cờ Gánh gốc (Gánh, Chẹt, Mở) và thuật toán Minimax (Bot rule-based).
- `coganh_env.py`: Môi trường (Environment) mô phỏng bàn cờ giao tiếp với AI, tính toán phần thưởng (reward).
- `coganh_agent.py`: **File chính dùng để nộp bài**. Chứa mạng DQN và hàm `move(board, player, remain_time)` theo đúng chuẩn yêu cầu.
- `collect_coganh_data.py`: Script thu thập dữ liệu (Teacher Data) bằng cách cho Minimax đấu với Bot ngẫu nhiên.
- `train_coganh_supervised.py`: Huấn luyện nhanh (Pre-training) AI bằng phương pháp Học có giám sát (Supervised Learning) từ dữ liệu đã thu thập.
- `train_coganh.py`: Huấn luyện chuyên sâu (Fine-tuning) bằng Học tăng cường (DQN) cho phép AI tự chơi với môi trường để tối ưu chiến thuật.
- `coganh_ui.py`: Giao diện đồ họa (GUI) sử dụng Tkinter giúp trực quan hóa các trận đấu.

## 🚀 Yêu cầu hệ thống

Đảm bảo bạn đã cài đặt Python 3.7+ và các thư viện sau:

```bash
pip install torch numpy
```
*(Ghi chú: Thư viện `tkinter` để hiển thị UI đã được tích hợp sẵn trong Python tiêu chuẩn).*

## 📖 Hướng dẫn Huấn luyện AI (Training Pipeline)

Để tự huấn luyện ra một mô hình AI từ đầu, hãy chạy lần lượt các bước sau:

**Bước 1: Thu thập dữ liệu chuyên gia**
```bash
python collect_coganh_data.py
```
> Quá trình này sẽ chạy 1000 ván game giữa Minimax và Random Bot để tạo ra file dữ liệu `data/coganh_teacher.npz`.

**Bước 2: Huấn luyện nền tảng (Supervised Pre-training)**
```bash
python train_coganh_supervised.py
```
> AI sẽ học cách "bắt chước" các nước đi tốt từ file dữ liệu. Kết thúc bước này sẽ sinh ra file trọng số `model/coganh_dqn.pth`.

**Bước 3: Tối ưu chiến thuật (RL Fine-tuning)**
```bash
python train_coganh.py
```
> AI sẽ tự chơi với môi trường để cải thiện chiến thuật dựa trên phần thưởng. Sau khi hoàn thành, file trọng số `model/coganh_dqn.pth` sẽ được cập nhật với phiên bản tối ưu nhất.

## 🎯 Hướng dẫn Kiểm thử và Đánh giá (Evaluation)

Sau khi đã có file model `model/coganh_dqn.pth`, bạn có thể xem AI thi đấu bằng cách chạy Giao diện Đồ họa (GUI).

Giao diện 2D mô phỏng bàn cờ gỗ. AI DQN (quân X - Xanh) sẽ thi đấu trực tiếp với thuật toán Minimax (quân O - Đỏ).
```bash
python coganh_ui.py
```
*(Sử dụng các nút Start / Pause / Step trên UI để điều khiển trận đấu).*

## 🎓 Nộp bài

Để nộp bài, bạn chỉ cần nộp file `coganh_agent.py` và file trọng số mô hình `coganh_dqn.pth`. Hàm `move` bên trong `coganh_agent.py` đã được thiết kế hoàn toàn độc lập, tự động tải trọng số và phản hồi nước đi trong giới hạn 3 giây cho mỗi lượt."# BTL2-IntroAI" 
