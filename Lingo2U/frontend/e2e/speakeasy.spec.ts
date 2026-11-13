import { test, expect } from '@playwright/test';

test('register -> onboard -> session -> report flow', async ({ page }) => {
  await page.goto('http://localhost:5173/register');
  await page.fill('input[type="email"]', `learner_${Date.now()}@example.com`);
  await page.fill('input[type="password"]', 'Password123!');
  await page.click('button[type="submit"]');

  await expect(page).toHaveURL(/\/onboarding/);
  await page.click('button:has-text("Start Practicing")');

  await expect(page).toHaveURL(/\/dashboard/);
  await page.click('button:has-text("Start Speaking Now")');

  await expect(page).toHaveURL(/\/session\//);
  await page.fill('input[placeholder*="Or type your answer"]', 'Yesterday I go to the cafe.');
  await page.click('button:has-text("Send")');

  await expect(page.locator('text=Better way to say it:')).toBeVisible();

  await page.click('button:has-text("End Practice")');
  await expect(page).toHaveURL(/\/report/);
  await expect(page.locator('h1:has-text("Session Report")')).toBeVisible();
});
