from pathlib import Path
import time
import requests

DATA_RAW = Path("E:/DataScience/Projects/uk-cost-of-living-analysis/data/raw")
DATA_RAW.mkdir(parents=True, exist_ok=True)

FILES = {
    "mm23_consumer_price_indices.csv": "https://www.ons.gov.uk/file?uri=%2Feconomy%2Finflationandpriceindices%2Fdatasets%2Fconsumerpriceindices%2Fcurrent%2Fmm23.csv",
    "emp_average_weekly_earnings.csv": "https://www.ons.gov.uk/file?uri=%2Femploymentandlabourmarket%2Fpeopleinwork%2Fearningsandworkinghours%2Fdatasets%2Faverageweeklyearnings%2Fcurrent%2Femp.csv",
}

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "*/*",
    "Connection": "keep-alive",
}

def download(url: str, out_path: Path, retries: int = 5) -> None:
    tmp_path = out_path.with_suffix(out_path.suffix + ".part")

    for attempt in range(1, retries + 1):
        try:
            print(f"Downloading -> {out_path.name} (attempt {attempt}/{retries})")

            with requests.get(url, headers=HEADERS, stream=True, timeout=60) as r:
                r.raise_for_status()
                with open(tmp_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=1024 * 1024):  # 1MB
                        if chunk:
                            f.write(chunk)

            tmp_path.replace(out_path)
            print(f"Saved: {out_path}")
            return

        except Exception as e:
            print(f"⚠️ Download failed: {e}")

            if tmp_path.exists():
                try:
                    tmp_path.unlink()
                except Exception:
                    pass

            if attempt < retries:
                time.sleep(2 * attempt)
            else:
                raise

def main():
    for name, url in FILES.items():
        out = DATA_RAW / name
        if out.exists():
            print(f"Already exists: {out}")
            continue
        download(url, out)

    print("\nDone. Files in data/raw/:")
    for p in sorted(DATA_RAW.glob("*.csv")):
        print(" -", p.name)

if __name__ == "__main__":
    main()