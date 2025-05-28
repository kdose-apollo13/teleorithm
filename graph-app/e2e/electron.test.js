// e2e/electron.test.js
import { test, expect } from '@playwright/test';
import { _electron as electron } from '@playwright/test';
import path from 'path';

test('Electron app loads SvelteKit page with node list', async () => {
  const electronApp = await electron.launch({
    args: [path.join(process.cwd(), 'main.js')],
    env: { ...process.env, VITE_DEV_SERVER_URL: 'http://localhost:5173' }
  });

  const window = await electronApp.firstWindow();
  await window.waitForLoadState('networkidle', { timeout: 15000 });
  await window.waitForTimeout(2000);

  // Debug
  const content = await window.content();
  // console.log('Page content:', content);

  // Test node list
  const nodeList = await window.locator('div[role="listbox"][aria-label="Node List"]');
  await expect(nodeList).toBeVisible({ timeout: 10000 });

  // Test specific nodes
  await expect(window.locator('text=node1')).toBeVisible();
  await expect(window.locator('text=node2')).toBeVisible();

  await electronApp.close();
});
