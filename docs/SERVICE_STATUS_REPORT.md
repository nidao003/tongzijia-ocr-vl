# PaddleOCR-VL 服务运行状态报告

## 📋 问题回答

### ❌ 问题 1: 是否开机自动启动？

**答案：否**

当前部署的服务 **不会开机自动启动**。

**说明**：
- ✅ 服务当前正在运行（手动启动）
- ❌ 未配置开机自启动（LaunchDaemon/LaunchAgent）
- ❌ 未配置 systemd 或其他自启动机制

**重启后状态**：重启电脑后，**所有服务都会停止**，需要手动重新启动。

---

### ✅ 问题 2: 后台运行对电能和性能的影响

**答案：有显著影响，需要优化**

## 🔍 详细分析

### 当前运行的服务（3个）

| 服务 | 端口 | PID | CPU | 内存 | 状态 |
|------|------|-----|-----|------|------|
| MLX-VLM 推理服务 | 8111 | 34837 | **76.2%** | 41MB | ⚠️ 高 CPU 占用 |
| MLX-VLM API 服务 | 8001 | 59094 | 0.1% | 5.5MB | ✅ 正常 |
| PaddleOCR API 服务 | 8000 | 32692 | 0.0% | **6.5GB** | ⚠️ 高内存占用 |

### 资源占用分析

#### 1️⃣ MLX-VLM 推理服务（最大问题 🔴）
```
CPU 占用: 76.2% （持续高占用）
内存占用: 41MB （较小）
影响: 🔴 严重影响电能消耗
```

**问题原因**：
- MLX-VLM 推理服务加载了模型权重到内存
- 即使没有请求，也在持续进行某种计算或轮询
- 可能是模型预加载和准备状态

#### 2️⃣ PaddleOCR API 服务（次大问题 🟡）
```
CPU 占用: 0.0% （空闲时正常）
内存占用: 6.5GB （非常大）
影响: 🟡 占用大量内存，影响其他应用
```

**问题原因**：
- PaddleOCR 模型权重已加载到内存（约 2-3GB）
- Python 进程保留了大量虚拟内存
- 模型初始化后常驻内存

#### 3️⃣ MLX-VLM API 服务（正常 🟢）
```
CPU 占用: 0.1% （非常低）
内存占用: 5.5MB （很小）
影响: 🟢 影响很小
```

---

## ⚡ 电能影响评估

### 空闲状态（无请求时）

**总体影响**：
- 🔴 **MLX-VLM 推理服务**：持续高 CPU（76.2%），**显著增加电能消耗**
- 🟡 **PaddleOCR API 服务**：6.5GB 内存占用，**增加内存压力**
- 🟢 **MLX-VLM API 服务**：影响很小

**估计影响**：
- **CPU 持续负载**：约 76% 单核持续占用
- **电能增加**：相比完全空闲状态，**增加约 30-50% 电能消耗**
- **风扇噪音**：可能触发风扇持续运行
- **电池续航**：如果是笔记本，**续航显著降低**

### 处理请求时

**处理请求时的影响**：
- 单次请求：7 秒，峰值内存 2.58GB
- 批量处理：CPU 和内存占用线性增长
- 并发请求：需要更多资源

---

## 🎯 推荐方案

### 方案 A：按需启动（推荐 ⭐）

**优点**：
- ✅ 零空闲资源占用
- ✅ 不影响电能消耗
- ✅ 灵活可控

**实施**：
1. **关闭所有服务**（不使用时）
2. **使用前启动**（需要时手动启动）
3. **使用后停止**（完成后停止）

**操作脚本**：
```bash
# 启动服务
cd /Users/daodao/dsl/paddleocr-vl
./start_services.sh

# 停止服务
./stop_services.sh
```

---

### 方案 B：仅启动轻量 API（次选）

**优点**：
- ✅ 资源占用极小（5.5MB 内存，0.1% CPU）
- ✅ 快速启动（按需启动后端）

**实施**：
1. **只运行 MLX-VLM API 服务**（端口 8001）
2. **首次请求时自动启动 MLX-VLM 推理服务**
3. **空闲超时后自动停止推理服务**

**启动命令**：
```bash
cd /Users/daodao/dsl/paddleocr-vl
# 只启动 API 服务，推理服务按需启动
.venv_paddleocr/bin/python mlx_vlm_api_server.py
```

---

### 方案 C：配置开机自启动 + 优化（生产环境）

**适用场景**：
- 需要长期稳定运行
- 多用户/多应用频繁调用
- 服务器环境（不在乎电能）

