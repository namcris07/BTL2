import os
import numpy as np
import torch
from torch.utils.data import TensorDataset, DataLoader
from coganh_agent import DQN_CoGanh

def train_supervised(data_path=None, epochs=100, batch_size=128, lr=1e-3):
    # Tăng epochs lên 100 để AI học sâu hơn từ bộ dữ liệu lớn
    if data_path is None:
        data_path = os.path.join(os.path.dirname(__file__), "data", "coganh_teacher.npz")
        
    if not os.path.exists(data_path):
        print(f"[ERROR] Không tìm thấy {data_path}. Vui lòng chạy collect_coganh_data.py trước!")
        return
        
    data = np.load(data_path)
    states = torch.from_numpy(data["states"]).float()
    actions = torch.from_numpy(data["actions"]).long()

    dataset = TensorDataset(states, actions)
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = DQN_CoGanh().to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)

    # Cờ bật/tắt weighted loss để xử lý mất cân bằng class nếu cần sau này.
    USE_WEIGHTED_LOSS = False

    if USE_WEIGHTED_LOSS:
        action_counts = np.bincount(data["actions"], minlength=200).astype(np.float32)
        class_weights = np.ones(200, dtype=np.float32)
        non_zero_mask = action_counts > 0
        class_weights[non_zero_mask] = action_counts[non_zero_mask].sum() / action_counts[non_zero_mask]
        class_weights = np.clip(class_weights, 1.0, 20.0)
        class_weights_tensor = torch.from_numpy(class_weights).float().to(device)
        criterion = torch.nn.CrossEntropyLoss(weight=class_weights_tensor, label_smoothing=0.05)
    else:
        # Chuyển về baseline loss ổn định (không weight, không label smoothing)
        criterion = torch.nn.CrossEntropyLoss()

    print(f"[INFO] Bắt đầu huấn luyện Supervised trên thiết bị: {device}...")
    for epoch in range(1, epochs + 1):
        model.train()
        total_loss = 0.0
        for batch_states, batch_actions in loader:
            batch_states, batch_actions = batch_states.to(device), batch_actions.to(device)
            logits = model(batch_states)
            loss = criterion(logits, batch_actions)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            total_loss += loss.item() * batch_states.size(0)
        print(f"[INFO] Epoch {epoch}/{epochs} - Loss: {total_loss / len(dataset):.4f}")

    save_path = os.path.join(os.path.dirname(__file__), "model", "coganh_dqn.pth")
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    torch.save(model.state_dict(), save_path)
    print(f"[INFO] Đã lưu model (trọng số mạng Nơ-ron) thành công vào: {save_path}")

if __name__ == "__main__":
    train_supervised()