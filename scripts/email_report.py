"""
Bluestock MF — B5: Automated Weekly Performance Email Report
---------------------------------------------------------------
Generates a styled HTML weekly performance summary (top gainers/losers,
AUM overview, SIP inflow trend, risk flags) and emails it via SMTP.

USAGE:
    # Generate the HTML report only (no email sent) — good for testing:
    python scripts/email_report.py --dry-run

    # Generate and email:
    python scripts/email_report.py --to investor.relations@bluestock.example

Configure SMTP credentials via environment variables (never hard-code secrets):
    setx BLUESTOCK_SMTP_HOST   "smtp.gmail.com"
    setx BLUESTOCK_SMTP_PORT   "587"
    setx BLUESTOCK_SMTP_USER   "your_email@gmail.com"
    setx BLUESTOCK_SMTP_PASS   "your_app_password"

(For Gmail, use an App Password, not your normal password — see
https://support.google.com/accounts/answer/185833)

Intended to be scheduled weekly alongside B1's Task Scheduler job.
"""
import argparse
import os
import smtplib
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

import pandas as pd

DATA_DIR = Path("../data/raw")
OUTPUT_HTML = Path("weekly_report.html")

NAVY = "#1E3A5F"
BLUE = "#00B4D8"
LIGHT_BG = "#F7FAFC"
GREEN = "#1E7A4A"
RED = "#9B2C2C"


def load_data(data_dir: Path = DATA_DIR):
    fund_master = pd.read_csv(data_dir / "01_fund_master.csv")
    nav_history = pd.read_csv(data_dir / "02_nav_history.csv", parse_dates=["date"])
    scheme_perf = pd.read_csv(data_dir / "07_scheme_performance.csv")
    transactions = pd.read_csv(data_dir / "08_investor_transactions.csv", parse_dates=["transaction_date"])
    return fund_master, nav_history, scheme_perf, transactions


def compute_weekly_movers(nav_history: pd.DataFrame, fund_master: pd.DataFrame, n=5):
    """Top gainers/losers over the most recent 7 available days of NAV data."""
    nav_history = nav_history.sort_values(["amfi_code", "date"])
    latest_date = nav_history["date"].max()
    week_ago = latest_date - timedelta(days=7)

    recent = nav_history[nav_history["date"] >= week_ago]
    movers = []
    for code, grp in recent.groupby("amfi_code"):
        grp = grp.sort_values("date")
        if len(grp) < 2:
            continue
        pct_change = (grp["nav"].iloc[-1] / grp["nav"].iloc[0] - 1) * 100
        movers.append({"amfi_code": code, "week_change_pct": pct_change})

    movers_df = pd.DataFrame(movers)
    names = fund_master.set_index("amfi_code")["scheme_name"]
    movers_df["scheme_name"] = movers_df["amfi_code"].map(names)

    gainers = movers_df.sort_values("week_change_pct", ascending=False).head(n)
    losers = movers_df.sort_values("week_change_pct", ascending=True).head(n)
    return gainers, losers, latest_date, week_ago


def compute_sip_inflows(transactions: pd.DataFrame, weeks=4):
    sip = transactions[transactions["transaction_type"] == "SIP"].copy()
    latest = sip["transaction_date"].max()
    cutoff = latest - timedelta(weeks=weeks)
    recent = sip[sip["transaction_date"] >= cutoff]
    weekly = recent.set_index("transaction_date").resample("W")["amount_inr"].sum()
    return weekly


def compute_risk_flags(scheme_perf: pd.DataFrame, fund_master: pd.DataFrame, n=5):
    names = fund_master.set_index("amfi_code")["scheme_name"]
    risky = scheme_perf.sort_values("std_dev_ann_pct", ascending=False).head(n).copy()
    risky["scheme_name"] = risky["amfi_code"].map(names)
    return risky[["scheme_name", "risk_grade", "std_dev_ann_pct", "sharpe_ratio"]]


def row_html(cells, color=NAVY):
    tds = "".join(f'<td style="padding:8px 12px;color:{color};">{c}</td>' for c in cells)
    return f"<tr>{tds}</tr>"


