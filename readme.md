# Workshop K8s 101 — Debug Life Indonesia

> **Deploy Pertamamu ke Kubernetes.**
> Dari nol sampai pipeline jalan — di EC2-mu sendiri.

---

## Arsitektur Deploy

```
git push → GitHub Actions
               │
               ├─ Job 1: Build & Push Docker image ke ghcr.io
               │
               └─ Job 2: SSH ke EC2
                           │
                           └─ kubectl apply (jalan LOKAL di EC2)
                                       │
                                       └─ K3s cluster (127.0.0.1:6443)
```

> Port 6443 **tidak perlu dibuka** ke internet.
> GitHub Actions deploy via SSH, bukan konek langsung ke API server.
> Tidak ada TLS SAN issue.

---

## Struktur Repo

```
2048-main/
├── static/                   ← Asset CSS & JS frontend
│   ├── css/
│   └── js/
├── templates/                ← HTML templates (Jinja2)
│   ├── index.html
│   └── modal.html
├── k8s/
│   └── manifest.yaml         ← Deployment + Service (1 file)
├── .github/
│   └── workflows/
│       └── deploy.yml        ← CI/CD pipeline (SSH deploy)
├── agent.py                  ← AI agent (minimax)
├── board.py                  ← Logic papan 2048
├── engine.py                 ← Engine pencarian move terbaik
├── game.py                   ← Game state & controller
├── main.py                   ← FastAPI app — entry point
├── requirements.txt          ← Python dependencies
├── Dockerfile                ← Recipe build image (port 8080)
└── README.md                 ← Kamu di sini
```

---

## Hands-On: 7 Steps

### STEP 1 — SSH ke EC2

```bash
# Pastikan permission key sudah benar
chmod 400 workshop.pem

# SSH ke EC2 (username default EC2 Ubuntu = "ubuntu")
ssh -i workshop.pem ubuntu@<EC2-PUBLIC-IP>
```

> Credential ada di channel **#workshop** di Discord.

**Troubleshooting SSH:**

| Error | Penyebab | Fix |
|-------|----------|-----|
| `Permission denied (publickey)` | chmod belum 400 | `chmod 400 workshop.pem` |
| `Warning: Unprotected private key` | Permission file terlalu lebar | `chmod 400 workshop.pem` |
| `Connection timed out` | Security Group belum buka port 22 | Cek inbound rules EC2 |

---

### STEP 2 — Clone Repo Workshop

```bash
git clone https://github.com/Deri-Nugroho/Testing.git
cd Testing
ls
```

Output yang harus muncul:

```
static/  templates/  k8s/  .github/  Dockerfile  requirements.txt  main.py  README.md
```

---

### STEP 3 — Install K3s

```bash
bash install-k3s.sh
```

Script ini otomatis:
- Update system packages
- Install K3s (plain, tanpa `--tls-san` — tidak perlu!)
- Setup `kubectl` tanpa sudo
- Verifikasi node Ready
- Print panduan setup GitHub Secrets

> ⏱️ Estimasi: **2–3 menit**. Jangan close terminal!

**Verifikasi manual setelah install:**

```bash
kubectl get nodes
# NAME             STATUS   ROLES                  AGE
# ip-172-31-xx-xx  Ready    control-plane,master   2m
```

---

### STEP 4 — Setup GitHub Secrets (3 Secrets)

GitHub Actions konek ke EC2 via SSH key — `kubectl` jalan lokal di EC2 pakai `~/.kube/config` milik user ubuntu.

> 🚫 **JANGAN** buat secret `KUBECONFIG`.
> Panduan lain yang minta `sudo cat /etc/rancher/k3s/k3s.yaml | base64 -w 0`
> adalah untuk pendekatan *remote kubectl* (konek dari luar ke port 6443).
> Workshop ini pakai SSH — tidak perlu itu sama sekali.

**a) Dapatkan nilai untuk setiap secret:**

