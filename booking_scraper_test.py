import asyncio
from datetime import datetime, timedelta
from dateutil import tz
from playwright.async_api import async_playwright

# Hostel metadata
HOSTELS = {
    "Generator DC": {
        "url_template": "https://www.booking.com/hotel/us/generator-washington-dc.html?checkin={checkin}&checkout={checkout}&group_adults=1&group_children=0&no_rooms=1",
        "max_dorm_beds": 160,
        "max_private_rooms": 106
    },
    "I Street Capsule Hostel": {
        "url_template": "https://www.booking.com/hotel/us/i-street-capsule-hostel.html?checkin={checkin}&checkout={checkout}&group_adults=1&group_children=0&no_rooms=1",
        "max_dorm_beds": 64,
        "max_private_rooms": 1
    }
}

# Date calculation: 2 days from today
now = datetime.now(tz.gettz('America/New_York'))
checkin = (now + timedelta(days=2)).strftime('%Y-%m-%d')
checkout = (now + timedelta(days=3)).strftime('%Y-%m-%d')

async def scrape_booking_data(name, url):
    print(f"\n🔍 Scraping: {name}")
    print(f"🌐 URL: {url}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto(url)
        await page.wait_for_timeout(10000)

        # Select all rows with accommodation options
        rows = await page.query_selector_all('tr.js-rt-block-row')

        total_dorm_beds = 0
        total_private_rooms = 0
        dorm_price_total = 0
        private_price_total = 0

        for row in rows:
            try:
                name_el = await row.query_selector('.hprt-roomtype-icon-link')
                price_el = await row.query_selector('.bui-price-display__value')
                select_el = await row.query_selector('select')

                if not (name_el and price_el and select_el):
                    continue

                name_text = (await name_el.inner_text()).strip().lower()
                price_text = (await price_el.inner_text()).replace("$", "").replace(",", "").strip()
                quantity_options = await select_el.query_selector_all('option')

                max_qty = int((await quantity_options[-1].get_attribute("value")) or 0)
                price = float(price_text)

                if "bed in" in name_text:
                    total_dorm_beds += max_qty
                    dorm_price_total += price * max_qty
                else:
                    total_private_rooms += max_qty
                    private_price_total += price * max_qty

            except Exception as e:
                print(f"⚠️ Error parsing row: {e}")
                continue

        avg_dorm_price = round(dorm_price_total / total_dorm_beds, 2) if total_dorm_beds else ""
        avg_private_price = round(private_price_total / total_private_rooms, 2) if total_private_rooms else ""

        print(f"🛏️ Dorm beds available: {total_dorm_beds}")
        print(f"💸 Avg dorm bed price: {avg_dorm_price}")
        print(f"🏠 Private rooms available: {total_private_rooms}")
        print(f"💰 Avg private room price: {avg_private_price}")

        await browser.close()

async def main():
    for name, meta in HOSTELS.items():
        url = meta["url_template"].format(checkin=checkin, checkout=checkout)
        await scrape_booking_data(name, url)

if __name__ == "__main__":
    asyncio.run(main())
