# CGO Issue - Backend Won't Start

## Problem
The backend requires CGO (C compiler) for SQLite, but it's not available on Windows.

## Solutions

### Option 1: Install MinGW-w64 (Recommended)
1. Download from: https://github.com/niXman/mingw-builds-binaries/releases
2. Get: `x86_64-13.2.0-release-posix-seh-ucrt-rt_v11-rev0.7z`
3. Extract to `C:\mingw64`
4. Add `C:\mingw64\bin` to PATH
5. Restart terminal
6. Run: `go run cmd/server/main.go`

### Option 2: Use In-Memory Database (Quick Test)
- Data won't persist between restarts
- Good for testing only
- I can modify the code if you prefer this

### Option 3: Use Pre-built Binary
- I can build the backend on a system with CGO
- You run the .exe file directly

## Current Status
- Frontend: Ready to run
- Backend: Blocked on CGO dependency

Please let me know which option you'd like to proceed with.
