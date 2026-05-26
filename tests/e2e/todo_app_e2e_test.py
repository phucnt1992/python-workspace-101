from playwright.sync_api import Page, expect


def test_todo_app_end_to_end_flow(page: Page, app_url: str) -> None:
    page.goto(f"{app_url}/ui/")

    expect(page.get_by_role("heading", name="Todo Kanban Board")).to_be_visible()
    expect(page.locator("#health-status")).to_contain_text("Liveness:")
    expect(page.locator("#health-status")).to_contain_text("Readiness:")

    page.locator("#title").fill("Buy milk")
    page.locator("#description").fill("2 bottles")
    page.get_by_role("button", name="Add Card").click()

    first_item = page.locator(".todo-item").first
    expect(first_item).to_be_visible()
    expect(first_item.locator('input[name="title"]')).to_have_value("Buy milk")
    expect(page.locator(".kanban-column").first.locator('input[name="title"]').first).to_have_value("Buy milk")

    first_item.get_by_role("button", name="Complete").click()
    expect(page.locator(".kanban-column").nth(1).locator('input[name="title"]').first).to_have_value("Buy milk")

    page.locator(".todo-item").first.get_by_role("button", name="Reopen").click()
    expect(page.locator(".kanban-column").first.locator('input[name="title"]').first).to_have_value("Buy milk")

    updated_item = page.locator(".todo-item").first
    updated_item.locator('input[name="title"]').fill("Buy oat milk")
    updated_item.locator('input[name="description"]').fill("Unsweetened")
    updated_item.get_by_role("button", name="Save").click()
    expect(page.locator(".todo-item").first.locator('input[name="title"]')).to_have_value("Buy oat milk")

    page.locator(".todo-item").first.get_by_role("button", name="Delete").click()
    expect(page.locator(".todo-item")).to_have_count(0)
