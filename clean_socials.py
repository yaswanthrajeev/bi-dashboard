import pandas as pd

# --- 1. Facebook ---
fb = pd.read_csv("data/Facebook.csv")

# Rename columns to standard names


# Convert types
fb["date"] = pd.to_datetime(fb["date"])

fb["platform"] = "Facebook"

# Save cleaned version
fb.to_csv("data/Facebook_clean.csv", index=False)


# --- 2. Google ---
google = pd.read_csv("data/Google.csv")



google["date"] = pd.to_datetime(google["date"])

google["platform"] = "Google"

google.to_csv("data/Google_clean.csv", index=False)


# --- 3. TikTok ---
tt = pd.read_csv("data/TikTok.csv")


tt["date"] = pd.to_datetime(tt["date"])
tt["platform"] = "TikTok"

tt.to_csv("data/TikTok_clean.csv", index=False)

print("✅ Cleaned files saved: Facebook_clean.csv, Google_clean.csv, TikTok_clean.csv")
