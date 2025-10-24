# Playwright Testing Setup

This document explains how to run the Playwright tests for the Clinic Billing System.

## Prerequisites

1. **Backend Server**: The FastAPI backend must be running on `http://localhost:8000`
2. **Frontend Server**: The React frontend must be running on `http://localhost:3000`
3. **Test Data**: Ensure there's a patient named "John Smith" in the database

## Quick Start

### Option 1: Using the Test Runner Scripts (Recommended)

**Windows Batch:**
```bash
run-tests.bat
```

**PowerShell:**
```powershell
.\run-tests.ps1
```

### Option 2: Start Servers Manually, Then Run Tests

1. **Start both servers:**
   ```bash
   start-servers.bat
   ```

2. **Run tests in manual mode:**
   ```bash
   npm run test:manual
   ```

### Option 3: Manual Commands

1. **Start the Backend Server:**
   ```bash
   cd backend
   python -m uvicorn app.main:app --reload --port 8000
   ```

2. **Start the Frontend Server:**
   ```bash
   cd frontend
   npm run dev
   ```

3. **Run the Tests:**
   ```bash
   # Run all tests
   npm test
   
   # Run with UI mode (interactive)
   npm run test:ui
   
   # Run in headed mode (see browser)
   npm run test:headed
   
   # Run specific test file
   npx playwright test seed.spec.ts
   ```

## Test Files

- `seed.spec.ts` - Tests for the staff/patients page functionality

## Test Scenarios

### Staff Patients Page Tests
1. **Patient Display Test**: Verifies that "John Smith" patient is visible in the patients table
2. **Table Structure Test**: Verifies that all table headers (Name, Email, Phone, DOB, Created, Actions) are present

## Available Test Commands

```bash
# Auto-start server and run tests
npm test
npm run test:ui
npm run test:headed
npm run test:debug

# Manual mode (servers must be running)
npm run test:manual
npm run test:manual:ui
npm run test:manual:headed

# View test report
npm run test:report
```

## Troubleshooting

### Common Issues

1. **"Page not found" errors**: Ensure both backend and frontend servers are running
2. **"John Smith not found"**: Ensure test data exists in the database
3. **Authentication issues**: The patients page might require login - check if authentication is needed

### Debug Mode

To debug tests step by step:
```bash
npx playwright test seed.spec.ts --debug
```

### View Test Results

After running tests, view the HTML report:
```bash
npx playwright show-report
```

## Test Configuration

The tests are configured in `playwright.config.ts`:
- Base URL: `http://localhost:3000`
- Browsers: Chrome, Firefox, Safari
- Screenshots and videos on failure
- HTML reporter enabled

## Adding New Tests

To add new tests, create new `.spec.ts` files in the root directory or modify existing ones. Follow the same pattern as `seed.spec.ts`.