def build_html_report(gainers, losers, sip_weekly, risk_flags, latest_date, week_ago):
    report_date = latest_date.strftime("%d %b %Y")
    period = f"{week_ago.strftime('%d %b')} – {latest_date.strftime('%d %b %Y')}"

    gainer_rows = "".join(
        row_html([r.scheme_name[:40], f"+{r.week_change_pct:.2f}%"], color=GREEN)
        for r in gainers.itertuples()
    )
    loser_rows = "".join(
        row_html([r.scheme_name[:40], f"{r.week_change_pct:.2f}%"], color=RED)
        for r in losers.itertuples()
    )
    sip_rows = "".join(
        row_html([d.strftime("%d %b %Y"), f"₹{v:,.0f}"])
        for d, v in sip_weekly.items()
    )
    risk_rows = "".join(
        row_html([r.scheme_name[:40], r.risk_grade, f"{r.std_dev_ann_pct:.1f}%", f"{r.sharpe_ratio:.2f}"])
        for r in risk_flags.itertuples()
    )

    html = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="margin:0;padding:0;background-color:{LIGHT_BG};font-family:Calibri,Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background-color:{LIGHT_BG};padding:24px 0;">
    <tr><td align="center">
      <table width="640" cellpadding="0" cellspacing="0" style="background-color:#ffffff;border-radius:10px;overflow:hidden;">

        <tr><td style="background-color:{NAVY};padding:28px 32px;">
          <div style="color:{BLUE};font-size:14px;font-weight:bold;letter-spacing:2px;">BLUESTOCK</div>
          <div style="color:#ffffff;font-size:22px;font-weight:bold;margin-top:6px;">Weekly Performance Summary</div>
          <div style="color:#CFE8F3;font-size:13px;margin-top:4px;">{period}</div>
        </td></tr>

        <tr><td style="padding:28px 32px 8px 32px;">
          <div style="color:{NAVY};font-size:16px;font-weight:bold;margin-bottom:10px;">📈 Top 5 Gainers (7-day)</div>
          <table width="100%" cellpadding="0" cellspacing="0" style="font-size:13px;">
            {gainer_rows}
          </table>
        </td></tr>

        <tr><td style="padding:20px 32px 8px 32px;">
          <div style="color:{NAVY};font-size:16px;font-weight:bold;margin-bottom:10px;">📉 Top 5 Losers (7-day)</div>
          <table width="100%" cellpadding="0" cellspacing="0" style="font-size:13px;">
            {loser_rows}
          </table>
        </td></tr>

        <tr><td style="padding:20px 32px 8px 32px;">
          <div style="color:{NAVY};font-size:16px;font-weight:bold;margin-bottom:10px;">💰 SIP Inflows (last 4 weeks)</div>
          <table width="100%" cellpadding="0" cellspacing="0" style="font-size:13px;">
            {sip_rows}
          </table>
        </td></tr>

        <tr><td style="padding:20px 32px 28px 32px;">
          <div style="color:{NAVY};font-size:16px;font-weight:bold;margin-bottom:10px;">⚠️ Highest Volatility Schemes</div>
          <table width="100%" cellpadding="0" cellspacing="0" style="font-size:13px;">
            <tr style="color:#5B6B79;font-weight:bold;">
              <td style="padding:8px 12px;">Scheme</td>
              <td style="padding:8px 12px;">Risk Grade</td>
              <td style="padding:8px 12px;">Std Dev</td>
              <td style="padding:8px 12px;">Sharpe</td>
            </tr>
            {risk_rows}
          </table>
        </td></tr>

        <tr><td style="background-color:{LIGHT_BG};padding:16px 32px;text-align:center;">
          <div style="color:#5B6B79;font-size:11px;">
            Generated automatically by Bluestock MF Analytics · {report_date}<br/>
            This is an automated report. Data reflects available NAV/transaction history in the current dataset.
          </div>
        </td></tr>

      </table>
    </td></tr>
  </table>
</body>
</html>"""
    return html


def send_email(html_content: str, to_address: str, subject: str):
    host = os.environ.get("BLUESTOCK_SMTP_HOST")
    port = int(os.environ.get("BLUESTOCK_SMTP_PORT", "587"))
    user = os.environ.get("BLUESTOCK_SMTP_USER")
    password = os.environ.get("BLUESTOCK_SMTP_PASS")

    if not all([host, user, password]):
        raise EnvironmentError(
            "Missing SMTP configuration. Set BLUESTOCK_SMTP_HOST, BLUESTOCK_SMTP_USER, "
            "and BLUESTOCK_SMTP_PASS as environment variables before sending."
        )

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = user
    msg["To"] = to_address
    msg.attach(MIMEText(html_content, "html"))

    with smtplib.SMTP(host, port) as server:
        server.starttls()
        server.login(user, password)
        server.sendmail(user, to_address, msg.as_string())

    print(f"Report emailed to {to_address}")


def main():
    parser = argparse.ArgumentParser(description="Generate and optionally email the weekly Bluestock MF report.")
    parser.add_argument("--to", type=str, default=None, help="Recipient email address")
    parser.add_argument("--dry-run", action="store_true", help="Only generate the HTML file, don't send email")
    args = parser.parse_args()

    fund_master, nav_history, scheme_perf, transactions = load_data()
    gainers, losers, latest_date, week_ago = compute_weekly_movers(nav_history, fund_master)
    sip_weekly = compute_sip_inflows(transactions)
    risk_flags = compute_risk_flags(scheme_perf, fund_master)

    html = build_html_report(gainers, losers, sip_weekly, risk_flags, latest_date, week_ago)
    OUTPUT_HTML.write_text(html, encoding="utf-8")
    print(f"Report written to {OUTPUT_HTML.resolve()}")

    if args.dry_run or not args.to:
        print("Dry run — no email sent. Open weekly_report.html in a browser to preview.")
        return

    subject = f"Bluestock MF — Weekly Performance Summary ({latest_date.strftime('%d %b %Y')})"
    send_email(html, args.to, subject)


if __name__ == "__main__":
    main()
