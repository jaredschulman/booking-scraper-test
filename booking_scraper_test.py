import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from datetime import datetime

DORM_KEYWORDS = ["bed in", "dormitory", "shared"]
PRIVATE_KEYWORDS = ["room", "private"]

def is_dorm(name):
    return any(k in name.lower() for k in DORM_KEYWORDS)

def is_private(name):
    return any(k in name.lower() for k in PRIVATE_KEYWORDS) and not is_dorm(name)

async def scrape_booking_data(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto(url, timeout=60000)

        await page.wait_for_selector("table#hprt-table")
        html = await page.content()
        await browser.close()
        return parse_booking_html(html)

def parse_booking_html(html):
    soup = BeautifulSoup(html, "html.parser")
    rows = soup.select("table#hprt-table tr.js-rt-block-row")
    print(f"\n🔍 Found {len(rows)} rows")
    print(f"Scraped at: {datetime.now().isoformat()}")

    dorm_beds = []
    private_rooms = []

    for row in rows:
        name_tag = row.select_one("a.hprt-roomtype-link span")
        select_tag = row.select_one("select.hprt-nos-select")
        price_tag = row.select_one("span.prco-valign-middle-helper")

        if not name_tag or not select_tag or not price_tag:
            continue

        # Only keep Free Cancellation rows
        free_cancel = any(
            "free cancellation" in tag.get_text(strip=True).lower()
            for tag in row.select("li.e2e-cancellation, li[data-testid='cancellation-subtitle']")
        )
        if not free_cancel:
            continue

        name = name_tag.get_text(strip=True)

        try:
            price = float(price_tag.get_text(strip=True).replace("$", "").replace(",", ""))
        except ValueError:
            continue

        options = select_tag.find_all("option")
        quantity = len(options) - 1  # Exclude option 0

        if quantity == 0:
            continue

        print(f"{name} | ${price:.2f} | {quantity} available")

        if is_dorm(name):
            beds_per_room = 1
            if "4-bed" in name.lower():
                beds_per_room = 4
            elif "6-bed" in name.lower():
                beds_per_room = 6
            elif "8-bed" in name.lower():
                beds_per_room = 8
            elif "10-bed" in name.lower():
                beds_per_room = 10
            elif "12-bed" in name.lower():
                beds_per_room = 12

            total_beds = beds_per_room * quantity
            dorm_beds += [price] * total_beds
        elif is_private(name):
            private_rooms += [price] * quantity

    print(f"\n🛏️ Dorm beds available: {len(dorm_beds)}")
    print(f"💸 Avg dorm bed price: ${sum(dorm_beds)/len(dorm_beds):.2f}" if dorm_beds else "💸 Avg dorm bed price: N/A")
    print(f"🏠 Private rooms available: {len(private_rooms)}")
    print(f"💰 Avg private room price: ${sum(private_rooms)/len(private_rooms):.2f}" if private_rooms else "💰 Avg private room price: N/A")

# -----------------------------
# 🔍 Example test run
# -----------------------------
if __name__ == "__main__":
    test_url = "https://www.booking.com/hotel/us/i-street-hostel.en-gb.html?checkin=2025-04-27&checkout=2025-04-28&group_adults=1"
    asyncio.run(scrape_booking_data(test_url))
