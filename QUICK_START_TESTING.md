# Quick Start Testing Guide

## 🚀 Fastest Way to Run Tests

### Option 1: Complete Setup (Recommended)
```bash
setup-and-test.bat
```
This script will:
- Install all dependencies
- Start both servers
- Run the tests
- Show results

### Option 2: Manual Setup
1. **Start servers manually:**
   ```bash
   start-servers.bat
   ```

2. **Run tests:**
   ```bash
   test-simple.bat
   ```

### Option 3: NPM Commands
```bash
# Start servers first, then:
npm test
```

## 🔧 Troubleshooting

### If you get "webServer" errors:
- Use `test-simple.bat` instead
- Or run `npm run test:manual`

### If servers won't start:
1. Check if ports 3000 and 8000 are free
2. Make sure Python and Node.js are installed
3. Run `setup-and-test.bat` for complete setup

### If tests fail:
1. Make sure both servers are running
2. Check that "John Smith" patient exists in database
3. Try `npm run test:headed` to see the browser

## 📋 Available Scripts

| Script | Purpose |
|--------|---------|
| `setup-and-test.bat` | Complete setup + test run |
| `start-servers.bat` | Start both servers |
| `test-simple.bat` | Run tests (servers must be running) |
| `run-tests.bat` | Smart test runner |

## 🎯 Test Commands

```bash
npm test              # Run tests (manual mode)
npm run test:ui       # Interactive UI
npm run test:headed   # See browser
npm run test:debug    # Step-by-step
npm run test:report   # View results
```
