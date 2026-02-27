# UI Access Issue - Solutions

## Problem
The frontend and backend are running on a remote server (private IP: 172.31.79.156).
You can't access http://localhost:3000 from your local machine because it's not running locally.

## ✅ Quick Solutions

### Option 1: Deploy to Public Hosting (Recommended)
This makes it accessible from anywhere via a public URL.

**Deploy to Vercel + Railway (15 min):**
1. Push code to GitHub
2. Deploy backend to Railway → get URL like `https://social-agent-xxx.railway.app`
3. Deploy frontend to Vercel → get URL like `https://social-agent-pro.vercel.app`
4. Update CORS to allow Vercel domain
5. Access from any browser ✅

**See DEPLOY.md for step-by-step instructions.**

### Option 2: SSH Port Forwarding (For Testing Now)
Forward the remote ports to your local machine:

```bash
# On your local machine (not on the server):
ssh -L 3000:localhost:3000 -L 8000:localhost:8000 ubuntu@<server-ip>

# Then open in your browser:
# http://localhost:3000 → Frontend
# http://localhost:8000 → Backend
```

**Replace `<server-ip>`** with the actual public IP or hostname of this server.

### Option 3: Use a Tunnel (ngrok/cloudflared)
Expose the local services via a public tunnel:

**Using cloudflared:**
```bash
# Install cloudflared
curl -L --output cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64.deb
sudo dpkg -i cloudflared.deb

# Tunnel frontend
cloudflared tunnel --url http://localhost:3000

# You'll get a public URL like: https://xxx-xxx-xxx.trycloudflare.com
```

### Option 4: Open Server Ports (If You Control the Server)
If this is your own server (EC2, VPS, etc.), open ports 3000 and 8000 in the firewall/security group.

**For AWS EC2:**
1. Go to EC2 Console
2. Select this instance
3. Security Groups → Edit Inbound Rules
4. Add rules:
   - Type: Custom TCP
   - Port: 3000 (Frontend)
   - Source: Your IP or 0.0.0.0/0 (public)
5. Add rule for port 8000 (Backend)
6. Save
7. Access via `http://<public-ip>:3000`

## Current Services Status

Both services are running perfectly:

✅ **Backend:** http://localhost:8000 (on server)
- Health check passing
- Twitter API configured
- All endpoints operational

✅ **Frontend:** http://localhost:3000 (on server)
- Vite dev server running
- HTML serving correctly
- React app loaded

## Recommended Next Step

**I recommend Option 1: Deploy to production**

Why:
- Most professional solution
- Always accessible
- Free/cheap ($0-5/month)
- Takes ~15 minutes
- You get public URLs to share

**Alternative:** If you just want to test right now, use **Option 2 (SSH port forwarding)** — it's the fastest way to access the UI from your local machine.

## Need Help?

Let me know which option you'd like to pursue and I'll help you set it up!

---

**Quick Commands:**

```bash
# Check services are running
curl http://localhost:8000/api/v1/health  # Backend
curl -I http://localhost:3000             # Frontend

# Stop services
pkill -f uvicorn  # Backend
pkill -f vite     # Frontend

# Restart
# See STATUS.md for restart commands
```
