import { test, expect } from '@playwright/test';

test.describe('Login and Dashboard Navigation', () => {

  test('should login successfully and navigate to dashboard', async ({ page }) => {
    // Navigate to login page
    await page.goto('http://localhost:5173/staff/login');
    await page.waitForLoadState('networkidle');

    // Verify login page elements
    await expect(page.getByText('Clinic Billing')).toBeVisible();
    await expect(page.getByText('Sign in to your account')).toBeVisible();

    // Check if email and password fields are present
    const emailField = page.getByLabel('Email Address');
    const passwordField = page.getByLabel('Password');
    await expect(emailField).toBeVisible();
    await expect(passwordField).toBeVisible();

    // Verify default values are pre-filled
    await expect(emailField).toHaveValue('admin@clinic.com');
    await expect(passwordField).toHaveValue('admin123');

    // Click the Sign In button
    const signInButton = page.getByRole('button', { name: 'Sign In' });
    await expect(signInButton).toBeVisible();
    await expect(signInButton).toBeEnabled();

    // Click login button
    await signInButton.click();

    // Wait for navigation to dashboard
    await page.waitForURL('**/staff/dashboard');
    await page.waitForLoadState('networkidle');

    // Verify we're on the dashboard page - use more specific selector
    await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();

    
  });
});
