import { test, expect } from "@playwright/test";

const TEST_EMAIL = process.env.TEST_ADMIN_EMAIL || "admin@example.com";
const TEST_PASSWORD = process.env.TEST_ADMIN_PASSWORD || "Admin123!";

test.describe("Login page", () => {
  test("should display login form", async ({ page }) => {
    await page.goto("/login");
    await expect(page.getByRole("heading", { name: /family network/i })).toBeVisible();
    await expect(page.getByLabel(/email/i)).toBeVisible();
    await expect(page.getByLabel(/mật khẩu/i)).toBeVisible();
    await expect(page.getByRole("button", { name: /đăng nhập/i })).toBeVisible();
  });

  test("should navigate to register", async ({ page }) => {
    await page.goto("/login");
    await page.getByRole("link", { name: /đăng ký/i }).click();
    await expect(page).toHaveURL(/\/register/);
  });

  test("should login with valid credentials", async ({ page }) => {
    await page.goto("/login");
    await page.getByLabel(/email/i).fill(TEST_EMAIL);
    await page.getByLabel(/mật khẩu/i).fill(TEST_PASSWORD);
    await page.getByRole("button", { name: /đăng nhập/i }).click();
    await expect(page).toHaveURL(/\/dashboard/, { timeout: 10000 });
  });

  test("should show error on invalid credentials", async ({ page }) => {
    await page.goto("/login");
    await page.getByLabel(/email/i).fill("invalid@example.com");
    await page.getByLabel(/mật khẩu/i).fill("wrongpassword");
    await page.getByRole("button", { name: /đăng nhập/i }).click();
    await expect(page.getByText(/invalid|thất bại|sai/i)).toBeVisible({ timeout: 5000 });
  });
});
