import cecil

session = cecil.start_session()
print("cecil-sdk patched and usage session started (local-only by default)")

# Run provider SDK calls here, then print a local report:
session.print_report(usd_decimals=8)
session.save_json("cecil_usage_report.json", usd_decimals=8)
session.close()