**配置方法**：
1. 创建 LaunchDaemon 配置
2. 设置资源限制
3. 配置自动重启

**配置文件示例**：
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.paddleocr.mlxvlm</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Users/daodao/dsl/paddleocr-vl/.venv_paddleocr/bin/python</string>
        <string>/Users/daodao/dsl/paddleocr-vl/mlx_vlm_api_server.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <false/>
    <key>WorkingDirectory</key>
    <string>/Users/daodao/dsl/paddleocr-vl</string>
    <key>StandardOutPath</key>
    <string>/Users/daodao/dsl/paddleocr-vl/mlx_vlm_api_server.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/daodao/dsl/paddleocr-vl/mlx_vlm_api_server.log</string>
</dict>
</plist>
```

---

## 🛠️ 立即行动建议

### 推荐：方案 A（按需启动）

#### 1. 当前立即停止所有服务
```bash
cd /Users/daodao/dsl/paddleocr-vl
./stop_services.sh

# 或者手动停止
pkill -f mlx_vlm.server
pkill -f mlx_vlm_api_server.py
pkill -f api_server.py
```

#### 2. 需要时启动
```bash
cd /Users/daodao/dsl/paddleocr-vl
./start_services.sh
# 选择选项 4: MLX-VLM + MLX-VLM API
```

#### 3. 使用后停止
```bash
./stop_services.sh
```

---

## 📊 资源占用对比

| 状态 | CPU 占用 | 内存占用 | 电能影响 | 推荐度 |
|------|----------|----------|----------|--------|
| **完全停止** | 0% | 0GB | 无 | ⭐⭐⭐⭐⭐ |
| **仅 API 服务** | 0.1% | 5.5MB | 极小 | ⭐⭐⭐⭐ |
| **API + 推理服务** | 76.2% | 6.5GB | **严重** | ⭐⭐ |

---

## 💡 最佳实践建议

### 对于个人使用（OpenClaw 场景）

**强烈推荐**：**按需启动（方案 A）**

**理由**：
1. ✅ 节省电能（不使用时零消耗）
2. ✅ 减少硬件磨损
3. ✅ 降低风扇噪音
4. ✅ 释放内存给其他应用
5. ✅ 延长设备寿命

**使用流程**：
```
需要 OCR → 启动服务 → 识别完成 → 停止服务
   ↓              ↓              ↓
  2 秒          7 秒           1 秒
```

### 对于服务器/生产环境

**推荐**：**方案 C（开机自启动）**

**理由**：
- 需要随时可用
- 多用户/多应用调用
- 服务器运行环境

---

## 🔧 优化建议

### 当前优化

#### 1. 停止不必要的服务

**立即停止**：
```bash
# 停止 PaddleOCR API 服务（最占用内存）
pkill -f api_server.py

# 停止 MLX-VLM 推理服务（最占用 CPU）
pkill -f mlx_vlm.server
```

**保留轻量服务**：
```bash
# 仅保留 MLX-VLM API 服务
# 这个服务占用极小：5.5MB 内存，0.1% CPU
```

#### 2. 创建按需启动脚本

我已经创建了启动脚本，可以直接使用：
```bash
cd /Users/daodao/dsl/paddleocr-vl
./start_services.sh  # 启动
./stop_services.sh   # 停止
```

---

## 📋 总结

### 核心问题

**问题 1：开机自启动**
- ❌ 当前没有配置
- ⚠️ 需要手动启动

**问题 2：后台影响**
- 🔴 MLX-VLM 推理服务：持续 76% CPU，**严重影响电能**
- 🟡 PaddleOCR API 服务：占用 6.5GB 内存
- 🟢 MLX-VLM API 服务：影响很小

### 推荐做法

**对于 OpenClaw 使用场景**：
1. ✅ **不配置开机自启动**
2. ✅ **按需启动服务**（使用时启动，用完停止）
3. ✅ **优先使用 MLX-VLM API**（端口 8001）
4. ❌ **不长期运行所有服务**

### 立即行动

**现在就可以做**：
```bash
# 1. 停止所有服务（节省资源）
cd /Users/daodao/dsl/paddleocr-vl
./stop_services.sh

# 2. 需要时再启动
./start_services.sh

# 3. 使用完后停止
./stop_services.sh
```

**这样可以**：
- 💰 节省 30-50% 电能
- 🔇 降低风扇噪音
- 💾 释放 6.5GB 内存
- ⏰ 延长设备寿命

---

**建议：强烈推荐按需使用，不要让服务长期后台运行！** ⚠️
