import { test, expect } from "@playwright/test";

const TEST_EMAIL = process.env.TEST_ADMIN_EMAIL || "admin@example.com";
const TEST_PASSWORD = process.env.TEST_ADMIN_PASSWORD || "Admin123!";

test.describe("Auth flow", () => {
  test("should redirect to login when accessing protected route", async ({ page }) => {
    await page.goto("/dashboard");
    await expect(page).toHaveURL(/\/login/, { timeout: 5000 });
  });

  test("should persist session after login", async ({ page }) => {
    await page.goto("/login");
    await page.getByLabel(/email/i).fill(TEST_EMAIL);
    await page.getByLabel(/mật khẩu/i).fill(TEST_PASSWORD);
    await page.getByRole("button", { name: /đăng nhập/i }).click();
    await expect(page).toHaveURL(/\/dashboard/, { timeout: 10000 });
    await page.goto("/");
    await expect(page).not.toHaveURL(/\/login/);
  });

  test("should show dashboard content after login", async ({ page }) => {
    await page.goto("/login");
    await page.getByLabel(/email/i).fill(TEST_EMAIL);
    await page.getByLabel(/mật khẩu/i).fill(TEST_PASSWORD);
    await page.getByRole("button", { name: /đăng nhập/i }).click();
    await expect(page).toHaveURL(/\/dashboard/, { timeout: 10000 });
    await expect(page.getByText(/dashboard|admin|family/i)).toBeVisible({ timeout: 5000 });
  });
});