```bash
# Di terminal EC2 — jalankan untuk dapat public IP
curl -s ifconfig.me
```

**b) Tambahkan 3 secret ke GitHub:**

Buka repo → **Settings → Secrets and variables → Actions → New repository secret**

| Secret Name | Value |
|-------------|-------|
| `EC2_HOST` | Public IP EC2, contoh: `3.210.198.54` |
| `EC2_USER` | Username SSH, contoh: `ubuntu` |
| `EC2_SSH_KEY` | Seluruh isi file `.pem` — dari `-----BEGIN RSA PRIVATE KEY-----` sampai `-----END RSA PRIVATE KEY-----` |

> ⚠️ `EC2_SSH_KEY` harus **seluruh isi** file `.pem`, termasuk header & footer.
> Cara lihat: `cat /path/to/workshop.pem`
> Copy semua — paste ke secret value as-is (multi-line diperbolehkan GitHub).

> ⚠️ **Jangan pernah commit file `.pem` ke repo. Ever.**

**c) Pastikan port 22 terbuka di Security Group EC2:**

```
AWS Console → EC2 → Security Groups → Inbound Rules
Type   : SSH
Port   : 22
Source : 0.0.0.0/0   (atau batasi ke IP spesifik untuk keamanan)
```

**Troubleshooting Step 4:**

| Error | Penyebab | Fix |
|-------|----------|-----|
| `ssh: handshake failed: unable to authenticate` | EC2_SSH_KEY salah / terpotong | Paste ulang isi `.pem` lengkap |
| `dial tcp: connection refused` | EC2_HOST salah | Cek public IP EC2 di console AWS |
| `dial tcp: i/o timeout` | Port 22 tidak terbuka | Buka port 22 di Security Group |

---

### STEP 5 — Trigger Pipeline Pertama

```bash
git add .
git commit -m "trigger: first deploy"
git push origin main
```

**Pantau progress pipeline:**
1. Buka `github.com/<username>/Testing`
2. Klik tab **Actions**
3. Klik workflow run terbaru
4. Lihat log real-time — ada **2 job**: `Build Docker Image` → `Deploy to K3s via SSH`
5. Tunggu ✓ hijau (~2–3 menit)

> ⚠️ **Pastikan GitHub Container Registry package di-set Public!**
> `github.com/<username>` → tab **Packages** → `game-2048` → **Package settings → Change visibility → Public**
> Tanpa ini K3s tidak bisa pull image dan pod akan `ImagePullBackOff`.

---

### STEP 6 — Verifikasi App Jalan

```bash
kubectl get pods
# NAME                            READY   STATUS    RESTARTS   AGE
# game-2048-76d48c88df-xxxxx      1/1     Running   0          42s

kubectl get svc
# NAME            TYPE       CLUSTER-IP     EXTERNAL-IP   PORT(S)        AGE
# game-2048-svc   NodePort   10.43.106.147  <none>        80:30080/TCP   42s
```

Kalau `STATUS = Running` → kamu berhasil! 🎉

**Buka browser:**

```
http://<EC2-PUBLIC-IP>:30080
```

> ⚠️ Pastikan Security Group EC2 membuka **port 30080** (inbound, TCP)

---

### BONUS STEP — Self-Healing Demo

```bash
# 1. Catat nama pod yang sedang running
kubectl get pods

# 2. Bunuh pod-nya dengan sengaja
kubectl delete pod game-2048-xxxxx-yyyyy

# 3. Pantau langsung — jalankan segera setelah delete
kubectl get pods -w
```

Dalam ~5 detik:

```
NAME                         READY   STATUS        AGE
game-2048-76d48c88df-xxxxx   1/1     Terminating   5m
game-2048-76d48c88df-yyyyy   0/1     Pending       1s
game-2048-76d48c88df-yyyyy   1/1     Running       4s
```

