from bs4 import BeautifulSoup
from datetime import datetime

# ----- LOAD HTML -----
# Replace this with actual HTML loading logic (e.g., Playwright, requests)
with open("sample_bookingcom_page.html", "r", encoding="utf-8") as f:
    html = f.read()

# ----- PARSE HTML -----
soup = BeautifulSoup(html, "html.parser")
rows = soup.select("tr.js-rt-block-row")
print(f"Found {len(rows)} room rows\n")

# ----- DATA HOLDERS -----
dorm_beds = 0
dorm_prices = []
private_rooms = 0
private_prices = []
detailed_lines = []

# ----- PARSE EACH ROOM ROW -----
for row in rows:
    name_tag = row.select_one("span.hprt-roomtype-icon-link")
    price_tag = row.select_one("div.bui-price-display__value")
    select_tag = row.select_one("select.js-hprt-nos-select")
    cancellation = row.select_one("li.e2e-cancellation")

    # Skip incomplete rows
    if not (name_tag and price_tag and select_tag and cancellation):
        continue

    room_name = name_tag.get_text(strip=True)
    price_str = price_tag.get_text(strip=True).replace("$", "").replace(",", "")
    try:
        price = float(price_str)
    except ValueError:
        continue

    is_dorm = "Bed in" in room_name
    is_free_cancel = "Free cancellation" in cancellation.get_text()

    # Skip non-refundable rooms
    if not is_free_cancel:
        continue

    # Extract max selectable value (available quantity)
    options = select_tag.find_all("option")
    available = max([int(opt["value"]) for opt in options if opt.has_attr("value") and opt["value"].isdigit()], default=0)

    # Add to summary stats
    if is_dorm:
        dorm_beds += available
        dorm_prices.extend([price] * available)
    else:
        private_rooms += available
        private_prices.extend([price] * available)

    # Add to detailed log
    detailed_lines.append(f"{room_name} | ${price:.2f} | {available} available")

# ----- SUMMARY OUTPUT -----
print("🛏️ Dorm beds available:", dorm_beds)
print("💸 Avg dorm bed price:", f"${sum(dorm_prices)/len(dorm_prices):.2f}" if dorm_prices else "N/A")
print("🏠 Private rooms available:", private_rooms)
print("💰 Avg private room price:", f"${sum(private_prices)/len(private_prices):.2f}" if private_prices else "N/A")
print()

# ----- DETAILED OUTPUT -----
print("Scraped at:", datetime.now().isoformat())
for line in detailed_lines:
    print(line)
