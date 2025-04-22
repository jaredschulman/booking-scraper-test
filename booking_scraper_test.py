from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from datetime import datetime

print("📄 Booking.com Scraper Version: v1.0.1")

HOSTELS = [
    {
        "name": "Generator DC",
        "url": "https://www.booking.com/hotel/us/generator-washington-dc.en-gb.html"
    },
    {
        "name": "I Street Capsule Hostel",
        "url": "https://www.booking.com/hotel/us/i-street-capsule-hostel.en-gb.html"
    }
]

def parse_booking_html(html):
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table", {"id": "hprt-table"})
    if not table:
        return [], []

    rows = table.find_all("tr", class_="hprt-table-cheapest-block")
    dorm_beds = 0
    private_rooms = 0
    dorm_prices = []
    private_prices = []
    detailed_output = []

    for row in rows:
        room_name_el = row.find("span", class_="hprt-roomtype-icon-link")
        if not room_name_el:
            continue
        room_name = room_name_el.text.strip()

        # Check for refundable options only
        cancellation_policy = row.find("li", class_="e2e-cancellation")
        if not cancellation_policy or "Free cancellation" not in cancellation_policy.text:
            continue

        # Get price
        price_el = row.find("div", class_="bui-price-display__value")
        if not price_el:
            continue
        price_text = price_el.text.strip().replace("$", "").replace(",", "")
        try:
            price = float(price_text)
        except:
            continue

        # Get max selector value
        select_el = row.find("select")
        if not select_el:
            continue
        option_values = [int(opt["value"]) for opt in select_el.find_all("option") if opt["value"].isdigit()]
        quantity = max(option_values) if option_values else 0

        if "Bed in" in room_name:
            dorm_beds += quantity
            dorm_prices.extend([price] * quantity)
        else:
            private_rooms += quantity
            private_prices.extend([price] * quantity)

        detailed_output.append(f"{room_name} | ${price:.2f} | {quantity} available")

    return {
        "dorm_beds": dorm_beds,
        "dorm_prices": dorm_prices,
        "private_rooms": private_rooms,
        "private_prices": private_prices,
        "detailed": detailed_output
    }

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context()

    for hostel in HOSTELS:
        print(f"🔎 Scraping {hostel['name']}: {hostel['url']}")
        try:
            with context.new_page() as page:
                page.goto(hostel["url"], timeout=30000)
                page.wait_for_selector("#hprt-table", timeout=10000)
                html = page.content()
                result = parse_booking_html(html)

                print(f"📆 Scraped at: {datetime.now().isoformat()}")
                for line in result["detailed"]:
                    print(line)

                avg_dorm = round(sum(result["dorm_prices"]) / len(result["dorm_prices"]), 2) if result["dorm_prices"] else 0
                avg_private = round(sum(result["private_prices"]) / len(result["private_prices"]), 2) if result["private_prices"] else 0

                print(f"🛏️ Dorm beds available: {result['dorm_beds']}")
                print(f"💸 Avg dorm bed price: ${avg_dorm}")
                print(f"🏠 Private rooms available: {result['private_rooms']}")
                print(f"💰 Avg private room price: ${avg_private}")
                print("—" * 60)

        except Exception as e:
            print(f"❌ Error scraping {hostel['name']}: {e}")

    browser.close()