Pod lama mati → pod baru lahir otomatis. Inilah **self-healing** Kubernetes.

```
Deployment (replicas: 2)
    ↓ deteksi pod mati
Controller Loop
    ↓ buat pod baru
Pod baru → Running
    ↓
Service tetap hidup (port 30080 tidak pernah down)
```

---

## Troubleshooting Umum

```bash
# Cek status pod
kubectl get pods

# Detail error pod (lihat bagian Events di bawah output)
kubectl describe pod <nama-pod>

# Lihat log app
kubectl logs <nama-pod>

# Lihat log K3s live
sudo journalctl -u k3s -f

# Cek status service K3s
sudo systemctl status k3s

# Restart K3s
sudo systemctl restart k3s

# Fix kubeconfig lokal kalau kubectl tiba-tiba tidak bisa connect
sudo cp /etc/rancher/k3s/k3s.yaml $HOME/.kube/config
sudo chown $USER:$USER $HOME/.kube/config
```

**Pod `ImagePullBackOff`?**

```bash
# Cek image apa yang dicoba di-pull
kubectl describe pod <nama-pod> | grep -A5 "Events:"
# Solusi: jadikan GitHub Container Registry package = Public
```

**Service dapat `EXTERNAL-IP <pending>` terus?**

> Ini normal untuk NodePort. Akses app via `<EC2-IP>:30080` langsung — tidak perlu EXTERNAL-IP.

---

## 8 Command Wajib

```bash
kubectl get nodes              # cek status cluster
kubectl get pods               # cek pod running/tidak
kubectl get svc                # cek service & port
kubectl describe pod <pod>     # detail pod — untuk debug ImagePullBackOff, CrashLoop, dll
kubectl logs <pod>             # lihat log app
kubectl delete pod <pod>       # hapus pod (untuk demo self-healing)
sudo systemctl status k3s      # cek K3s service
sudo journalctl -u k3s -f      # live log K3s
```

---

## Stack Workshop

| Komponen | Tool | Fungsi |
|----------|------|--------|
| App | FastAPI + Uvicorn | Game 2048 dengan AI (port 8080) |
| CI/CD | GitHub Actions | Trigger pipeline tiap `git push` |
| Deploy method | SSH via `appleboy/ssh-action` | Jalankan `kubectl` di EC2 secara lokal |
| Container | Docker (multi-stage) | Bungkus app jadi image ringan |
| Registry | GitHub Container Registry (ghcr.io) | Simpan Docker image — harus **Public** |
| Orchestrator | K3s | Kubernetes ringan untuk EC2 |
| Service type | NodePort (30080) | Expose app ke luar via port EC2 |

---

## Catatan EC2 vs VPS Biasa

| Aspek | VPS Biasa | AWS EC2 (Workshop ini) |
|-------|-----------|------------------------|
| SSH | `ssh user@ip -p port` | `ssh -i key.pem ubuntu@ip` |
| Install K3s | `curl ... \| sh -` | `curl ... \| sh -` (sama) |
| Deploy method | SSH ke VPS → kubectl lokal | SSH ke EC2 → kubectl lokal |
| Service type | NodePort | NodePort (port 30080) |
| Akses app | `http://IP:30080` | `http://IP:30080` |
| GitHub Secrets | `EC2_HOST, EC2_USER, EC2_SSH_KEY` | `EC2_HOST, EC2_USER, EC2_SSH_KEY` |

---

## API Endpoints (2048 Game)

| Method | Endpoint | Fungsi |
|--------|----------|--------|
| `GET` | `/` | Render antarmuka game |
| `GET` | `/board` | State papan & skor saat ini (JSON) |
| `GET` | `/ai_move` | AI lakukan 1 move, return state baru |
| `POST` | `/move/{direction}` | Geser tile: `up/down/left/right` |
| `POST` | `/reset` | Reset papan ke kondisi awal |

---

*debug life indonesia · inspect · reflect · refactor · 2026*
