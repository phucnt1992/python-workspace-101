from playwright.sync_api import Locator, Page, expect


def _click_and_wait_for_htmx_settle(page: Page, trigger: Locator) -> None:
    page.evaluate(
        """() => {
            window.__todoHtmxSettled = new Promise((resolve) => {
                document.body.addEventListener("htmx:afterSettle", resolve, { once: true });
            });
        }"""
    )
    trigger.click()
    page.evaluate("() => window.__todoHtmxSettled")


def test_todo_app_end_to_end_flow(page: Page, app_url: str) -> None:
    page.goto(f"{app_url}/ui/")

    expect(page.get_by_role("heading", name="Todo Kanban Board")).to_be_visible()
    expect(page.locator("#health-status")).to_contain_text("Liveness:")
    expect(page.locator("#health-status")).to_contain_text("Readiness:")

    page.locator("#title").fill("Buy milk")
    page.locator("#description").fill("2 bottles")
    _click_and_wait_for_htmx_settle(page, page.get_by_role("button", name="Add Card"))

    first_item = page.locator(".todo-item").first
    expect(first_item).to_be_visible()
    expect(first_item.locator('input[name="title"]')).to_have_value("Buy milk")
    expect(page.locator(".kanban-column").first.locator('input[name="title"]').first).to_have_value("Buy milk")

    _click_and_wait_for_htmx_settle(page, first_item.get_by_role("button", name="Complete"))
    expect(page.locator(".kanban-column").nth(1).locator('input[name="title"]').first).to_have_value("Buy milk")

    _click_and_wait_for_htmx_settle(page, page.locator(".todo-item").first.get_by_role("button", name="Reopen"))
    expect(page.locator(".kanban-column").first.locator('input[name="title"]').first).to_have_value("Buy milk")

    updated_item = page.locator(".todo-item").first
    updated_item.locator('input[name="title"]').fill("Buy oat milk")
    updated_item.locator('input[name="description"]').fill("Unsweetened")
    _click_and_wait_for_htmx_settle(page, updated_item.get_by_role("button", name="Save"))
    expect(page.locator(".todo-item").first.locator('input[name="title"]')).to_have_value("Buy oat milk")

    _click_and_wait_for_htmx_settle(page, page.locator(".todo-item").first.get_by_role("button", name="Delete"))
    expect(page.locator(".todo-item")).to_have_count(0)
