import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from datetime import datetime

# URLs for Generator DC and I Street Capsule Hostel
URLS = {
    "Generator DC": "https://www.booking.com/hotel/us/generator-washington-dc.en-gb.html",
    "I Street Capsule Hostel": "https://www.booking.com/hotel/us/i-street-capsule-hostel.en-gb.html"
}

async def scrape_hostel(name, url):
    print(f"\n🔎 Scraping {name}: {url}")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url, timeout=60000)
        await page.wait_for_selector("#hprt-table", timeout=10000)
        html = await page.content()
        await browser.close()

    soup = BeautifulSoup(html, "html.parser")
    rows = soup.select("table#hprt-table > tbody > tr")
    print(f"Found {len(rows)} room rows")

    dorm_beds_total = 0
    dorm_bed_prices = []
    private_rooms_total = 0
    private_room_prices = []
    scraped_room_details = []

    for row in rows:
        room_name = row.select_one("th.hprt-table-cell").get_text(strip=True)
        if "non-refundable" in row.get_text().lower():
            continue  # skip non-refundable options

        price_span = row.select_one(".hprt-table-cell-price span.prco-valign-middle-helper")
        selector = row.select_one("select.hprt-nos-select")

        if not price_span or not selector:
            continue

        try:
            max_option_value = max(int(opt.get("value")) for opt in selector.select("option") if opt.get("value").isdigit())
        except:
            max_option_value = 0

        price_text = price_span.get_text(strip=True).replace("$", "")
        try:
            price = float(price_text)
        except ValueError:
            price = None

        if "Bed in" in room_name:
            dorm_beds_total += max_option_value
            if price: dorm_bed_prices.append(price)
        else:
            private_rooms_total += max_option_value
            if price: private_room_prices.append(price)

        scraped_room_details.append(f"{room_name} | ${price} | {max_option_value} available")

    # Summary output
    print(f"🛏️ Dorm beds available: {dorm_beds_total}")
    print(f"💸 Avg dorm bed price: ${round(sum(dorm_bed_prices)/len(dorm_bed_prices), 2) if dorm_bed_prices else 'N/A'}")
    print(f"🏠 Private rooms available: {private_rooms_total}")
    print(f"💰 Avg private room price: ${round(sum(private_room_prices)/len(private_room_prices), 2) if private_room_prices else 'N/A'}")

    # Detailed room listing
    print(f"\nScraped at: {datetime.now().isoformat()}")
    for detail in scraped_room_details:
        print(detail)

async def main():
    for name, url in URLS.items():
        try:
            await scrape_hostel(name, url)
        except Exception as e:
            print(f"❌ Error scraping {name}: {e}")

if __name__ == "__main__":
    asyncio.run(main())
